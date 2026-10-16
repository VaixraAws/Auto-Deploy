#!/bin/bash
cd "$HOME/auto-deploy/portal"
set -a; source .env; set +a
exec venv/bin/python app.py
