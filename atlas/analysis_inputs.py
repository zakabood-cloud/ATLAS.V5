"""Financial-model input provenance, no automatic confidence inflation."""
import re
from .io import AtlasError


def validate_inputs(spec):
    if not isinstance(spec,dict) or not isinstance(spec.get('inputs'),list) or not spec['inputs']:
        raise AtlasError('Model input records required')
    errors=[]; ids=set()
    for row in spec['inputs']:
        if not isinstance(row,dict): raise AtlasError('Each model input must be a record')
        identifier=row.get('name')
        if not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,79}',identifier):
            raise AtlasError('Invalid model input name')
        if identifier in ids: raise AtlasError('Duplicate input name')
        ids.add(identifier)
        if row.get('basis') not in {'observed','derived','estimate','assumption'}:errors.append([identifier,'basis'])
        if row.get('value') is None or isinstance(row['value'],bool): errors.append([identifier,'value'])
        if not isinstance(row.get('unit'),str) or not row['unit'].strip(): errors.append([identifier,'unit'])
        if not isinstance(row.get('time_period'),str) or not row['time_period'].strip(): errors.append([identifier,'time_period'])
        if row.get('basis') in {'observed','derived'}:
            if not row.get('source_id') or not row.get('source_snapshot_sha256'):errors.append([identifier,'source'])
        if row.get('basis') in {'estimate','assumption'} and not row.get('uncertainty'):
            errors.append([identifier,'uncertainty'])
    return {'ok':not errors,'errors':errors,'inputs':len(ids),
            'qualification':'Input provenance is declared, not externally authenticated; calculations need independent verification.'}
