# 10. Observability: Logging, Metrics & Tracing

## 10.1 Structured Error Logging

Every caught error must be logged as a structured object containing:

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "error",
  "message": "Failed to process upload",
  "request_id": "req-abc-123",
  "error": {
    "type": "FileTooLarge",
    "classification": "Parsing",
    "message": "File exceeds 10MB limit",
    "stack": "..."
  },
  "context": {
    "file_size_bytes": 15728640,
    "max_size_bytes": 10485760
  }
}
```

Error classifications: `Network`, `Permission`, `Parsing`, `Model`, `Logic`.

## 10.2 Log Levels

| Level   | Meaning                       | Action Required             |
|---------|-------------------------------|-----------------------------|
| `debug` | Development diagnostics       | None (disabled in prod)     |
| `info`  | Normal operational events     | None                        |
| `warn`  | Degraded but functional       | Investigate soon            |
| `error` | Operation failed              | Investigate now             |
| `fatal` | System cannot continue        | Immediate response          |

Never log at `error` for expected conditions. Never log sensitive data.

## 10.3 Metrics (Beyond Logs)

| Signal  | Answers                      | Example                           |
|---------|------------------------------|-----------------------------------|
| Logs    | What happened?               | "User X failed to upload file Y"  |
| Metrics | How often is it happening?   | "Upload failure rate: 2.3%"       |
| Traces  | Where is time spent?         | "Auth took 400ms of 600ms total"  |

Minimum metrics to track: request success rate, retry frequency, timeout frequency, cache hit
ratio, p95/p99 response time, queue depth, error rate by category.

## 10.4 Diagnostics Export

Provide a mechanism to write logs to a rotatable local diagnostic file so users can export logs
for troubleshooting if a crash occurs.
