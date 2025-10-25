FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Expose Flask/Gunicorn port
EXPOSE 5000

# Security: use a non-root userls
RUN useradd -m appuser
USER appuser

# Environment variables
ENV FLASK_ENV=production
ENV PORT=5000

# Start the app using Gunicorn (recommended for production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]
