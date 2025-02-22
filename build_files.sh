#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Collect static files (if using Django)
python manage.py collectstatic --noinput

# Run migrations (if using Django)
python manage.py migrate