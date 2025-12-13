FROM python:3.12-slim

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# in a machine where the image will be installed:
#   - create /the_news_hub folder
#   - cd /the_news_hub
WORKDIR /the_news_hub

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    fonts-unifont \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# copy and install dependencies (already cached if code changes)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

RUN /the_news_hub/.venv/bin/playwright install chromium

# copy and install source code (install source code a package)
COPY config.py .
COPY src ./src
COPY scripts ./scripts
COPY templates ./templates
RUN uv sync --frozen --no-dev

# "activate" .venv in remote machine
ENV PATH="/the_news_hub/.venv/bin:$PATH"
