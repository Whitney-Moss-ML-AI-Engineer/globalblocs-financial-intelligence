# GlobalBLOCS Desktop Application

## Target
Cross-platform desktop client for Windows, macOS, and Linux.

## Framework
Tauri 2 is the recommended desktop shell so the existing dashboard frontend can be reused.

## Modes
- Cloud API: hosted GlobalBLOCS
- Local API: http://127.0.0.1:8000
- Enterprise: organization-managed API endpoint

## First-run installer responsibilities
1. Install the desktop client.
2. Start the first-run wizard.
3. Detect OS and architecture.
4. Test API connectivity.
5. Configure API endpoint.
6. Configure authentication.
7. Optionally validate Docker for local mode.
8. Store non-secret preferences locally.
9. Never embed database passwords in the application bundle.

A later release can package FastAPI as a signed sidecar for fully local desktop operation.
