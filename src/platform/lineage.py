from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform, subprocess, sys

def sha256_file(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def git_commit(root='.'):
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return None

def create_run_metadata(dataset_path=None, root='.'):
    p=Path(dataset_path) if dataset_path else None
    return {'run_timestamp':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],'platform':platform.platform(),'git_commit':git_commit(root),'dataset':str(p) if p else None,'dataset_sha256':sha256_file(p) if p and p.exists() else None}

def write_run(path, metadata):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(metadata,indent=2,default=str)); return p
