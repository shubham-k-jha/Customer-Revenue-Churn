"""Validate a release tree contains only intended source artifacts."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}

def cleanup() -> None:
    for name in FORBIDDEN_DIRS:
        for p in ROOT.rglob(name):
            if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in FORBIDDEN_SUFFIXES: p.unlink(missing_ok=True)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main() -> int:
    cleanup()
    subprocess.run([sys.executable,"-m","compileall","-q","src","api","app","scripts"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,"-m","pytest","-q","--disable-warnings"],cwd=ROOT,check=True)
    cleanup()
    errors=[]
    for p in ROOT.rglob("*"):
        if any(part in FORBIDDEN_DIRS for part in p.parts) or (p.is_file() and p.suffix in FORBIDDEN_SUFFIXES):
            errors.append(f"forbidden artifact: {p.relative_to(ROOT)}")
    lock=ROOT/"uv.lock"
    manifest={"version":_version(),"files":sum(1 for p in ROOT.rglob("*") if p.is_file()),"lock_sha256":sha256(lock) if lock.exists() else None,"dependency_lock_status":"present" if lock.exists() else "not-generated-in-offline-audit-environment"}
    (ROOT/"reports"/"release_validation.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if errors: print("\n".join(errors)); return 1
    print(json.dumps(manifest,indent=2)); return 0

def _version():
    import tomllib
    return tomllib.loads((ROOT/"pyproject.toml").read_text())["project"]["version"]
if __name__=="__main__": raise SystemExit(main())
