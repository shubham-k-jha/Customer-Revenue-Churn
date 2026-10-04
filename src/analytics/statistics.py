from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats

def compare_numeric_by_binary(df,column,target):
    a=pd.to_numeric(df.loc[df[target].astype(str).str.lower().isin(['1','yes','true']),column],errors='coerce').dropna()
    b=pd.to_numeric(df.loc[~df[target].astype(str).str.lower().isin(['1','yes','true']),column],errors='coerce').dropna()
    if len(a)<2 or len(b)<2: raise ValueError('Each group needs at least two observations')
    result=stats.mannwhitneyu(a,b,alternative='two-sided')
    return {'test':'Mann-Whitney U','column':column,'group_a_n':len(a),'group_b_n':len(b),'p_value':float(result.pvalue),'effect_median_difference':float(a.median()-b.median())}

def chi_square(df,a,b):
    table=pd.crosstab(df[a],df[b]); chi,p,dof,_=stats.chi2_contingency(table)
    return {'test':'Chi-square','a':a,'b':b,'chi2':float(chi),'p_value':float(p),'dof':int(dof)}
