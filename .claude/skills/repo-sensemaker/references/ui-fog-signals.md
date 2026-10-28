# UI Fog Signals: Checkable Indicators of UI-Complexity Problems

## About This Document
This registry lists specific, evidence-based signals for detecting `ui_fog` in repositories.
**UI Fog** occurs when the primary problem is **screen design, interaction patterns, navigation structure, or design system coherence**.

Use these signals to distinguish `ui_fog` from other fog types:
- `product_fog`: Unclear user needs, missing feature specs (not about screens)
- `architecture_fog`: Code structure, module boundaries, coupling (not about UI)
- `docs_fog`: Missing documentation (not specifically about UI)
- `ui_fog`: Problems with screens, flows, components, design consistency, user interactions

---

## Tier 1 Signals: Strong Evidence of UI Fog (Weight: High)

### 1.1 Missing UI Flow Documentation
**What to check**: Does the codebase have documented user flows, screens, or interactions?
- **Signal present**: Repository contains
  - `/docs/ui-flows.md` or `/design/flows/` with user journey diagrams
  - Storybook or component documentation showing screen states
  - Figma links or design specs referenced in code
- **Signal absent**: User interaction flows are undocumented; screens not mapped
- **Evidence marker**: Look in README, `/docs/`, `/design/`, or code comments for UI documentation references

### 1.2 Complex Frontend Codebase Without Component Boundaries
**What to check**: Is the frontend code organized? Are components reusable or scattered?
- **Signal present**: Codebase has
  - `/components/` or `/src/components/` with clear component hierarchy
  - Design tokens or CSS variables in consistent location
  - Component library documentation or Storybook
- **Signal absent**:
  - Frontend files scattered across directories without logical grouping
  - Each page/screen reimplements similar UI logic
  - No visible component abstraction layer
- **Evidence marker**: Run `find . -name "*.jsx" -o -name "*.tsx" | head -20` to see file distribution

### 1.3 Routing Complexity Without Navigation Architecture
**What to check**: Does the app have clear navigation structure? Is routing logic explicit?
- **Signal present**: Codebase shows
  - Explicit router configuration (e.g., `routes.ts`, `router.config.js`)
  - Route definitions in one or two files
  - Navigation hierarchy documented in README or docs
- **Signal absent**:
  - Routes defined inline in multiple files
  - Unclear how screens connect to each other
  - Navigation structure not documented
- **Evidence marker**: Search for route definitions; count files containing route logic

### 1.4 Design System Fragmentation or Absence
**What to check**: Is there a unified design language? Or is styling inconsistent?
- **Signal present**: Codebase has
  - Design tokens file (`tokens.json`, `tokens.ts`, `theme.ts`)
  - CSS-in-JS configuration or Tailwind config
  - Component library with documented design patterns
- **Signal absent**:
  - Inline styles or scattered CSS files
  - Multiple conflicting color/spacing conventions
  - No documented design system or shared component library
- **Evidence marker**: Search for color definitions, spacing units, font sizes across codebase

---

## Tier 2 Signals: Moderate Evidence of UI Fog (Weight: Medium)

### 2.1 Low Test Coverage for UI Logic
**What to check**: Are UI interactions and flows tested? Or only backend logic?
- **Signal present**: Test files show
  - E2E tests for user flows (Cypress, Playwright, etc.)
  - Component tests for interactions
  - Accessibility tests (a11y)
- **Signal absent**:
  - Few or no tests for UI behavior
  - Tests only cover API/backend
  - No interaction or flow testing
- **Evidence marker**: Check `/test/`, `/tests/`, `__tests__/` directories; look for `*.spec.tsx` or E2E config

### 2.2 Accessibility Not Addressed
**What to check**: Are accessibility concerns documented? Or ignored?
- **Signal present**: Codebase shows
  - WCAG guidelines reference in code or docs
  - Accessibility testing tools mentioned
  - Semantic HTML and ARIA attributes used
- **Signal absent**:
  - No accessibility documentation
  - CSS-only interactions without semantic HTML
  - No alt text or aria labels
- **Evidence marker**: Search for `aria-`, `role=`, accessibility-related comments

### 2.3 Responsive Design Not Documented
**What to check**: Is the app designed for multiple screen sizes? Is it documented?
- **Signal present**: Codebase shows
  - Media queries or responsive design tokens
  - Mobile/tablet/desktop breakpoints defined
  - Responsive design mentioned in README or docs
- **Signal absent**:
  - Single fixed-width layout
  - No mention of mobile or responsive design
  - No breakpoints defined
- **Evidence marker**: Search for media queries, screen breakpoints, responsive design references

### 2.4 Screen/Page Count High Relative to Documentation
**What to check**: How many screens exist relative to how well they're documented?
- **Signal present**:
  - Documented/mapped screens match codebase screens
  - Each major screen has design spec or Figma reference
