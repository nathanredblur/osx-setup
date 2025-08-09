# Mac Setup Store (Astro + React + Tailwind)

This web app simulates an “app store” for building a personalized macOS setup, inspired by the attached UI. All UI is in English.

## Tech

- Astro (TypeScript) with React islands
- Tailwind CSS, Lucide icons
- Client search: Fuse.js
- State: Zustand (persisted to `localStorage`)
- File export: File System Access API with blob fallback

## Commands

- `pnpm install`
- `pnpm dev` – start dev server
- `pnpm build` – production build
- `pnpm preview` – preview build

## Project Plan Checklist

- [x] Initialize Astro project and Tailwind
- [x] Enable React islands
- [x] Create base layout with styles
- [x] Sidebar with Apps/Tweeks/Settings
- [x] Pages: `/`, `/tweeks`, `/settings`
- [x] Summary panel skeleton with CTA “create setup”
- [x] Filters bar skeleton (search, category, tag, toggles)
- [x] App grid and basic `AppCard`
- [x] Local stores scaffolding (selection, filters)
- [x] Utilities: fuzzy search, file export, validators, bundle/script generators (initial)
- [ ] Wire real data from `src/assets/data/*.json`
- [ ] Implement fuzzy search and filters with Zustand state
- [ ] Persist selection and filters to `localStorage`
- [ ] App detail Drawer/Modal
- [ ] Summary stats (by type, paid, with settings)
- [ ] Generator: create setup (brew bundle + scripts)
- [ ] Toast/notifications
- [ ] Settings page (theme, defaults, cache, reload catalog)
- [ ] Tweeks page toggles connected to state
- [ ] Polished UI and accessibility

## Data

Local JSON catalog lives at `src/assets/data/`.

## Structure

Key directories:

- `src/react/*` – React components (Sidebar, Apps view, Filters, Summary, Cards)
- `src/stores/*` – Zustand stores
- `src/lib/*` – utilities (fuzzy, file, validators, bundle, script)
- `src/pages/*` – Astro pages
- `public/icons/*` – fallback icons
