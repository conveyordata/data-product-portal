---
name: portal-design
description: Design guide for the Data Product Portal UI - information architecture, task flows, statuses, components, icons, terminology, typography, colour and onboarding. Use when designing or building a screen or feature in frontend/, reviewing a UI change, or looking for visual or UX inconsistencies.
---

# Portal design

Apply these rules when you design, build or review anything a portal user sees. Each section has a principle, the rules, and where to check them in this repository. Paths describe the repository at the time of writing: if one moved, find its successor rather than skipping the check.

## Before you start

- Read `frontend/AGENTS.md` for the implementation rules (Ant Design components, theme tokens, semantic size tokens, i18next, no custom CSS).
- Read `CONTEXT.md` for the domain terms. They are the glossary for user-facing copy too.
- Look at how two or three existing screens solve the same problem before adding anything. Reuse what `frontend/src/components/` already offers; a new pattern needs a reason.

## 1. Information architecture and navigation

Principle: structure every screen around what the user needs to do, not around the data model.

- Start from the user's task ("request access", "check my pending requests") and work back to the screen.
- Put items that need attention (pending actions, incomplete setup) in a prominent, prioritised position.
- Show hierarchy visually when one entity lives under another: an Output Port page shows which Data Product it belongs to in a parent context header, not only in the breadcrumb.
- Every child page offers a way back up its hierarchy (Output Port to Data Product).
- Do not use tabs as a catch-all. A task with several steps or that needs focus gets a dedicated flow that shows the number of steps upfront (see `frontend/src/components/wizard/`).

## 2. Task flows

Principle: every flow tells the user what happens next and never ends on an empty or ambiguous state.

- After an action that creates or completes something, show the next step.
- Minimise clicks for high-frequency actions such as reviewing pending requests.
- Test a new flow as a first-time user with no one to ask; add guidance where they would get stuck.
- Never show a screen with no data and no explanation. Empty states explain what the screen is and what to do, using one shared pattern.
- One conceptual action (for example creating an Output Port) has one canonical entry point.

## 3. Screen and concept differentiation

Principle: a user knows what kind of screen they are on without reading the breadcrumb.

- Each core concept (Product Studio, Marketplace, Data Product, Output Port) has a distinct, consistently applied treatment: layout, colour accent or icon.
- Prefer progressive disclosure over tabs for complex entities.
- Make relationships visible in the UI: Data Product to Output Port to Technical Asset.
- A new concept-level object needs a one-sentence definition of how it differs from the existing ones.
- Product Studio (manage) and Marketplace (browse) keep distinct intents and interaction patterns.

## 4. Rows, cards and statuses

Principle: a user scanning a list understands state and priority without opening anything.

- Every object type has a defined status set, shown with the same colour, icon and label everywhere it appears.
- Decide the 2-3 facts a card or row must show at a glance before building it.
- Consider every persona that sees the object (owner, producer, consumer) and which fields matter to each.
- A status that implies a manual step makes that next action clear.

## 5. Components

Principle: the same interaction looks and behaves the same everywhere.

- Buttons: one placement for edit, add, save and delete, and one rule for text, icon or icon plus text. Follow the existing buttons in `frontend/src/components/buttons/` and on comparable screens.
- Modal for a quick single-step confirmation; a page for multi-step or data-heavy tasks; inline only for small edits.
- One empty-state pattern: icon or illustration, explanation, primary action.
- One table pattern: pagination placement, row density and action column position match the other list views.
- Never introduce a new modal, form or table layout without checking for an existing one.

## 6. Iconography

Principle: every icon has one meaning and is never the only way to trigger an important action.

- Classify each icon as action, status or decorative before using it.
- Action icons carry a text label. Icon-only buttons are only for universally recognised actions (delete with confirmation) and always have a tooltip.
- Use one icon set: `@ant-design/icons`, plus the portal's own icons under `frontend/src/components/icons/` and the assets they load. Same stroke, radius and fill style.
- Icons of the same semantic weight have the same size.
- One icon shape never carries two meanings. Search the frontend for the icon before introducing it, and reuse the icon that already represents the concept.
- Icon colour follows the colour rules in section 9.

## 7. Terminology

Principle: every core term has one meaning, one spelling and one casing, everywhere.

- Use the terms and definitions in `CONTEXT.md` (Data Product, Output Port, Input Port, Technical Asset, ...) in UI copy and docs. A term used in two meanings is a defect.
- All copy goes through i18next (`frontend/public/locales/`); keep casing and pluralisation consistent across keys.
- Add a tooltip or short help next to terms a new user would not understand, and link to the docs from the relevant screen.
- Prefer plain language over engineering terms for audiences such as data consumers.
- Keep integration names (Conveyor, GitHub, ...) out of user-facing copy unless they are genuinely clearer.

## 8. Typography

Principle: visual weight reflects importance.

- Use the Ant Design type scale (`Typography`, `token.fontSize*`) and no ad-hoc font sizes.
- Cards and rows read title, then description, then metadata, with decreasing weight.
- Secondary text must still meet contrast standards.
- Similar components share width, title size and text hierarchy (for example all Marketplace cards).
- Design for realistic content length: long names (Technical Assets) must not break a layout; truncate with a tooltip.

## 9. Colour

Principle: colour carries meaning.

- Use the semantic tokens from the theme (`frontend/src/theme/antd-theme.ts`, read with `theme.useToken()`): primary, success, warning, error and neutral. No hardcoded colours.
- Apply the same meaning to buttons, statuses and icons alike.
- One primary action colour; do not mix black and coloured primary buttons.
- A page that deviates from the palette needs a documented reason.

## 10. First-time experience

Principle: a new user is never left wondering what to do next.

- Major feature areas offer a guided tour or contextual walkthrough.
- Setup actions end with clear next-step guidance.
- Sample data (`backend/sample_data.sql`) tells a coherent, believable story.
- The product teaches its essentials; do not rely on external docs for basic concepts.

## Reviewing a screen

When asked to review a screen or hunt for inconsistencies, compare it against equivalent screens section by section, name the rule each finding breaks, and show it with a screenshot or a file reference. The fix aligns with what most equivalent screens already do; never introduce a new visual style to resolve an inconsistency.
