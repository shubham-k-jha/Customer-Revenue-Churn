from dataclasses import asdict,dataclass
import re,pandas as pd
TARGET_HINTS={'target','label','class','outcome','response','y','churn','default','fraud','converted','conversion','clicked','purchase','sales','revenue'}
ID_HINTS={'id','uuid','guid','customerid','userid','accountid','orderid','invoiceid'}
DATE_HINTS={'date','time','timestamp','datetime','created','updated','dob'}
PII_HINTS={'email','phone','mobile','address','ssn','socialsecurity','passport','iban','accountnumber'}
@dataclass
class ColumnProfile:
 name:str;dtype:str;rows:int;missing:int;missing_pct:float;unique:int;unique_pct:float;likely_id:bool;likely_date:bool;likely_target:bool;possible_pii:bool;sample_values:list[str]
def _norm(name):return re.sub(r'[^a-z0-9]','',str(name).lower())
def _likely_id(name,s):
 n=_norm(name); u=s.nunique(dropna=True); ratio=u/max(len(s),1)
 if any(h in n for h in ID_HINTS): return True
 if len(s)>20 and ratio>.98: return True
 if len(s)>20 and ratio>.90 and pd.api.types.is_numeric_dtype(s):
  x=pd.to_numeric(s,errors='coerce').dropna().to_numpy()
  if len(x)>20:
   diffs=x[1:]-x[:-1]
   if len(diffs) and ((diffs==1).mean()>.95 or (diffs==-1).mean()>.95): return True
 return False
def _likely_date(name,s):
 n=_norm(name)
 if any(h in n for h in DATE_HINTS) or pd.api.types.is_datetime64_any_dtype(s):return True
 if s.dtype=='object':
  sample=s.dropna().astype(str).head(200)
  if sample.empty or not sample.str.contains(r'[-/:]',regex=True).mean()>=.50:return False
  return pd.to_datetime(sample,errors='coerce',utc=True,format='mixed').notna().mean()>=.90
 return False
def _likely_target(name,s):
 n=_norm(name)
 if n in TARGET_HINTS or any(h in n for h in TARGET_HINTS if len(h)>=4 and h in n):return True
 return s.nunique(dropna=True)==2 and not _likely_id(name,s)
def _possible_pii(name,s):
 n=_norm(name)
 if any(h in n for h in PII_HINTS):return True
 if s.dtype=='object':
  sample=s.dropna().astype(str).head(200)
  if not sample.empty and (sample.str.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').mean()>.8):return True
 return False
def profile_dataframe(df):
 if df.empty:raise ValueError('Dataset is empty')
 if df.columns.duplicated().any():raise ValueError(f'Duplicate column names: {df.columns[df.columns.duplicated()].tolist()}')
 profiles=[]
 for c in df.columns:
  s=df[c]; profiles.append(asdict(ColumnProfile(str(c),str(s.dtype),len(df),int(s.isna().sum()),float(s.isna().mean()),int(s.nunique(dropna=True)),float(s.nunique(dropna=True)/len(df)),_likely_id(c,s),_likely_date(c,s),_likely_target(c,s),_possible_pii(c,s),[str(x)[:80] for x in s.dropna().head(5)])))
 return {'rows':len(df),'columns':len(df.columns),'memory_mb':float(df.memory_usage(deep=True).sum()/1024**2),'duplicate_rows':int(df.duplicated().sum()),'pii_columns':[p['name'] for p in profiles if p['possible_pii']],'profiles':profiles}
def rank_target_candidates(df):
 rows=[]
 for c in df.columns:
  s=df[c]
  if _likely_id(c,s) or _likely_date(c,s):continue
  n=_norm(c);score=100 if n in TARGET_HINTS else (50 if any(h in n for h in TARGET_HINTS if len(h)>=4) else 0);u=s.nunique(dropna=True)
  if u==2:score+=30
  elif 2<=u<=min(20,max(2,int(len(df)*.05))):score+=10
  rows.append({'column':str(c),'score':score,'unique':int(u),'dtype':str(s.dtype)})
 return sorted(rows,key=lambda x:(-x['score'],x['column']))
