from __future__ import annotations
import pandas as pd
import numpy as np


def retention_cohort(df, customer_col, date_col, period='M'):
    for c in (customer_col,date_col):
        if c not in df: raise KeyError(c)
    x=df[[customer_col,date_col]].copy(); x[date_col]=pd.to_datetime(x[date_col],errors='coerce',utc=True,format='mixed'); x=x.dropna()
    if x.empty: raise ValueError('No usable cohort rows')
    x['period']=x[date_col].dt.tz_convert(None).dt.to_period(period).dt.to_timestamp().dt.tz_localize('UTC')
    first=x.groupby(customer_col)['period'].min().rename('cohort_period'); x=x.join(first,on=customer_col)
    x['period_number']=((x['period'].dt.year-x['cohort_period'].dt.year)*12+(x['period'].dt.month-x['cohort_period'].dt.month)).astype(int)
    counts=x.drop_duplicates([customer_col,'cohort_period','period_number']).groupby(['cohort_period','period_number'])[customer_col].nunique().unstack(fill_value=0)
    retention=counts.div(counts.iloc[:,0],axis=0)
    return {'counts':counts,'retention':retention}
