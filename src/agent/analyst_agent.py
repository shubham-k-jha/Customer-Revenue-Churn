from dataclasses import dataclass,field
from .tools import ToolRegistry,Tool
@dataclass
class AnalysisPlan:
 question:str;steps:list[str]=field(default_factory=list);evidence:list[dict]=field(default_factory=list);conclusions:list[str]=field(default_factory=list)
class AnalystAgent:
 def __init__(self):self.tools=ToolRegistry()
 def register_default_tools(self,profile_fn,quality_fn,sql_fn,model_fn):
  self.tools.register(Tool('profile','Profile schema and distributions',profile_fn));self.tools.register(Tool('quality','Run data-quality gates',quality_fn));self.tools.register(Tool('sql','Execute validated read-only SQL',sql_fn));self.tools.register(Tool('model','Train/evaluate a governed model',model_fn))
 def plan(self,question):return AnalysisPlan(question=question,steps=['profile data','validate quality','choose analytical method','run SQL/statistics/modeling','validate outputs','produce evidence-backed business summary'])
