# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for WeasyPrint (Cairo, Pango, etc.)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json first for better caching
COPY package.json package-lock.json* ./
RUN npm install

# Create static directories before building
RUN mkdir -p static/css static/js static/fonts

# Copy project files
COPY . .

# Build static assets (copy Bootstrap files to static directories)
RUN npm run build

# Collect Django static files
RUN python manage.py collectstatic --noinput --clear

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]