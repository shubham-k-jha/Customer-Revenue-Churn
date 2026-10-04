from pathlib import Path
import json

def build_model_card(metadata, output='reports/model_card.json'):
    card={'model':metadata,'intended_use':'Business decision support; not autonomous decision-making.','limitations':['Predictive association is not causal evidence.','Performance depends on data quality and population stability.','Thresholds should be chosen using business costs and validated data.'],'governance':['Keep an untouched final evaluation period.','Track dataset/model hashes.','Monitor drift and performance after deployment.']}
    p=Path(output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(card,indent=2,default=str)); return card
