#!/usr/bin/env python3
"""Fetch public URLs from a request file; write results encrypted to pubkey.pem.

Request: {"id": "...", "urls": [...], "mode": "http" | "chrome", "delay": seconds}
Output dir gets <id>.tgz.enc (AES-256-CBC, PBKDF2), <id>.key.enc (RSA-OAEP-SHA256)
and <id>.status.json (status codes only, no page content).
"""
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zlib

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
MAX_BYTES = 15 * 1024 * 1024
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}


def decode_body(body, encoding):
    try:
        if encoding == "gzip":
            return gzip.decompress(body)
        if encoding == "deflate":
            return zlib.decompress(body)
    except Exception:
        pass
    return body


def fetch_http(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read(MAX_BYTES + 1)
            meta = {"status": resp.status, "final_url": resp.geturl(),
                    "content_type": resp.headers.get("Content-Type", "")}
            enc = resp.headers.get("Content-Encoding", "")
    except urllib.error.HTTPError as e:
        body = e.read(MAX_BYTES + 1) if e.fp else b""
        meta = {"status": e.code, "final_url": url,
                "content_type": e.headers.get("Content-Type", "") if e.headers else ""}
        enc = e.headers.get("Content-Encoding", "") if e.headers else ""
    body = decode_body(body, enc)
    meta["truncated"] = len(body) > MAX_BYTES
    return meta, body[:MAX_BYTES]


def fetch_chrome(url):
    cmd = ["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
           "--disable-dev-shm-usage", f"--user-agent={UA}",
           "--virtual-time-budget=15000", "--dump-dom", url]
    p = subprocess.run(cmd, capture_output=True, timeout=150)
    ok = p.returncode == 0 and bool(p.stdout.strip())
    meta = {"status": 200 if ok else None, "final_url": url,
            "content_type": "text/html; dumped-dom", "chrome_returncode": p.returncode,
            "truncated": len(p.stdout) > MAX_BYTES}
    if not ok:
        meta["chrome_stderr_tail"] = p.stderr.decode(errors="replace")[-300:]
    return meta, p.stdout[:MAX_BYTES]


def main(request_path, out_dir):
    spec = json.loads(pathlib.Path(request_path).read_text())
    rid, mode, delay = spec["id"], spec.get("mode", "http"), float(spec.get("delay", 1.0))
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        payload = tmp / rid
        payload.mkdir()
        index = []
        for i, url in enumerate(spec["urls"]):
            started = time.time()
            try:
                meta, body = (fetch_chrome if mode == "chrome" else fetch_http)(url)
                meta["error"] = None
            except Exception as exc:  # record every failure; never retry silently
                meta, body = {"status": None, "final_url": url, "content_type": "",
                              "error": f"{type(exc).__name__}: {exc}"[:300]}, b""
            meta.update({"index": i, "url": url, "mode": mode,
                         "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         "seconds": round(time.time() - started, 2), "bytes": len(body),
                         "sha256": hashlib.sha256(body).hexdigest()})
            (payload / f"{i:03d}.body").write_bytes(body)
            index.append(meta)
            print(f"[{i:03d}] status={meta['status']} bytes={meta['bytes']} "
                  f"error={(meta['error'] or '')[:80]}")
            time.sleep(delay)
        (payload / "index.json").write_text(json.dumps(index, indent=1))
        archive = tmp / "payload.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(payload, arcname=rid)
        keyfile = tmp / "key"
        keyfile.write_text(os.urandom(32).hex())
        subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt",
                        "-in", str(archive), "-out", str(out / f"{rid}.tgz.enc"),
                        "-pass", f"file:{keyfile}"], check=True)
        subprocess.run(["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", "pubkey.pem",
                        "-pkeyopt", "rsa_padding_mode:oaep", "-pkeyopt", "rsa_oaep_md:sha256",
                        "-in", str(keyfile), "-out", str(out / f"{rid}.key.enc")], check=True)
    status = [{"index": m["index"], "status": m["status"], "bytes": m["bytes"],
               "error": (m["error"] or "")[:200]} for m in index]
    (out / f"{rid}.status.json").write_text(json.dumps(status, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
