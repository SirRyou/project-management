# 14. Code Complexity Budget

AI-generated code is especially prone to producing 300–500 line functions that "work" but are
unmaintainable. Apply the same standards regardless of code origin.

## 14.1 Guidelines

| Rule                              | Guideline                  |
|-----------------------------------|----------------------------|
| Maximum lines per function        | < 50 (guideline)           |
| Maximum nesting depth             | ≤ 3 control blocks         |
| Single responsibility per function| Always, especially public  |
| Prefer composition over nesting   | Always                     |

## 14.2 When Complexity Is Necessary

If a feature requires complex orchestration:

- Introduce dedicated service modules.
- Use state machines instead of deeply nested conditionals.
- Extract configuration objects for functions with many parameters.
- Use builder patterns for complex object construction.

## 14.3 Enforcement

- Track cyclomatic complexity in CI (e.g., `complexity-report`, `radon`, `escomplex`).
- Flag functions exceeding complexity thresholds for mandatory review.