- **Signal absent**:
  - Many screens exist but few are documented
  - Screen count unclear from codebase
  - Documentation is outdated vs. current code
- **Evidence marker**: Count `.tsx` `.jsx` `.vue` files in `/pages/`, `/screens/`, `/views/` directories

---

## Tier 3 Signals: Supporting Evidence of UI Fog (Weight: Low)

### 3.1 Limited Component Reusability
**What to check**: Are similar UI elements reimplemented multiple times, or reused?
- **Signal present**:
  - Same component used across multiple screens
  - Button, Form, Modal implementations in shared location
- **Signal absent**:
  - Similar logic reimplemented in different files
  - High code duplication in UI layer
- **Evidence marker**: Search for duplicate component implementations

### 3.2 State Management Complexity in UI
**What to check**: Is client state management explicit? Or scattered in components?
- **Signal present**:
  - Centralized state management (Redux, Vuex, Pinia, etc.)
  - State architecture documented
- **Signal absent**:
  - State scattered across component tree
  - No clear state management strategy
- **Evidence marker**: Look for Redux store, Vuex modules, context files

### 3.3 User Feedback Loops Not Documented
**What to check**: Are error handling, loading states, success messages clear?
- **Signal present**:
  - Toast/notification system documented
  - Error handling strategy shown in code
  - Loading states explicitly handled
- **Signal absent**:
  - Inconsistent error messages
  - No feedback for async operations
  - Missing loading indicators
- **Evidence marker**: Search for error handling, toast/notification code patterns

---

## Fog Type Decision Tree

Use this tree when deciding if a repository has **UI Fog**:

```
Does the codebase have frontend/UI code? (React/Vue/Angular/HTML/CSS)
├─ NO → Not ui_fog; check other fog types (product, docs, architecture)
└─ YES → Continue...

Are user flows, screens, or interactions documented?
├─ YES (flows + screens documented; design system clear) → PROBABLY NOT ui_fog
│   └─ Check if the problem is product (user needs) or architecture (performance/coupling)
└─ NO (flows missing; screens undocumented; design scattered) → Continue...

Is the primary problem about "how the UI works" vs "what the UI should do"?
├─ "What it should do" (e.g., "we need a new feature") → product_fog, not ui_fog
└─ "How it works" (e.g., "screens are too complex; navigation is confusing") → ui_fog likely

Are multiple Tier 1 signals present? (flows missing, components scattered, routing unclear, design fragmented)
├─ 2+ Tier 1 signals → STRONG CONFIDENCE: ui_fog
├─ 1 Tier 1 signal + 2+ Tier 2 signals → MEDIUM CONFIDENCE: ui_fog
└─ Only Tier 3 signals → LOW CONFIDENCE: Probably not ui_fog

Result: Classify as ui_fog
```

---

## Verification Rules

1. **No vibe-based classification**: Every ui_fog diagnosis must cite at least one Tier 1 or two Tier 2 signals.
2. **Evidence grounding**: Cite file paths, line numbers, or directory structure as proof.
3. **Contrastive evidence**: Compare what the README claims about UI vs. what code shows.
4. **Distinguish from architecture_fog**: UI fog is about *screen/flow/component design*. Architecture fog is about *module structure/coupling/performance*. A codebase can have both.

---

## Examples

### Example 1: STRONG UI Fog Signal (High Confidence)
**Repository**: `SaaS dashboard app`
- ✅ `/src/pages/` has 15 screen files, but `/docs/` has no flow documentation
- ✅ `/src/components/` has no clear hierarchy; components scattered in `/pages/`
- ✅ Routing rules spread across 5 files; no central router
- **Diagnosis**: `ui_fog` (Tier 1.1, 1.2, 1.3)

### Example 2: WEAK UI Fog Signal (Low Confidence)
**Repository**: `API library with React examples`
- ✅ `/examples/` has React components but they're not the core product
- ✅ Main library is API focused; UI is secondary
- ❌ No indication that UI screens or flows are the primary problem
- **Diagnosis**: Probably `architecture_fog` or `product_fog`, not `ui_fog`

### Example 3: UI Fog + Architecture Fog (Both Present)
**Repository**: `E-commerce platform`
- ✅ Multiple screens poorly documented (ui_fog signal)
- ✅ State management is chaotic with props drilling (architecture_fog signal)
- **Diagnosis**: Primary fog type depends on "weakest boundary" — which is worse?
  - If screen/flow design is the blocking issue → `primary_fog_type: ui_fog`
  - If state coupling is blocking UI improvements → `primary_fog_type: architecture_fog`
  - Use user intent as tiebreaker if both are strong

---

## Related Documents
- [Weakness Types](weakness-types.md) — General weakness classification
- [Evidence Rules](evidence-rules.md) — Evidence grounding requirements
- [Repo Analysis Template](repo-analysis-template.md) — Output format requiring fog type classification
