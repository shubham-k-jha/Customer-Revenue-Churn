import json
from src.registry.registry import ModelRegistry
from src.production.settings import settings

p='artifacts/model_summary.json'
meta=json.loads(open(p).read()) if __import__('os').path.exists(p) else {'status':'untrained'}
print(ModelRegistry(settings.registry_path).register(settings.model_path,meta))
