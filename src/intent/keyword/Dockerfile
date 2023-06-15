FROM python:3.11-slim-bullseye as base

ENV PYTHONIOENCODING=utf-8


RUN useradd -u 1999 --create-home --shell /bin/bash toni


FROM base as builder

RUN apt-get update && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y  apt-utils && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/toni
RUN mkdir -p /home/toni/config
RUN python -m venv env

ARG PIP_TRUSTED_HOST="pypi.gate.lan"
#ARG PIP_INDEX_URL="http://pypi.gate.lan/root/prod"
ARG PIP_INDEX_URL="http://pypi.gate.lan/root/rc"
ARG BUILD_ALEXANDER_VERSION=""
ENV PIP_DEFAULT_TIMEOUT=180

RUN env/bin/pip install --disable-pip-version-check --no-cache-dir -U "alexander_fw${BUILD_ALEXANDER_VERSION}"

ARG service_config="config/intent_keyword.yml"

COPY ${service_config} ./config/config.yml
COPY ./src/intent/keyword/run.py ./



FROM base

LABEL maintainer="Florian Jung <jungflor@gmail.com>"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8

# Install necessary system packages
RUN apt-get update && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y  apt-utils && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    dumb-init \
    curl htop tree less vim curl wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /home/toni /home/toni

WORKDIR /home/toni
RUN chown -R 1999 /home/toni

USER toni

ARG log_level="info"
ARG build_version="UNSET"
ENV SETA_LOG_LEVEL=${log_level}
ENV BUILD_VERSION=${build_version}

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/home/toni/env/bin/python", "run.py", "--config", "config/config.yml"]
