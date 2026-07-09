# Reference: Design/UI-UX Review

This reference document outlines the conditional Design/UI-UX lens executed during Step 6 of the `deep-plan` workflow.

---

## 1. When to Trigger the UI/UX Lens

Inspect the Scope Brief (Step 2A) and in-scope items (Step 2B) for any work involving:
- User interfaces (UI) or user experience (UX) flows.
- Frontend development, layout structures, components, styling, or settings pages.
- Visual assets, mockups, screens, or interactive components.

If any of these conditions are met, the Design/UI-UX review lens is **mandated** and must be run.

---

## 2. What to Review

When the UI/UX lens is active:
1. **Source Designs**: Request the user to provide mockups, wireframes, screenshots, or design descriptions if they are not already in the context.
2. **Review Execution**: Invoke the `uiux-review` skill (or equivalent design auditing tool/agent you have) to analyze the provided layouts.
3. **Core Design Evaluation**:
   - Check layout responsiveness and visual hierarchy.
   - Audit accessibility, cognitive load, and styling standards.
   - Enforce consistency with existing design tokens and spacing systems.

---

## 3. How Findings Integrate with Amendments

- **Additive Nature**: UI/UX review findings are **additive** to the Eng/Security review results. They do not replace or substitute the technical and security adversarial review passes.
- **Compilation**: Once the UI/UX review concludes, compile its actionable findings into the **Amendments to Incorporate** list under the `From Design/UI-UX Review` section:

```markdown
From Design/UI-UX Review:
- [Design finding/gap] → [What changes in task or style token] / REJECTED: [Reason]
```

- **Confirmation**: Present the combined amendments list (Scope + Eng/Security + UI/UX) to the user for final approval before writing the roadmap.
