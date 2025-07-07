#!/bin/bash
PROJECT_DIR="/Users/ivan/Workspace/mcp-projects/pnda-mcp"
VENV_PATH="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/etl/logs/etl.log"

cd "$PROJECT_DIR"
echo "Starting ETL at $(date)" >> "$LOG_FILE"
source "$VENV_PATH/bin/activate"
echo "Python path: $(which python)" >> "$LOG_FILE"
export PYTHONPATH="$PROJECT_DIR"
"$VENV_PATH/bin/python" etl/pipeline.py