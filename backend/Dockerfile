FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ARG INSTALL_AI=0
RUN if [ "$INSTALL_AI" = "1" ]; then apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 build-essential && pip install --no-cache-dir -r requirements-ai.txt; fi
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
# ONE worker on purpose: door state, lockout counters and the vector cache live in memory.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed && gunicorn smartdoor.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 8 --timeout 120"]
