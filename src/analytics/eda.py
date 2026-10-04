from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import REPORTS

def make_plots(df):
    out=REPORTS/'figures'; out.mkdir(exist_ok=True)
    sns.set_theme(style='whitegrid')
    plots=[('Contract','Churn','churn_by_contract.png'),('InternetService','Churn','churn_by_internet.png'),('PaymentMethod','Churn','churn_by_payment.png')]
    for col,target,name in plots:
        rate=df.groupby(col,observed=False)['churn_flag'].mean().sort_values(ascending=False)
        ax=rate.mul(100).plot(kind='bar',figsize=(9,5),title=f'Churn rate by {col}')
        ax.set_ylabel('Churn rate (%)'); plt.tight_layout(); plt.savefig(out/name,dpi=160); plt.close()
    return out
