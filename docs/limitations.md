# Limitations

- Public sample data is fictional and not a production CRM extract.
- Single customer snapshot; no true time series of customer states.
- Churn label represents an observed historical outcome, not a future event horizon designed by this project.
- No randomized treatment/offer field, so retention uplift cannot be estimated causally.
- Demographic/service features may reflect historical business processes and should be reviewed for fairness and policy compliance before deployment.
- `TotalCharges` is cumulative and may encode tenure-related information; model interpretation must respect this relationship.
- Performance on this sample does not establish generalization to another telecom population.
