"""Transactional preflight reservations for optional external calls.

Cannot enforce provider-side billing; caller must reserve BEFORE dispatch and
settle only after use. All amounts are declared estimated USD, not invoices.
"""
import sqlite3
from decimal import Decimal
from pathlib import Path
from contextlib import contextmanager
from .io import AtlasError, now
from .quant import nonnegative

class Budget:
    def __init__(self,path,limit):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.limit=nonnegative(limit)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS reservations (
                key TEXT PRIMARY KEY, estimated TEXT NOT NULL, actual TEXT,
                status TEXT NOT NULL, authorized_at TEXT NOT NULL, provider TEXT NOT NULL)''')
            db.execute('CREATE TABLE IF NOT EXISTS authorization (id INTEGER PRIMARY KEY CHECK(id=1), ceiling TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO authorization VALUES (1,?)',(str(self.limit),))
            if nonnegative(db.execute('SELECT ceiling FROM authorization WHERE id=1').fetchone()[0])!=self.limit:
                raise AtlasError('Budget limit differs from the persisted authorization; use an explicit authorized amendment')
    @contextmanager
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        try:
            db.execute('PRAGMA busy_timeout=10000')
            yield db
        finally:
            if db.in_transaction: db.rollback()
            db.close()
    def _totals(self,db):
        self.limit=nonnegative(db.execute('SELECT ceiling FROM authorization WHERE id=1').fetchone()[0])
        committed=Decimal('0'); reserved=Decimal('0')
        for est,actual,status in db.execute('SELECT estimated,actual,status FROM reservations'):
            if status=='settled': committed+=nonnegative(actual)
            elif status=='reserved': reserved+=nonnegative(est)
            elif status!='canceled': raise AtlasError('Corrupt budget reservation status')
        return committed,reserved
    def reserve(self,key,estimated,provider,authorized=False):
        amount=nonnegative(estimated)
        if not authorized: raise AtlasError('Explicit paid-tool authorization required')
        if any(not isinstance(v,str) or not v.strip() for v in (key,provider)): raise AtlasError('Reservation key/provider required')
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT estimated,provider,status FROM reservations WHERE key=?',(key,)).fetchone()
            if existing:
                if nonnegative(existing[0])!=amount or existing[1]!=provider: raise AtlasError('Idempotency-key conflict')
                db.execute('COMMIT'); return {'key':key,'status':existing[2],'idempotent':True,'dispatch_allowed':False}
            committed,reserved=self._totals(db)
            if amount+committed+reserved>self.limit: raise AtlasError('Estimated call exceeds remaining authorization')
            db.execute('INSERT INTO reservations VALUES (?,?,?,?,?,?)',(key,str(amount),None,'reserved',now(),provider))
            db.execute('COMMIT')
        return {'key':key,'status':'reserved','estimated_usd':str(amount),'dispatch_allowed':True}
    def settle(self,key,actual):
        amount=nonnegative(actual)
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT estimated,actual,status FROM reservations WHERE key=?',(key,)).fetchone()
            if not row: raise AtlasError('Unknown reservation')
            if row[2]=='settled':
                if nonnegative(row[1])!=amount: raise AtlasError('Settlement conflict')
            elif row[2]!='reserved': raise AtlasError('Cannot settle canceled reservation')
            else:
                db.execute('UPDATE reservations SET actual=?,status=? WHERE key=?',(str(amount),'settled',key))
            db.execute('COMMIT')
        return self.status()
    def cancel(self,key):
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT status FROM reservations WHERE key=?',(key,)).fetchone()
            if not row or row[0]!='reserved': raise AtlasError('Only active reservations can be canceled')
            db.execute('UPDATE reservations SET status=? WHERE key=?',('canceled',key)); db.execute('COMMIT')
        return self.status()
    def status(self):
        with self._connect() as db: committed,reserved=self._totals(db)
        return {'ok':committed+reserved<=self.limit,'budget_usd':str(self.limit),'settled_usd':str(committed),'reserved_usd':str(reserved),
                'remaining_usd':str(self.limit-committed-reserved),
                'action':'halt new provider work; recorded actual cost exceeded authorization' if committed+reserved>self.limit else 'within declared authorization',
                'limit':'local call authorization only; provider-side spending must also be controlled'}

    def amend_limit(self,amount,authorized=False):
        amount=nonnegative(amount)
        if not authorized: raise AtlasError('Explicit authorization required to amend a budget')
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            committed,reserved=self._totals(db)
            if amount<committed+reserved: raise AtlasError('New ceiling cannot conceal already committed or reserved cost')
            db.execute('UPDATE authorization SET ceiling=? WHERE id=1',(str(amount),))
            db.execute('COMMIT')
        self.limit=amount
        return self.status()
