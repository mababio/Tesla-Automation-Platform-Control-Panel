FROM python:3.10-slim
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY util  util/
COPY custom custom/
COPY main.py ./
COPY requirement.txt ./
RUN pip install --no-cache-dir -r  requirement.txt
RUN pip install 'pymongo[srv]'
ENV PORT 8080
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
