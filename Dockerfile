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
EXPOSE 8080

# Run the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "frontend:app", "--workers", "1", "--threads", "1"]
