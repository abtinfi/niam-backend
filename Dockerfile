# Base image: استفاده از یک ایمیج رسمی پایتون
FROM python:3.10-slim-bullseye

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# نصب وابستگی‌های سیستمی مورد نیاز
# libpq5 برای psycopg2-binary و postgresql-client برای ابزار psql (اختیاری اما مفید)
RUN apt-get update \
    && apt-get install -y libpq5 postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ایجاد پوشه کاری
WORKDIR /app

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن اسکریپت entrypoint
COPY entrypoint.sh /app/entrypoint.sh
# دادن مجوز اجرا به اسکریپت entrypoint
RUN chmod +x /app/entrypoint.sh

# کپی کردن بقیه کدهای پروژه
COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]

# پورت پیش‌فرض
EXPOSE 8000

# دستور پیش‌فرض برای اجرای برنامه با Gunicorn
# core_project.wsgi باید با نام پوشه پروژه اصلی شما که حاوی wsgi.py است، مطابقت داشته باشد
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core_project.wsgi:application"]
