from __future__ import annotations
import pandas as pd, numpy as np
from dataclasses import dataclass, asdict

@dataclass
class QualityIssue:
    severity: str
    rule: str
    column: str | None
    message: str

class DataQualityEngine:
    def __init__(self, null_warn=.30, duplicate_warn=.05): self.null_warn=null_warn; self.duplicate_warn=duplicate_warn
    def run(self, df, target=None, date_column=None):
        if not isinstance(df, pd.DataFrame): raise TypeError('df must be a pandas DataFrame')
        if df.empty:
            return {'status':'fail','rows':0,'columns':len(df.columns),'duplicate_rate':0.0,'issues':[asdict(QualityIssue('critical','empty_dataset',None,'dataset contains no rows'))]}
        issues=[]
        dup=float(df.duplicated().mean())
        if dup>self.duplicate_warn: issues.append(QualityIssue('warning','duplicates',None,f'{dup:.1%} duplicate rows'))
        for c in df.columns:
            null=float(df[c].isna().mean())
            if null>=self.null_warn: issues.append(QualityIssue('warning','missingness',c,f'{null:.1%} missing'))
            if df[c].nunique(dropna=False)<=1: issues.append(QualityIssue('warning','constant',c,'constant column'))
        if date_column and date_column in df:
            parsed=pd.to_datetime(df[date_column],errors='coerce',format='mixed',utc=True)
            if parsed.notna().mean()<.90: issues.append(QualityIssue('critical','date_parse',date_column,'<90% values parse as dates'))
            elif parsed.max()>pd.Timestamp.now(tz='UTC')+pd.Timedelta(days=1): issues.append(QualityIssue('warning','future_dates',date_column,'contains future dates'))
        if target and target in df:
            if df[target].nunique(dropna=True)<2: issues.append(QualityIssue('critical','target_variance',target,'target has fewer than two observed values'))
        return {'status':'fail' if any(x.severity=='critical' for x in issues) else ('warn' if issues else 'pass'),'rows':len(df),'columns':len(df.columns),'duplicate_rate':dup,'issues':[asdict(x) for x in issues]}
