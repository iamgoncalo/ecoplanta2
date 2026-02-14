# Frontend Premium Agent

## Role
Builds Apple-like UI shell with routing, shadcn components, charts, and API client.

## Scope
- React + TypeScript + Vite application
- Tailwind CSS + shadcn/ui for premium, minimal design
- 6 navbar modules: Fabric, Frameworks, Sales, Intelligence, Deploy, Partners
- OpenAPI-generated typed API client (no hardcoded data)
- Connectivity Sentinel: visible backend health indicator
- Responsive layout, consistent design system
- Charts and data tables for module pages

## Design Principles
- Apple-like: minimal, premium, fast, consistent
- No fake JS data - all data from backend APIs
- Loading states, error states, empty states handled
- Accessible (WCAG 2.1 AA minimum)

## DoD Checklist
- [ ] All 6 navbar items route correctly
- [ ] Each page fetches and renders real API data
- [ ] Connectivity Sentinel shows backend health
- [ ] Premium visual quality (spacing, typography, colors)
- [ ] No console errors in browser
- [ ] Frontend lint passes
- [ ] TypeScript strict mode passes
