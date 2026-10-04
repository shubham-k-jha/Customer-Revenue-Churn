"""Fast end-to-end smoke test for the released platform."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
import pandas as pd
from sklearn.datasets import load_breast_cancer, load_diabetes

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="crci-smoke-") as td:
        out = Path(td)
        cancer = load_breast_cancer(as_frame=True).frame.copy()
        cancer_path = out / "classification.csv"; cancer.to_csv(cancer_path, index=False)
        diabetes = load_diabetes(as_frame=True).frame.rename(columns={"target": "revenue"})
        regression_path = out / "regression.csv"; diabetes.to_csv(regression_path, index=False)

        run([sys.executable, "-m", "src.universal.cli", "profile", str(cancer_path)])
        run([sys.executable, "-m", "src.universal.cli", "train", str(cancer_path), "--target", "target", "--artifact", str(out / "classification.joblib")])
        run([sys.executable, "-m", "src.universal.cli", "train", str(regression_path), "--target", "revenue", "--task", "regression", "--artifact", str(out / "regression.joblib")])
        from fastapi.testclient import TestClient
        from api.main import app
        client = TestClient(app)
        assert client.get("/health").status_code == 200
        assert client.get("/metrics").status_code == 200
        response = client.post("/data/profile", files={"file": ("classification.csv", cancer_path.read_bytes(), "text/csv")})
        assert response.status_code == 200, response.text
        assert "target_candidates" in response.json()
        sql = client.post("/sql/validate", json={"sql": "SELECT 1"})
        assert sql.status_code == 200, sql.text
        bad = client.post("/sql/validate", json={"sql": "DROP TABLE customers"})
        assert bad.status_code == 400, bad.text
        report = {"status": "PASS", "classification_rows": len(cancer), "regression_rows": len(diabetes)}
        (ROOT / "reports" / "smoke_latest.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
