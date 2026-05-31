FROM python:3.13-slim

WORKDIR /app

COPY pykhinsider/ ./pykhinsider/
RUN pip install ./pykhinsider

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY frontend/build/ ./frontend/build/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]