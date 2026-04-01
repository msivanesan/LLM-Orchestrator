# --- Stage 1: Build & Python Setup ---
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Run the worker process
# (This script manages the worker lifecycle and Redis consumption)
CMD ["python", "manage.py", "runworker"]
