ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim AS base

# Set environment variables to prevent Python from writing .pyc files and to disable buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set environment variable to prevent Poetry from creating virtual environments
ENV POETRY_VIRTUALENVS_CREATE=false

# Set the working directory inside the container to /app
WORKDIR /app

# Define an argument for the user ID, defaulting to 10001
ARG UID=10001

# Create a non-login user with the specified UID
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy the Poetry configuration files to the working directory
COPY pyproject.toml poetry.lock* ./

# Install Poetry and use it to install dependencies, excluding dev dependencies
RUN pip install --no-cache-dir poetry && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy the entire application code into the container
COPY . .

# Change ownership of the /app directory to the appuser
RUN chown -R appuser:appuser /app

# Switch to the appuser created earlier
USER appuser

# Set the default command to run the application
CMD ["python", "-m", "desktop_dispatcher.main"]
