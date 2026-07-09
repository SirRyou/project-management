# 17. Documentation & Architecture Decisions

Every significant engineering decision should leave written documentation.

## 17.1 What to Document

| Artifact                     | Purpose                                        |
|------------------------------|------------------------------------------------|
| ADR (Architecture Decision)  | Why a specific approach was chosen             |
| Migration rationale          | Why and how data or APIs were migrated         |
| Protocol changes             | What changed and backward compatibility impact |
| Tradeoffs                    | What was considered and rejected               |

## 17.2 Standards

- Use a consistent ADR template (status, context, decision, consequences).
- Store documentation **alongside code**, not in separate wikis.
- Future developers should understand **why**, not only **what**.
