from __future__ import annotations

from dataclasses import asdict, dataclass

from .provider import LLMProvider, extract_json
from src.security.guards import validate_read_only_sql


@dataclass
class AgentPlan:
    intent: str
    steps: list[str]
    sql: str | None = None
    caveats: list[str] | None = None


SYSTEM = """You are an evidence-first analytics agent. Produce JSON with intent, steps, sql, caveats. SQL must be read-only SELECT/WITH/EXPLAIN and must not contain DDL/DML, multiple statements, comments, or secrets. Never claim causality from observational data."""


def _string_list(value, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


class AnalyticsAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def plan(self, question: str, schema: dict) -> AgentPlan:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if not isinstance(schema, dict):
            raise ValueError("schema must be an object")
        msg = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Question: {question}\nSchema: {schema}"},
        ]
        obj = extract_json(self.provider.complete(msg, temperature=0))
        intent = obj.get("intent", "analysis")
        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("intent must be a non-empty string")
        steps = _string_list(obj.get("steps", []), "steps")
        caveats = _string_list(obj.get("caveats", []), "caveats")
        sql = obj.get("sql")
        if sql is not None and not isinstance(sql, str):
            raise ValueError("sql must be a string or null")
        if sql:
            sql = validate_read_only_sql(sql)
        return AgentPlan(intent.strip(), steps, sql, caveats)

    def explain(self, plan: AgentPlan) -> dict:
        return asdict(plan)
