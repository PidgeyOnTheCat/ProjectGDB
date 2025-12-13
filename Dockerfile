FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose for any network use (optional)
EXPOSE 8080

# Run bot
CMD ["python", "main.py"]