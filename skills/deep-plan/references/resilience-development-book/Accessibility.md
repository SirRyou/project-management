# 15. Accessibility

Accessibility is **part of correctness**, not a nice-to-have.

## 15.1 Minimum Requirements for Every UI Feature

- [ ] Full keyboard navigation (Tab, Enter, Escape, Arrow keys)
- [ ] Visible focus indicators on all interactive elements
- [ ] Screen reader labels (`aria-label`, `aria-describedby`, roles)
- [ ] Sufficient color contrast (WCAG AA minimum: 4.5:1 for text)
- [ ] Reduced motion support (`prefers-reduced-motion`)
- [ ] Semantic HTML (`<button>`, `<nav>`, `<main>`, `<h1>`–`<h6>`)
- [ ] Form inputs have associated labels
- [ ] Error messages are announced to assistive technology
- [ ] Touch targets are at least 44×44px on mobile

## 15.2 Automated Checks

- Run accessibility linting in CI (`axe-core`, `eslint-plugin-jsx-a11y`, etc.).
- Manual screen reader testing for all critical flows.
