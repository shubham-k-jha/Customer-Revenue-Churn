from pathlib import Path
import tempfile, json, os
import pandas as pd
import streamlit as st
import plotly.express as px
ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title='AI Data Science Workbench',layout='wide')
st.title('AI Data Science & Business Intelligence Workbench')
st.caption('Universal data → quality → analytics → ML → agent → BI/reporting workflow')

from src.universal.io import read_table,list_excel_sheets
from src.universal.profile import profile_dataframe,rank_target_candidates
from src.universal.model import train_generic
from src.platform.quality import DataQualityEngine
from src.reporting.excel_universal import write_management_workbook
from src.advanced.multitable import suggest_joins,safe_join
from src.advanced.segmentation import rfm_segment
from src.advanced.forecast import lag_forecast
from src.advanced.time_series_analysis import TimeSeriesConfig, analyze_time_series
from src.advanced.deep_timeseries import clean_series, full_diagnostics
from src.advanced.forecasting_deep import expanding_backtest
from src.models.deep_evaluation import optimize_threshold, calibration_diagnostics, decision_curve
from src.agent.provider import OpenAICompatibleProvider
from src.agent.orchestrator import AnalyticsAgent

uploads=st.sidebar.file_uploader('Upload one or more CSV/TSV/XLSX/XLS/Parquet files',type=['csv','tsv','xlsx','xls','parquet','pq'],accept_multiple_files=True)
if not uploads:
    st.info('Recruiter demo: upload a dataset to run the full universal workflow. Curated churn assets appear below when installed.')
