# Base Image
FROM python:3.13-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Show Python logs immediately
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Install dependencies first (better build caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Gunicorn will listen on this port
EXPOSE 8000

# Start Zoothy
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]