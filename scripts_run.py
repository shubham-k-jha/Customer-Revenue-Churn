from pathlib import Path
from src.data.download import download as telco_download
from src.data.prepare import prepare as telco_prepare
from src.features.build import build as build_features
from src.models.pipeline import train

if __name__=='__main__':
    telco_download(); telco_prepare(); build_features(); train(); print('Core pipeline complete')
