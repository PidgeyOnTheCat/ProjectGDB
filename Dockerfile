FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run bot
CMD ["python", "main.py"]