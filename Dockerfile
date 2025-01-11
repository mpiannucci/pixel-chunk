FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "pixel_chunk/app.py", "--port", "8080", "--host", "0.0.0.0"]
