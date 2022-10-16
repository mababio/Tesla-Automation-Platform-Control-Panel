#!/bin/sh
project_number=$(grep PROJECT_NUMBER .env| cut -d '=' -f 2)
python load_settings.py upload "$project_number"

