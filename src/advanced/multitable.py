from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class JoinCandidate:
    left_table: str
    right_table: str
    left_key: str
    right_key: str
    overlap_ratio: float
    left_unique_ratio: float
    right_unique_ratio: float
    relationship: str

def _norm(s: pd.Series) -> pd.Series: return s.dropna().astype(str).str.strip()

def suggest_joins(tables: dict[str, pd.DataFrame], min_overlap: float = .30) -> list[JoinCandidate]:
    if not 0 < min_overlap <= 1: raise ValueError('min_overlap must be in (0,1]')
    out=[]; names=list(tables)
    for i,left_name in enumerate(names):
        for right_name in names[i+1:]:
            left,right=tables[left_name],tables[right_name]
            for lk in left.columns:
                if left[lk].nunique(dropna=True) < 2: continue
                lv=_norm(left[lk]); lset=set(lv)
                if not lset: continue
                for rk in right.columns:
                    if right[rk].nunique(dropna=True) < 2: continue
                    rv=_norm(right[rk]); rset=set(rv)
                    overlap=len(lset & rset)/max(1,min(len(lset),len(rset)))
                    if overlap < min_overlap: continue
                    lu=left[lk].nunique(dropna=True)/max(1,len(left)); ru=right[rk].nunique(dropna=True)/max(1,len(right))
                    rel='one-to-one' if lu>.98 and ru>.98 else ('one-to-many' if lu>.98 else ('many-to-one' if ru>.98 else 'many-to-many'))
                    out.append(JoinCandidate(left_name,right_name,lk,rk,round(overlap,4),round(lu,4),round(ru,4),rel))
    return sorted(out,key=lambda x:(-x.overlap_ratio,-max(x.left_unique_ratio,x.right_unique_ratio)))

def safe_join(left: pd.DataFrame, right: pd.DataFrame, left_key: str, right_key: str, how: str='left', relationship: str|None=None, max_output_rows: int=1_000_000) -> pd.DataFrame:
    if how not in {'left','inner','outer','right'}: raise ValueError('Unsupported join type')
    if left_key not in left or right_key not in right: raise KeyError('Join key missing')
    if max_output_rows < 1: raise ValueError('max_output_rows must be positive')
    if relationship is not None and relationship not in {'one-to-one','one-to-many','many-to-one','many-to-many'}: raise ValueError('invalid relationship')
    try:
        validate_map={'one-to-one':'one_to_one','one-to-many':'one_to_many','many-to-one':'many_to_one','many-to-many':'many_to_many'}
        out=left.merge(right,left_on=left_key,right_on=right_key,how=how,suffixes=('','_right'),validate=validate_map[relationship] if relationship else None)
    except pd.errors.MergeError as exc:
        raise ValueError(f'Join violates declared relationship {relationship!r}: {exc}') from exc
    if len(out)>max_output_rows: raise ValueError(f'Join would produce {len(out):,} rows, exceeding max_output_rows={max_output_rows:,}')
    return out
