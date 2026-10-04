from __future__ import annotations

import re
from pathlib import Path

DANGEROUS_SQL = re.compile(r"\b(drop|delete|update|insert|alter|truncate|create|grant|revoke|copy|into|call|do|vacuum|refresh)\b", re.I)
LOCKING_SQL = re.compile(r"\bfor\s+(update|share)\b", re.I)


def _mask_sql_literals(sql: str) -> str:
    """Mask quoted literals so words like 'delete' are not treated as SQL verbs."""
    out=[]; i=0; quote=None
    while i < len(sql):
        ch=sql[i]
        if quote:
            if ch == quote:
                if i + 1 < len(sql) and sql[i+1] == quote:
                    out.extend('  '); i += 2; continue
                quote=None
            out.append(' '); i += 1; continue
        if ch in "'\"`":
            quote=ch; out.append(' '); i += 1; continue
        out.append(ch); i += 1
    return ''.join(out)


def validate_read_only_sql(sql):
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError('SQL must be a non-empty string')
    s = sql.strip()
    # Comments are deliberately rejected because they complicate reliable static safety checks.
    if '--' in s or '/*' in s or '*/' in s:
        raise ValueError('SQL comments are not permitted')
    had_terminal_semicolon = s.endswith(';')
    body = s[:-1].rstrip() if had_terminal_semicolon else s
    if ';' in _mask_sql_literals(body):
        raise ValueError('Multiple SQL statements are not permitted')
    s = body
    if not re.match(r'^(select|with|explain)\b', s, re.I):
        raise ValueError('Only read-only SELECT/WITH/EXPLAIN statements are permitted')
    masked = _mask_sql_literals(s)
    if re.search(r'\bexplain\s+analyze\b', masked, re.I):
        raise ValueError('EXPLAIN ANALYZE is not permitted in the read-only SQL guard')
    if DANGEROUS_SQL.search(masked) or LOCKING_SQL.search(masked):
        raise ValueError('Potentially mutating or locking SQL detected')
    return s


def validate_upload(filename, size_bytes, max_bytes=100*1024*1024):
    allowed={'.csv','.tsv','.xlsx','.xls','.parquet','.pq'}
    if Path(filename).suffix.lower() not in allowed:
        raise ValueError('Unsupported tabular file format')
    if size_bytes < 0:
        raise ValueError('File size cannot be negative')
    if size_bytes > max_bytes:
        raise ValueError(f'File exceeds {max_bytes//(1024*1024)} MB limit')
