FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY . /app

# Expose service port
EXPOSE 8080

ENV HOST=0.0.0.0
ENV PORT=8080

CMD ["python3", "server.py", "8080"]
