#!/bin/sh
set -euo pipefail
flask db upgrade
gunicorn --access-logfile - -b 0.0.0.0 wsgi