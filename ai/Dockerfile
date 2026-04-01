# --- Stage 1: Build & Python Setup ---
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install Python dependencies first (for faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Expose the service port
EXPOSE 5003

# Run the production server via manage.py
# (This starts Gunicorn automatically)
CMD ["python", "manage.py", "runprod"]
