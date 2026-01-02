#!/usr/bin/env bash
cd "$(dirname "$0")"
# load .env into environment
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
exec /usr/bin/env python3 vy.py >> ./email_agent.log 2>&1
