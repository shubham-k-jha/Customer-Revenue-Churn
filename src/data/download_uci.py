from pathlib import Path
import hashlib
import requests
from src.config import ROOT

RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
URL = 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'
OUT = RAW / 'online_retail_ii.zip'
SHA256 = None  # UCI page currently exposes the file and DOI; verify after download if a release digest is supplied.

def download(url: str = URL, out: Path = OUT) -> Path:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    out.write_bytes(r.content)
    return out

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

if __name__ == '__main__':
    p = download()
    print(f'{p} {p.stat().st_size:,} bytes sha256={sha256(p)}')
