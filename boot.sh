#!/bin/bash
source .venv/bin/activate

python manage.py deploy
if [[ "$?" == "0" ]]; then
    break
fi

exec gunicorn -b 0.0.0.0:5000 --log-level=info --worker-class gevent --workers 4 patched:app