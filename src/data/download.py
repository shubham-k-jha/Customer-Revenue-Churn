from pathlib import Path
import hashlib, requests
from src.config import DATA_URL, RAW
OUT=RAW/'telco_customer_churn.csv'
EXPECTED_SHA256='16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91'

def download(url=DATA_URL, out=OUT, verify_hash=True):
    r=requests.get(url,timeout=60); r.raise_for_status(); out.write_bytes(r.content)
    digest=hashlib.sha256(r.content).hexdigest()
    if verify_hash and digest != EXPECTED_SHA256:
        raise ValueError(f'Unexpected dataset hash: {digest}')
    return out,digest

if __name__=='__main__':
    path,digest=download(); print(f'{path}\nSHA256={digest}')
