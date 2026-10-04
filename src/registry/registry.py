from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
class ModelRegistry:
    """Small local registry with immutable artifact hashes and champion/challenger state."""
    def __init__(self,path='models/registry.json'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.data=json.loads(self.path.read_text()) if self.path.exists() else {'models':[],'champion':None}
    def register(self,artifact_path,metadata,status='challenger'):
        p=Path(artifact_path)
        if not p.exists(): raise FileNotFoundError(p)
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        record={**metadata,'artifact':str(p),'sha256':sha,'status':status,'registered_at':datetime.now(timezone.utc).isoformat()}
        self.data.setdefault('models',[]).append(record); self._save(); return record
    def promote(self,sha256):
        found=False
        for m in self.data['models']:
            if m['sha256']==sha256:
                found=True; m['status']='champion'; self.data['champion']=sha256
            elif m.get('status')=='champion': m['status']='archived'
        if not found: raise KeyError(f'Unknown model hash: {sha256}')
        self._save(); return self.champion()
    def champion(self):
        sha=self.data.get('champion')
        return next((m for m in reversed(self.data['models']) if m['sha256']==sha),None)
    def latest(self): return self.data['models'][-1] if self.data.get('models') else None
    def _save(self): self.path.write_text(json.dumps(self.data,indent=2,default=str))
