FROM python:3.12-slim

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# in a machine where the image will be installed:
#   - create /the_news_hub folder
#   - cd /the_news_hub
WORKDIR /the_news_hub

# copy and install dependencies (already cached if code changes)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# copy and install source code (install source code a package)
COPY config.py .
COPY src ./src
COPY scripts ./scripts
COPY templates ./templates
RUN uv sync --frozen --no-dev

# "activate" .venv in remote machine
ENV PATH="/the_news_hub/.venv/bin:$PATH"
