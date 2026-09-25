FROM python:3.12.14-alpine3.23@sha256:d339953547bb5bc57eb5c1ff3224c40890ce56e494b13a52a574658e5a0f888a AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md ./
COPY app ./app
RUN python -m pip install --prefix=/install .

FROM python:3.12.14-alpine3.23@sha256:d339953547bb5bc57eb5c1ff3224c40890ce56e494b13a52a574658e5a0f888a

ENV APP_MODE=offline_demo \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup -S app && adduser -S -G app -h /app app
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=app:app app ./app
LABEL "tee.launch_policy.allow_cmd_override"="true" \
      "tee.launch_policy.allow_env_override"="WIF_AUDIENCE,PROTECTED_SECRET_RESOURCE,PROTECTED_SECRET_EXPECTED_SHA256" \
      "tee.launch_policy.log_redirect"="always"
USER app
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]
