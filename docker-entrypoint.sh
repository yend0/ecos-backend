#!/bin/bash
uv run uvicorn ecos_backend.main:create_app --reload --factory --host 0.0.0.0 --workers 1 --port 8000