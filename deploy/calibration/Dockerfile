# D-19 calibration runtime (prereg §13 rev 7g item 6; FE-4).
# The image holds the whole userland the engine's bits depend on: libc and
# libm, Python, NumPy and its bundled OpenBLAS. Nothing in it is updated
# during a run. The engine code is NOT in the image: the launcher mounts
# its own pinned checkout read-only at /app, and the start gate hashes it.
# The run is gated by the built image's id, which `d19.sh` reads with
# `docker image inspect` on the host (never typed).
#
# Base: the official python:3.14-slim, pinned by its multi-arch index digest
# (Docker Hub, read 2026-10-11).
FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

# git: the definition recorder compares the checkout with its commit
# (read-only commands only).
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory /app

COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --no-compile --require-hashes --only-binary :all: \
        -r /tmp/requirements.lock \
    && rm /tmp/requirements.lock

# The engine never runs as root; uid 990 owns /var/lib/aqt-d19 on the host.
RUN useradd --system --uid 990 --no-create-home --shell /usr/sbin/nologin d19
USER d19
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
