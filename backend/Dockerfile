FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN addgroup --system django && adduser --system --ingroup django django
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY backend ./backend
COPY backend/entrypoint.sh ./entrypoint.sh
RUN chmod 755 ./entrypoint.sh && chown -R django:django /app
USER django
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
