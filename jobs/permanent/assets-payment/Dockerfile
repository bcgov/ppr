FROM python:3.12-bullseye AS development_build

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

USER root

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root

ARG APP_ENV \
  # Needed for fixing permissions of files created by Docker:
  UID=1000 \
  GID=1000

ENV APP_ENV=${APP_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  # poetry:
  POETRY_VERSION=1.8.3 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    wait-for-it \
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app-root

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml /opt/app-root/

COPY ./src /opt/app-root/src
COPY ./README.md /opt/app-root

# Project initialization:
RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
  echo "$APP_ENV" \
  && poetry version \
  # Install deps:
  && poetry run pip install -U pip \
  && poetry install \
    $(if [ -z ${APP_ENV+x} ] | [ "$APP_ENV" = 'production' ]; then echo '--only main'; fi) \
    --no-interaction --no-ansi

USER 1001

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

CMD [ "python", "-m", "assets_payment" ]
