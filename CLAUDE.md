# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a League of Legends eSports calendar generator that creates .ical files from the LoL eSports API. The application consists of a Python Flask backend that serves API endpoints and a React frontend for user interaction.

## Development Commands

### Backend (Python)
- **Run tests**: `python -m pytest tests.py`
- **Import data**: `python backend/api_parser.py` (imports leagues and matches from LoL API)
- **Start Flask server**: `python -m flask --app backend run` (development server)

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
- **`datastore.py`**: Database models using Peewee ORM with SQLite. Defines `League` and `Match` models with calendar generation functionality.
- **`web.py`**: Flask API endpoints serving league data and generating .ical calendar files.
- **`__init__.py`**: Flask app initialization.

### Frontend Structure (`frontend/src/`)
- Vue 3 application using Composition API with `<script setup>` syntax
- Built with Vite for fast development and optimized builds
- Configured to proxy API requests to Flask backend (port 5000)
- Components: `App.vue` (main application) and `League.vue` (league selection cards)

### Database
- SQLite database (`datastore.db`) managed via Peewee ORM
- Models: `League` (eSports leagues) and `Match` (individual matches)
- Database operations include caching with `@lru_cache` for performance

### API Integration
- Uses LoL eSports public API (`prod-relapi.ewp.gg`) with public API key
- Imports league and match data with pagination support
- Generates iCalendar format for calendar applications

### Configuration
- Database file name configured in `app_config.py`
- Sample config provided in `app_config.sample.py`

### Deployment
- CircleCI configuration for automated testing and deployment
- Deploys to production server via SSH on master branch commits
- Frontend build process integrated into deployment pipeline