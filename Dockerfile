# Use Python 3.12 as the base image
FROM python:3.12-slim

WORKDIR /app

# Install FFmpeg and other system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Streamlit will run on
EXPOSE 8501

CMD streamlit run src/report_generator.py --server.port=${PORT:-8501} --server.address=0.0.0.0