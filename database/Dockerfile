FROM python:3.9-slim

WORKDIR /database

COPY requirements.txt .
RUN pip install pymongo python-dotenv

COPY . .

CMD ["python", "init_db.py"]