else:
    tables={}
    for up in uploads:
        suffix=Path(up.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as f: f.write(up.getbuffer()); tmp=f.name
        try:
            sheets=list_excel_sheets(tmp); sheet=st.sidebar.selectbox(f'Sheet — {up.name}',sheets) if sheets else 0
            tables[up.name]=read_table(tmp,sheet)
        finally: Path(tmp).unlink(missing_ok=True)
    names=list(tables)
    tabs=st.tabs(['Data Quality','Multi-table','Modeling','Segmentation','Time Series','Forecasting','AI Agent'])
    with tabs[0]:
        name=st.selectbox('Dataset',names); df=tables[name]; prof=profile_dataframe(df); q=DataQualityEngine().run(df)
        a,b,c,d=st.columns(4); a.metric('Rows',f'{len(df):,}'); b.metric('Columns',f'{len(df.columns):,}'); c.metric('Duplicates',f'{df.duplicated().sum():,}'); d.metric('Memory',f"{prof['memory_mb']:.1f} MB")
        st.subheader('Quality gates'); st.json(q)
        st.subheader('Schema'); st.dataframe(pd.DataFrame(prof['profiles']),use_container_width=True,hide_index=True)
        st.subheader('Preview'); st.dataframe(df.head(100),use_container_width=True,hide_index=True)
    with tabs[1]:
        if len(tables)<2: st.info('Upload at least two datasets to discover possible joins.')
        else:
            candidates=suggest_joins(tables)
            st.dataframe(pd.DataFrame([c.__dict__ for c in candidates]),use_container_width=True,hide_index=True)
            if candidates:
                c=candidates[0]; st.caption('Suggestions are evidence-based; no join is executed automatically.')
                if st.button('Preview highest-overlap join'):
                    st.dataframe(safe_join(tables[c.left_table],tables[c.right_table],c.left_key,c.right_key).head(100),use_container_width=True)
    with tabs[2]:
        name=st.selectbox('Training dataset',names,key='model_dataset'); df=tables[name]; candidates=rank_target_candidates(df); target=st.selectbox('Target', ['None']+list(df.columns),index=1 if candidates else 0)
        task=st.selectbox('Task',['Auto-detect','Classification','Regression']); prof=profile_dataframe(df); date_candidates=[x['name'] for x in prof['profiles'] if x['likely_date'] and x['name']!=target]; datecol=st.selectbox('Date column',['None']+date_candidates)
        drops=st.multiselect('Exclude columns',list(df.columns),default=[x['name'] for x in prof['profiles'] if (x['likely_id'] or x['likely_date']) and x['name']!=target])
        if target!='None' and st.button('Run leakage-aware model benchmark',type='primary'):
            with st.spinner('Cross-validation and held-out evaluation...'):
                result=train_generic(df,target,None if task=='Auto-detect' else task.lower(),drops,ROOT/'artifacts/universal_uploaded_model.joblib',None if datecol=='None' else datecol)
            st.success(f"Selected by CV: {result['winner']}"); st.dataframe(pd.DataFrame(result['comparison']),use_container_width=True)
    with tabs[3]:
        st.write('RFM customer segmentation')
        df=tables[st.selectbox('RFM dataset',names,key='rfm_dataset')]
        if len(df.columns)>=3:
            cc=st.selectbox('Customer column',list(df.columns),key='rfm_c'); dc=st.selectbox('Date column',list(df.columns),key='rfm_d'); ac=st.selectbox('Amount column',list(df.columns),key='rfm_a')
            if st.button('Build RFM segments'):
                r=rfm_segment(df,cc,dc,ac); st.dataframe(r,use_container_width=True); st.plotly_chart(px.scatter(r,x='frequency',y='monetary',size='recency',color='segment_id'),use_container_width=True)
    with tabs[4]:
        df=tables[st.selectbox('Time-series dataset',names,key='ts_dataset')]
        dc=st.selectbox('Time-series date',list(df.columns),key='ts_d'); vc=st.selectbox('Time-series value',list(df.columns),key='ts_v')
        period=st.number_input('Seasonal period (optional; 0 disables decomposition)',0,365,0,key='ts_period')
        window=st.number_input('Rolling window',2,365,7,key='ts_window')
        max_lags=st.number_input('Maximum ACF/PACF lag',1,120,24,key='ts_lags')
        if st.button('Run time-series diagnostics',type='primary'):
            try:
                r=analyze_time_series(df,TimeSeriesConfig(dc,vc,seasonal_period=int(period) if period else None,max_lags=int(max_lags),rolling_window=int(window)))
                a,b,c=st.columns(3); a.metric('Observations',r['frequency']['observations']); b.metric('Median spacing',r['frequency']['median_delta']); c.metric('ADF p-value',f"{r['stationarity']['p_value']:.4g}")
                st.subheader('Stationarity'); st.json(r['stationarity'])
                st.subheader('Autocorrelation'); st.line_chart(pd.DataFrame({'ACF':r['autocorrelation']['acf'],'PACF':r['autocorrelation']['pacf']}))
                st.subheader('Rolling statistics'); st.dataframe(r['rolling'],use_container_width=True,hide_index=True)
                st.subheader('Dominant periods'); st.dataframe(pd.DataFrame(r['dominant_periods']),use_container_width=True,hide_index=True)
                if 'decomposition' in r:
                    st.subheader('Seasonal decomposition'); st.line_chart(r['decomposition'][['observed','trend','seasonal','resid']])
                st.divider(); st.subheader('Deep diagnostics')
                s=clean_series(df,dc,vc)
                deep=full_diagnostics(s,int(period) if period else None,int(window),int(max_lags))
                st.json({k:v for k,v in deep.items() if k not in {'outliers','autocorrelation'}})
                st.subheader('Recent robust outlier flags')
                st.dataframe(pd.DataFrame(deep['outliers']).tail(100),use_container_width=True,hide_index=True)
            except Exception as exc: st.error(str(exc))
    with tabs[5]:
        df=tables[st.selectbox('Forecast dataset',names,key='fc_dataset')]
        dc=st.selectbox('Forecast date',list(df.columns),key='fc_d'); vc=st.selectbox('Forecast value',list(df.columns),key='fc_v'); horizon=st.number_input('Forecast periods',1,90,14)
        season=st.number_input('Seasonal period for baseline comparison',0,365,7,key='fc_season')
        initial=st.number_input('Initial training observations',10,10000,56,key='fc_initial')
        step=st.number_input('Backtest step',1,365,7,key='fc_step')
        if st.button('Run expanding-window forecast benchmark',type='primary'):
            try:
                s=clean_series(df,dc,vc)
                r=expanding_backtest(s,int(horizon),int(initial),int(step),int(season) if season else None)
                st.success(f"Winner by mean backtest RMSE: {r['winner_by_rmse']}")
                st.dataframe(pd.DataFrame(r['summary']),use_container_width=True,hide_index=True)
                st.caption('Model selection uses repeated expanding-window validation; the final future horizon is not used to select the winner.')
            except Exception as exc: st.error(str(exc))
    with tabs[6]:
        name=st.selectbox('Agent dataset',names,key='agent_dataset'); df=tables[name]; question=st.text_area('Ask an analytics question','What are the main drivers of revenue in this dataset?')
        st.caption('Live LLM calls require LLM_API_KEY/OPENAI_API_KEY. Without credentials this tab intentionally does not fabricate an answer.')
        if st.button('Create guarded analysis plan'):
            schema={c:str(df[c].dtype) for c in df.columns}
            try:
                plan=AnalyticsAgent(OpenAICompatibleProvider()).plan(question,schema); st.json(plan.__dict__)
            except Exception as exc: st.error(str(exc))

st.divider(); st.header('Curated Churn Intelligence')
DATA=ROOT/'data/processed/model_dataset.csv'
if DATA.exists():
    df=pd.read_csv(DATA); a,b=st.columns(2); a.metric('Customers',f'{len(df):,}'); b.metric('Observed churn',f"{df.churn_flag.mean():.1%}" if 'churn_flag' in df else 'n/a')
else: st.info('Curated Telco data not installed. Universal Workbench is ready above.')
