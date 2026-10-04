from dataclasses import dataclass
@dataclass
class Tool:
 name:str;description:str;handler:object
class ToolRegistry:
 def __init__(self):self._tools={}
 def register(self,tool):self._tools[tool.name]=tool
 def get(self,name):return self._tools[name]
 def descriptions(self):return [{'name':t.name,'description':t.description} for t in self._tools.values()]
