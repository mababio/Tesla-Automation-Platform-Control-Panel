FROM python:3.10-slim
ENV APP_HOME /app
ENV PORT 8083

#ENV TESLA_LONG_TERM_JOB <VALUE>
#ENV MQTT_USER <VALUE>
#ENV MQTT_PASSWORD <VALUE>
#ENV TESLA_USERNAME <VALUE>
#ENV MQ_USER <VALUE>
#ENV MQ_PASSWORD <VALUE>
#ENV GMAPS_KEY <VALUE>
#ENV GARAGE_OPEN_LIMIT <VALUE>
#ENV CONFIRMATION_LIMIT <VALUE>
#ENV TESLA_DATA_SERVICES_BASE_URL <VALUE>
#ENV TESLA_LOCATION_SERVICES_BASE_URL <VALUE>
#ENV TESLA_CONTROL_SERVICES_BASE_URL <VALUE>
#ENV HOME_STREET <VALUE>

WORKDIR $APP_HOME
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/application_default_credentials.json
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/util"
COPY application_default_credentials.* ./
COPY src/  .
RUN apt-get update && apt-get install vim  curl lsof -y
#CMD echo $CACHE_TESLA_JSON > cache.json; exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
