FROM python:3.10-slim

######create appuser and directory for app#########
RUN groupadd -g 999 appuser && \
    useradd -m -r -u 999 -g appuser appuser
USER appuser
ENV APP_HOME  /home/appuser/app
RUN mkdir /home/appuser/app
RUN chown appuser:appuser /home/appuser/app
###### Create appuser and directory for application#########


WORKDIR $APP_HOME
COPY src/ .
COPY application_default_credentials.json ./

###### Create Python Virutal evironment ###########
RUN python -m venv $APP_HOME
RUN . $APP_HOME/bin/activate && pip install -r requirements.txt
# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:$APP_HOME:$APP_HOME/util"
###### Create Python Virutal evironment ###########

ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_HOME/application_default_credentials.json

####### Application specfic varaibles ##########
ENV PORT 8083
#################### For folks who are not creating kubernetes secrets ####################
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
#################### For folks who are not creating kubernetes secrets ####################
####### Application specfic varaibles ##########

ENTRYPOINT . $APP_HOME/bin/activate && exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
