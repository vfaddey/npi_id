FROM python:3.10.4-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generate_keys.py .
CMD ["python3", "generate_keys.py"]

COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --reload --port 0.0.0.0 --host 8000"]