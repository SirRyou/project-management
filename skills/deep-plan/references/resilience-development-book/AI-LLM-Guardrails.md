# 12. AI / LLM Guardrails

## 12.1 Rate Limits, Timeouts & Retries

Every LLM, TTS, or generation API call must have:

- A strict local timeout (e.g., 15 seconds).
- Exponential backoff retry (up to 3 retries on network/429 failures).
- A defined maximum retry count before hard failure.

## 12.2 Fallback Models

Define a lightweight, reliable fallback model/provider if the primary model fails or experiences
severe latency (e.g., switch to a smaller/local model, or return a friendly static fallback
response).

## 12.3 Token & Context Budget

Implement strict guardrails on session token generation. Prompt pipelines must truncate overflow
context using a **sliding window algorithm** rather than crashing at context limit errors.

## 12.4 Agent Explainability

Whenever an AI agent makes a decision, emit **structured reasoning metadata** — not raw
chain-of-thought. Emit metadata when an agent:

- Plans work
- Invokes tools
- Retries a failed operation
- Aborts a task or changes strategy mid-execution
- Selects between multiple approaches

Metadata schema example:

```json
{
  "planner": "task-planner-v2",
  "decision": "fallback_to_local_model",
  "reason": "primary_timeout",
  "retry": 2,
  "confidence": 0.87,
  "alternatives_considered": ["retry_primary", "skip_step"]
}
```

Metadata must be **machine-parseable**. Do not expose raw chain-of-thought in production logs.
Metadata should be sufficient to reconstruct the decision without re-running the agent.
