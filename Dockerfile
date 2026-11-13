FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازها
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirror-pypi.runflare.com/simple -r requirements.txt

# کپی کردن کدهای پروژه
COPY . .

# پورت اجرا
EXPOSE 8000

# اجرای FastAPI با Uvicorn
CMD ["uvicorn", "ingestion.main:app", "--host", "0.0.0.0", "--port", "8000"]
