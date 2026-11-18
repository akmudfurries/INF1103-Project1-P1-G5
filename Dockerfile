FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Singapore timezone
ENV TZ=Asia/Singapore

# Install application and testing dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Declare persistent storage location for SQLite
VOLUME ["/app/data"]

# Launch CLI application
CMD ["python", "main.py"]
