# Dockerfile builds your FastAPI app into a container image

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /the_news_hub

# Copy uv project files from root
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
RUN uv sync

# Copy the entire project unless .dockerignore  # TODO: Optimize this later
COPY . .

# Add the project root to PYTHONPATH so imports work correctly
ENV PYTHONPATH=/the_news_hub

# Expose port 7010
EXPOSE 7010

# Run the application using uv
WORKDIR /the_news_hub
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7010"]