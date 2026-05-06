# platform=linux/amd64
FROM python:3.12-bullseye

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

USER root

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root
WORKDIR /opt/app-root

RUN pip install --upgrade pip
COPY . .

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

USER 1001

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

CMD [ "/opt/app-root/run.sh" ]
