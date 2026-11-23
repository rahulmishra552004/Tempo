FROM python:3.12-slim

# Copy the uv binary from its official image (same version as local)
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Layer 1: dependencies only (cached until pyproject.toml or uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Layer 2: project code
COPY . .
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "tempo.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
