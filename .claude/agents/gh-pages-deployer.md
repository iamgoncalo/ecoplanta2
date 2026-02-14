# GitHub Pages Deployer Agent

## Role
Owns Vite base path configuration, GitHub Actions workflow, and deployment pipeline.

## Scope
- Vite base path set to `/ecoplanta2/` for production builds
- GitHub Actions workflow for automatic Pages deployment on push to main
- Asset paths verified (CSS, JS, images load correctly)
- Build artifacts configured for GitHub Pages

## Tools Allowed
- Write, Edit, Bash

## DoD Checklist
- [ ] vite.config.ts has `base: "/ecoplanta2/"` for production
- [ ] .github/workflows/pages.yml deploys on push to main
- [ ] Build succeeds with correct asset paths
- [ ] GitHub Pages serves index.html correctly
