import json
from src.config import RAW,PROCESSED
from src.data.quality import load_and_validate,quality_report

def main():
    df=load_and_validate(RAW/'telco_customer_churn.csv')
    out=PROCESSED/'customer_clean.csv'; df.to_csv(out,index=False)
    (PROCESSED/'quality_report.json').write_text(json.dumps(quality_report(df),indent=2))
    print(json.dumps(quality_report(df),indent=2))
if __name__=='__main__': main()
