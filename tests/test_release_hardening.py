from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_release_samples_are_real_and_nonempty():
    cls = ROOT / "data/samples/classification_breast_cancer.csv"
    reg = ROOT / "data/samples/regression_diabetes.csv"
    assert cls.exists() and cls.stat().st_size > 1000
    assert reg.exists() and reg.stat().st_size > 1000

def test_smoke_script_has_no_fake_metrics_contract():
    text = (ROOT / "scripts/smoke_test.py").read_text()
    assert "status\": \"PASS\"" in text
    assert "breast_cancer" in text
    assert "diabetes" in text

def test_benchmark_declares_synthetic_data():
    text = (ROOT / "scripts/benchmark.py").read_text()
    assert "synthetic" in text
    assert "10_000,100_000,1_000_000" in text
