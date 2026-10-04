from src.data.prepare import main as prepare
from src.features.build import main as features
from src.models.pipeline import train
from src.analytics.eda import make_plots
from src.data.quality import load_and_validate
from src.config import RAW

if __name__=='__main__':
    prepare(); features(); result,summary=train(); df=load_and_validate(RAW/'telco_customer_churn.csv'); make_plots(df)
    print('PIPELINE COMPLETE'); print(result.to_string(index=False)); print(summary)
