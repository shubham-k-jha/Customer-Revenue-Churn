from __future__ import annotations
from src.security.guards import validate_read_only_sql
class SQLAgent:
    def __init__(self, executor=None): self.executor=executor
    def validate(self,sql): return validate_read_only_sql(sql)
    def execute(self,sql):
        sql=self.validate(sql)
        if self.executor is None: raise RuntimeError('No SQL executor configured')
        return self.executor(sql)
