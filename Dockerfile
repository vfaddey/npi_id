FROM python:3.10.4-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generate_keys.py .
CMD ["python3 generate_keys.py"]

COPY . .
EXPOSE 8000
CMD ["alembic upgrade head"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]