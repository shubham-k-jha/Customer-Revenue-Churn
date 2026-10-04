"""Repeatable profiling benchmark. Synthetic data is used only for scalability testing."""
from __future__ import annotations
import argparse, json, time, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np, pandas as pd
from src.universal.profile import profile_dataframe

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--rows", type=int, nargs="+", default=[10_000,100_000,1_000_000]); ap.add_argument("--seed",type=int,default=42); ap.add_argument("--output",default="reports/benchmarks/latest.json"); a=ap.parse_args()
    rng=np.random.default_rng(a.seed); results=[]
    for n in a.rows:
        df=pd.DataFrame({"customer_id":np.arange(n,dtype=np.int64),"segment":rng.choice(["A","B","C","D"],n),"revenue":rng.gamma(2.0,100.0,n),"orders":rng.poisson(4,n).astype(np.int16),"event_date":pd.date_range("2020-01-01",periods=n,freq="min")})
        t=time.perf_counter(); prof=profile_dataframe(df); elapsed=time.perf_counter()-t
        results.append({"rows":n,"columns":df.shape[1],"seconds":round(elapsed,4),"rows_per_second":round(n/elapsed,1),"quality_score":prof.get("quality_score")})
    p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps({"seed":a.seed,"synthetic":True,"results":results},indent=2)+"\n"); print(json.dumps(results,indent=2))
if __name__ == "__main__": main()
