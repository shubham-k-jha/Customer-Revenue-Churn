# Data Dictionary

| Field | Type | Meaning | Modeling role |
|---|---|---|---|
| customerID | string | Customer identifier | ID only |
| gender | category | Customer-reported gender in source | Predictor |
| SeniorCitizen | binary | Senior-citizen indicator | Predictor |
| Partner | binary | Partner indicator | Predictor |
| Dependents | binary | Dependent indicator | Predictor |
| tenure | integer | Months with provider | Predictor |
| PhoneService | category | Phone service status | Predictor |
| MultipleLines | category | Multiple-line status | Predictor |
| InternetService | category | Internet service type | Predictor |
| OnlineSecurity | category | Security add-on | Predictor |
| OnlineBackup | category | Backup add-on | Predictor |
| DeviceProtection | category | Device-protection add-on | Predictor |
| TechSupport | category | Technical support add-on | Predictor |
| StreamingTV | category | TV streaming add-on | Predictor |
| StreamingMovies | category | Movie streaming add-on | Predictor |
| Contract | category | Contract type | Predictor |
| PaperlessBilling | binary | Paperless billing status | Predictor |
| PaymentMethod | category | Payment method | Predictor |
| MonthlyCharges | numeric | Current monthly charge | Predictor / revenue |
| TotalCharges | numeric | Total charges to date | Predictor, with caveat |
| Churn | binary | Whether customer churned | Target |

`TotalCharges` has 11 blank source values. These correspond to zero-tenure customers; the pipeline preserves those rows and records `total_charges_missing` before replacing the modeling value with 0.

Source structure and the 7,043-row/21-column shape are documented in the public IBM sample. citeturn0search0turn1view0
