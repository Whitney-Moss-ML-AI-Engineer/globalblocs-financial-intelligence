# GlobalBLOCS Mobile Application

## Target
iOS and Android.

## Framework
Expo + React Native is the recommended mobile implementation.

## Architecture
iOS/Android -> GlobalBLOCS Mobile UI -> HTTPS Authentication -> FastAPI /api/v1 -> PostgreSQL + Gold Layer + Analytics

The phone is a client, not the database or ETL server.

## Development
Use the Expo development workflow and point the app at a development or staging API.

## Production
Use separate development, staging, and production API endpoints. Production builds must use HTTPS and signed application releases.
