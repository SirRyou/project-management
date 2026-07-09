# 7. Third-Party Isolation & Dependency Governance

## 7.1 Adapter Pattern

Do not spread raw SDK calls (OpenAI, ElevenLabs, Stripe, etc.) across presentation or domain
components. Wrap them in generic **Adapter/Interface** classes.

If a dependency is deprecated or breaks, you should be able to swap the implementation by
changing **only the adapter**, keeping the core domain completely untouched.

## 7.2 Before Introducing a New Dependency

- [ ] Justify why the standard library is insufficient.
- [ ] Verify active maintenance (recent commits, responsive maintainers).
- [ ] Verify license compatibility.
- [ ] Evaluate bundle/binary size impact.
- [ ] Check for duplicate libraries solving the same problem.
- [ ] Review the transitive dependency tree.
- [ ] Assess security advisory history.

## 7.3 Ongoing Dependency Hygiene

- Pin versions in lockfiles.
- Run automated vulnerability scanning (`npm audit`, `cargo audit`, Dependabot, etc.).
- Schedule periodic dependency updates.
