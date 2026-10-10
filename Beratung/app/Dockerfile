FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_DB=/daten/beratung.sqlite
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 app && mkdir /daten && chown app /daten
COPY server ./server
COPY web ./web
USER app
EXPOSE 8000
# --no-access-log: keine Zugriffsprotokolle mit IP-Adressen. forwarded-allow-ips: nur das interne Docker-Netz (Caddy).
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--proxy-headers", "--forwarded-allow-ips", "172.16.0.0/12"]
