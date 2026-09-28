---
name: cypress-selector
description: 'Can write Cypress selectors in the way we want to use them. Always load this skill when writing cypresss.'
---

# Cypress selector priorities

Apply this priority order whenever a Cypress test needs to find an element. Always load this skill before writing or editing a Cypress spec.

## 1. Select by what the user can read or see

Prefer selectors that mimic how a real user finds the element: by its visible text.

- Use `cy.contains(text)` or `cy.contains(selector, text)` to scope to a container first.
- This is the default choice. Only move to step 2 when no stable, unique visible text exists (e.g. an icon-only button, a generic container with no unique label).

```ts
cy.contains('button', 'Add to cart').click();
```

## 2. Fall back to `data-cy`

If there is no visible/unique text to select on, use a `data-cy` attribute instead. Add a comment in the test next to the selector explaining why the fallback was needed (e.g. icon-only control, no unique text, dynamic/ambiguous text).

```ts
// Icon-only button has no visible text to select on.
cy.get('[data-cy="add-to-cart"]').click();
```

If the element doesn't have a `data-cy` attribute yet, add one to the source component rather than reaching for a CSS class, id, or DOM structure selector.

## 3. Never use `cy.findByRole` / Testing Library queries

Do not use `cy.findByRole`, `cy.findByLabelText`, or other `@testing-library/cypress` queries in this project. They are noticeably slower and are not the convention here — do not add `@testing-library/cypress` as a dependency.

## What to avoid

- CSS classes, ids, or DOM structure/nesting (e.g. `.ant-input-search input`, `.ant-select-dropdown`).
- Arbitrary waits — use `cy.intercept()` + `cy.wait('@alias')` or retrying assertions instead.
