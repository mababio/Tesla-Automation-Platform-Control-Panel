FROM python:3.10-slim
ENV APP_HOME /app
ENV PORT 8083
WORKDIR $APP_HOME
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/application_default_credentials.json
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/util"
COPY secret_manager.py .
COPY application_default_credentials.* ./
COPY src/  .
COPY src/config.py .
RUN python secret_manager.py download settings.toml tesla_setting_toml tesla-automation-397321
RUN python secret_manager.py download cache.json tesla_cred tesla-automation-397321
RUN python secret_manager.py download mqtt.crt mqtt_ca_crt tesla-automation-397321
RUN apt-get update && apt-get install vim  curl lsof -y
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app