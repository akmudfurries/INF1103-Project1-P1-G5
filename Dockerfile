FROM python:3.11-slim

# set working directory inside container
WORKDIR /app

# Container timezone (the app also sets Singapore time explicitly in config.py)
ENV TZ=Asia/Singapore

# Install required dependencies (such as the Google GenAI)
# tzdata is needed for ZoneInfo("Asia/Singapore") in the slim image
RUN pip install --no-cache-dir google-genai pytest tzdata

COPY . .

# ensure the data directory exists so JSON persistence works out-of-the-box
RUN mkdir -p data

# default command to run your CLI application
CMD ["python", "main.py"]