FROM arm64v8/python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Add net-tools because arp is needed to query connected access point devices
RUN apt update
RUN apt install net-tools

ENV PORT=80

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "${PORT}", "--host", "0.0.0.0"]