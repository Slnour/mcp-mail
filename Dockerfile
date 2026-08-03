FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

# Audit log of sent mail; mount a volume so it survives container replacement.
VOLUME ["/data"]
ENV DATA_DIR=/data

EXPOSE 8000

CMD ["mail-mcp"]
