FROM python:3.11-slim

# set working directory inside container
WORKDIR /app

# Install required dependencies (such as the Google GenAI)
RUN pip install --no-cache-dir google-genai pytest

COPY . .

# ensure the data directory exists so JSON persistence works out-of-the-box
RUN mkdir -p data

# default command to run your CLI application
CMD ["python", "main.py"]