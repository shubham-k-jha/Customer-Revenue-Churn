from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'; PROCESSED=ROOT/'data'/'processed'; ARTIFACTS=ROOT/'artifacts'; REPORTS=ROOT/'reports'
for p in [RAW,PROCESSED,ARTIFACTS,REPORTS]: p.mkdir(parents=True,exist_ok=True)
DATA_URL=os.getenv('DATA_URL','https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv')
RANDOM_STATE=int(os.getenv('RANDOM_STATE','42'))
HIGH_RISK_THRESHOLD=float(os.getenv('HIGH_RISK_THRESHOLD','0.60'))
MEDIUM_RISK_THRESHOLD=float(os.getenv('MEDIUM_RISK_THRESHOLD','0.30'))
RETENTION_OFFER_COST=float(os.getenv('RETENTION_OFFER_COST','20'))
EXPECTED_SAVED_MONTHS=float(os.getenv('EXPECTED_SAVED_MONTHS','6'))
GROSS_MARGIN_RATE=float(os.getenv('GROSS_MARGIN_RATE','0.70'))
