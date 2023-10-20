FROM python:3.10-slim
# Copy local code to the container image.
ENV APP_HOME /app
ENV PORT 8080
WORKDIR $APP_HOME
COPY util util/
COPY config.py ./
COPY main.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r  requirements.txt
RUN pip install 'pymongo[srv]'

# Option 1: locally load settings.toml file to run locally. Make sure to add this file to .gitignore
COPY settings.* ./

# Option 2: Save settings.toml to GCP Secret Manager. This approach allows for your repo to be clear of sensitive data
# Review load_settings_toml.py for instruction
#COPY application_default_credentials.* ./
#ENV GOOGLE_APPLICATION_CREDENTIALS=/app/application_default_credentials.json
#COPY load_settings_toml.py ./
#RUN python load_settings_toml.py



# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
