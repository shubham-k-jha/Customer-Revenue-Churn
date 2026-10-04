from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_name: str = 'Customer Intelligence API'
    model_path: str = 'artifacts/model_bundle.joblib'
    registry_path: str = 'models/registry.json'
    data_path: str = 'data/processed/model_dataset.csv'
    postgres_url: str = 'postgresql+psycopg2://postgres:postgres@postgres:5432/churn'
    prediction_log_path: str = 'artifacts/prediction_log.parquet'
    random_state: int = 42

settings = Settings()
