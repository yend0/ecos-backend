#!/bin/bash
uv run uvicorn ecos_backend.app:create_app --reload --factory --host localhost --workers 1 --port 8000