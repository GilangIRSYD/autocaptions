# Project Workflow Rules & Compliance

## Mandatory Checklist for Every Task

### 1. Planning & Context
- [ ] **Check Context7 First:** Before using or updating any library (Whisper, FFmpeg, Streamlit, etc.), use the `context7` MCP to verify the latest API syntax and best practices.
- [ ] **Brainstorming Gate:** For any new feature, follow the `@[/brainstorming]` workflow. Do not write code before the design is approved.

### 2. Implementation Standards
- [ ] **Versioning:** Every functional change or bug fix MUST be accompanied by a version bump in `app.py` (e.g., v1.3.0 -> v1.3.1).
- [ ] **Aesthetics:** All UI changes must adhere to premium design standards (Modern typography, HSL-based colors, subtle animations, and responsive layout).
- [ ] **CPU Optimization:** Since this project runs on a CPU-only homelab, always prefer libraries optimized for CPU (like `faster-whisper` with INT8 quantization).

### 3. Completion & Handoff
- [ ] **Git Synchronization:** Always `git add`, `git commit`, and `git push origin main` after completing a task.
- [ ] **Deployment Instructions:** At the end of every task, explicitly remind the user to:
    - Go to Portainer.
    - Click "Update the Stack".
    - Enable "Pull latest image".
- [ ] **Verification:** Confirm that the version number displayed in the UI matches the new version set in the code.

## Commit Message Convention
- `feat:` for new features (e.g., `feat: implement typewriter animation`)
- `fix:` for bug fixes (e.g., `fix: subtitle vertical position`)
- `perf:` for performance improvements (e.g., `perf: migrate to faster-whisper`)
- `chore:` for version bumps or maintenance
