FROM python:3.10

USER root
# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True
ENV DEBIAN_FRONTEND=noninteractive

# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN pip install .

USER 1001
# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
CMD exec python3 -m document_generation_service
