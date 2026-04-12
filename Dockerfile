FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 10001 omni \
    && adduser --system --uid 10001 --ingroup omni omni

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir .

USER omni

EXPOSE 8080

ENTRYPOINT ["omni-mcp"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
