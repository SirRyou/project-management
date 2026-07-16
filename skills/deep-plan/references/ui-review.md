# Reference: Design/UI-UX Review

Conditional Design/UI-UX lens executed during Phase 4 (Adversarial Review) of the deep-plan workflow.

---

## 1. When to Trigger

Inspect the Scope Brief (Phase 1) and in-scope items for any work involving:
- User interfaces (UI) or user experience (UX) flows
- Frontend development, layout structures, components, styling, settings pages
- Visual assets, mockups, screens, interactive components

If any of these conditions are met, the Design/UI-UX review is **mandated**.

---

## 2. What to Review

1. **Source Designs**: Request the user to provide mockups, wireframes, screenshots, or design descriptions if not already in context.
2. **Review Execution**: Run a design audit against the provided layouts.
3. **Core Evaluation**:
   - Layout responsiveness and visual hierarchy
   - Accessibility, cognitive load, styling standards
   - Consistency with existing design tokens and spacing systems

---

## 3. How Findings Integrate

- **Additive**: UI/UX findings supplement the Eng/Security review. They do not replace it.
- **Compilation**: Add findings to the amendments list:

```markdown
From Design/UI-UX Review:
- [Design finding/gap] → [What changes in task or style] / REJECTED: [Reason]
```

- **Confirmation**: Present the combined amendments list (Scope + Eng/Security + UI/UX) to the user for final approval.
