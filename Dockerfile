FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Create a non-root user for safety
RUN addgroup --system app && adduser --system --ingroup app app || true
USER app

CMD ["python", "main.py"]
