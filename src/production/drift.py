import pandas as pd
from src.monitoring.metrics import population_stability_index

def numeric_drift(reference_csv, current_csv, columns):
    ref=pd.read_csv(reference_csv); cur=pd.read_csv(current_csv); return {c:population_stability_index(ref[c].dropna(),cur[c].dropna()) for c in columns if c in ref and c in cur}
