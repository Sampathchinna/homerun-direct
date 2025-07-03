# Use Python 3.13 as base image
FROM python:3.13

# Set working directory inside the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy Django project files
COPY . .

# Expose port 8000 for Django app
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "homerun.wsgi:application", "--bind", "0.0.0.0:8000"]
