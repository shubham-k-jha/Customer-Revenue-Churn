from __future__ import annotations
import pandas as pd

def generate_executive_insights(df:pd.DataFrame, date_col=None, value_col=None, group_col=None):
    if value_col not in df: raise KeyError(value_col)
    x=pd.to_numeric(df[value_col],errors='coerce').dropna()
    if x.empty: raise ValueError('No numeric values available')
    insights=[f'{value_col} has {len(x):,} usable observations with mean {x.mean():,.2f} and median {x.median():,.2f}.']
    if date_col and date_col in df:
        d=pd.to_datetime(df[date_col],errors='coerce',format='mixed').dropna()
        if len(d)>=2: insights.append(f'Data spans {d.min().date()} to {d.max().date()}.')
    if group_col and group_col in df:
        g=df.assign(__v=pd.to_numeric(df[value_col],errors='coerce')).groupby(group_col)['__v'].sum().dropna().sort_values(ascending=False)
        if not g.empty: insights.append(f'Top {group_col} by {value_col} is {g.index[0]!s} with {g.iloc[0]:,.2f}.')
    return {'insights':insights,'caveats':['Descriptive analysis is not causal evidence.','Claims are calculated from the supplied dataset only.']}
