# API examples

Start:
```bash
uvicorn api.main:app --reload --port 8000
```

Health:
```bash
curl http://localhost:8000/health
```

Model metadata:
```bash
curl http://localhost:8000/model
```

Prediction:
```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"tenure":12,"MonthlyCharges":79.9,"TotalCharges":900,"Contract":"Month-to-month","gender":"Female","Partner":"No","Dependents":"No","PhoneService":"Yes","MultipleLines":"No","InternetService":"Fiber optic","OnlineSecurity":"No","OnlineBackup":"No","DeviceProtection":"No","TechSupport":"No","StreamingTV":"No","StreamingMovies":"No","PaperlessBilling":"Yes","PaymentMethod":"Electronic check"}'
```
