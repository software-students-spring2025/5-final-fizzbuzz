FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]