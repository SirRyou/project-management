# 16. Feature Flags & Safe Rollouts

Large features should not be permanently coupled into production.

## 16.1 Required Mechanisms

- **Feature flags**: Toggle features without redeployment.
- **Gradual rollout**: Enable for a percentage of users first.
- **Kill switches**: Immediately disable a feature in production.

## 16.2 Flag Hygiene

- Every flag must have an **owner** and a **removal date**.
- Expired flags must be cleaned up within a defined sprint.
- All flag combinations must be covered by tests — flags must not create untested code paths.
