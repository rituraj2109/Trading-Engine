FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Create a non-root user for safety
RUN addgroup --system app && adduser --system --ingroup app app || true

# Grant permissions to the app user
RUN chown -R app:app /app

USER app

EXPOSE 5000

# Use web_dashboard.py for the backend API
CMD ["python", "web_dashboard.py"]
