FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app

# Install dependencies only if requirements.txt is present
RUN if [ -f /app/requirements.txt ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

# Create a non-root user for safety
RUN addgroup --system app && adduser --system --ingroup app app || true

# Grant permissions to the app user
RUN chown -R app:app /app

USER app

CMD ["python", "main.py"]
