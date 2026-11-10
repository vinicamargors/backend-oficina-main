FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY core core
COPY modules modules
COPY main.py .

RUN useradd --system --uid 10001 app
USER app
EXPOSE 8000

# Atrás do Caddy (rede interna do compose): confia no X-Forwarded-* dele.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
