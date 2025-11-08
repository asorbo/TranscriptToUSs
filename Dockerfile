# Use official Python 3.13 slim image
FROM python:3.13.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8123

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-k", "gevent", "-w", "1", "--worker-connections", "1000", "-b", "0.0.0.0:8123", "frontend:app"]

