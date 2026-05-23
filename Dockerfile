FROM python:3.11-slim

WORKDIR /app

# Install only what's needed for `pip install -e .` to resolve.
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --no-cache-dir -e .

# Run as a non-root user.
RUN useradd --create-home --shell /bin/bash curius && chown -R curius:curius /app
USER curius

ENTRYPOINT ["curius"]
