# Security Model

- File extensions and upload size are validated before parsing.
- SQL API accepts only a single read-only SELECT/WITH/EXPLAIN statement.
- Destructive SQL keywords are rejected.
- API key authentication is supported through `PLATFORM_API_KEY`.
- Secrets belong in environment variables, never source control.
- Uploaded files should be processed in a sandboxed runtime in production.
- Logs should avoid raw customer PII.
- Database credentials should use least privilege and read-only credentials for the SQL agent.
- Add network egress restrictions when deploying an LLM-powered agent.
