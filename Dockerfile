FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install OS dependencies (ffmpeg)
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run bot
CMD ["python", "-u", "main.py"]
