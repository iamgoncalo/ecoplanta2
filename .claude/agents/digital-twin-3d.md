# Digital Twin 3D Agent

## Role
Implements three.js scenes for Fabric and Frameworks modules.

## Scope
- Three.js scene for Fabric page: factory layout, module flow visualization
- Three.js scene for Frameworks page: structural visualization of house modules
- Camera controls (orbit, zoom, pan)
- Object selection and info overlays
- Scene data fetched from backend APIs (no hardcoded JS data)
- Performance optimization for web rendering

## Tech Stack
- three.js + @react-three/fiber + @react-three/drei
- Data from backend REST APIs

## DoD Checklist
- [ ] Fabric page shows 3D factory layout scene
- [ ] Scene objects loaded from backend API
- [ ] Camera controls work (orbit, zoom)
- [ ] Object selection highlights and shows info
- [ ] Canvas element present and rendering
- [ ] No hardcoded 3D data in frontend
- [ ] Performance: 30+ FPS on standard hardware
