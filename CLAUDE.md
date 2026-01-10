# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a League of Legends eSports calendar generator that creates .ical files from the LoL eSports API. The application consists of a Python Flask backend that serves API endpoints and a React frontend for user interaction.

## Development Commands

### Backend (Python)
- **Start PostgreSQL**: `docker compose up postgres -d`
- **Run migrations**: `DATABASE_URL=postgresql://lolcalendar:devpassword@localhost:5432/lolcalendar uv run alembic upgrade head`
- **Run tests**: `DATABASE_URL=postgresql://lolcalendar:devpassword@localhost:5432/lolcalendar uv run pytest tests.py`
- **Import data**: `DATABASE_URL=postgresql://lolcalendar:devpassword@localhost:5432/lolcalendar uv run python -m backend.api_parser`
- **Start Flask server**: `DATABASE_URL=postgresql://lolcalendar:devpassword@localhost:5432/lolcalendar uv run python -m flask --app backend run`

### Frontend (Vue)
Navigate to `frontend/` directory first:
- **Development server**: `npm run dev` (runs on localhost:5173, proxies to Flask on :5000)
- **Build for production**: `npm run build`
- **Preview production build**: `npm run preview`

### Dependencies
- **Python**: Uses `uv` for dependency management (see `pyproject.toml`)
- **Node.js**: Standard npm package management (see `frontend/package.json`)

## Architecture

### Backend Structure (`backend/`)
- **`api_parser.py`**: Handles data import from LoL eSports API using public API key. Contains functions for importing leagues and matches with pagination support.
- **`datastore.py`**: Database models using SQLAlchemy ORM with PostgreSQL. Defines `League` and `Match` models with calendar generation functionality.
- **`web.py`**: Flask API endpoints serving league data and generating .ical calendar files.
- **`migrations/`**: Alembic database migrations.
- **`__init__.py`**: Flask app initialization.

### Frontend Structure (`frontend/src/`)
- Vue 3 application using Composition API with `<script setup>` syntax
- Built with Vite for fast development and optimized builds
- Configured to proxy API requests to Flask backend (port 5000)
- Components: `App.vue` (main application) and `League.vue` (league selection cards)

### Database
- PostgreSQL database managed via SQLAlchemy ORM
- Alembic for database migrations
- Models: `League` (eSports leagues) and `Match` (individual matches)
- Database operations include caching with `@lru_cache` for performance
- Requires `DATABASE_URL` environment variable

### API Integration
- Uses LoL eSports public API (`prod-relapi.ewp.gg`) with public API key
- Imports league and match data with pagination support
- Generates iCalendar format for calendar applications

### Deployment
- GitHub Actions workflow for automated testing and deployment
- Deploys to DigitalOcean via SSH on master branch commits
- Docker containers for backend and frontend
- Run migrations manually before deploying: `uv run alembic upgrade head`
