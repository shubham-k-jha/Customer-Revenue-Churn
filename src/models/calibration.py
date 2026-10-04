import json, joblib, pandas as pd, numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

def calibration_report(y, p, bins=10):
    prob_true, prob_pred=calibration_curve(y,p,n_bins=bins,strategy='quantile')
    return {'brier':float(brier_score_loss(y,p)),'mean_predicted':prob_pred.tolist(),'observed_frequency':prob_true.tolist()}
