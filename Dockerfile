# Use the official Python image as a base
FROM python:3.12-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*


# Copy requirements.txt first for better caching of dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# COPY . /app/
COPY . .
COPY start.sh /start.sh


RUN chmod +x /start.sh

EXPOSE 8000


# Run shell script that waits for DB, applies migrations, seeds data, then starts FastAPI
CMD ["/start.sh"]
# Expose the default FastAPI port

# Command to run the FastAPI application
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]