# platform=linux/amd64
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
    UID=1000 \
    GID=1000

ENV APP_ENV=${APP_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore \
    POETRY_VERSION=2.1.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/var/cache/pypoetry \
    POETRY_HOME=/usr/local \
    POETRY_INSTALLER_PARALLEL=false

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash \
        build-essential \
        curl \
        git \
    && curl -sSL https://install.python-poetry.org | python - \
    && poetry --version \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app-root

COPY ./poetry.lock ./pyproject.toml /opt/app-root/
COPY ./src /opt/app-root/src
COPY ./README.md /opt/app-root/
COPY ./run.sh /opt/app-root/

RUN --mount=type=cache,target="${POETRY_CACHE_DIR}" \
    poetry run pip install -U pip \
    && poetry install --only main --no-interaction --no-ansi \
    && chmod 755 /opt/app-root/run.sh

USER 1001

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

CMD ["./run.sh"]
