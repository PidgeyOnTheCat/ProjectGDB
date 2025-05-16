# Use Python 3.9 slim as the base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy your requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code
COPY . .

# Set environment variable (optional for cleaner logs)
ENV PYTHONUNBUFFERED=1

# Command to run your bot
CMD ["python", "main.py"]
