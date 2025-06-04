#!/bin/sh

# منتظر می‌مانیم تا سرویس PostgreSQL آماده پاسخگویی شود
echo "Waiting for PostgreSQL to start..."
# از متغیرهای محیطی که توسط docker-compose از .env خوانده شده‌اند استفاده می‌کنیم
# PGPASSWORD برای psql نیاز است تا بدون درخواست تعاملی پسورد کار کند
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "PostgreSQL started successfully!"

# اجرای مایگریشن‌های جنگو
echo "Applying database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# جمع‌آوری فایل‌های استاتیک
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear # --clear برای پاک کردن قبلی‌ها قبل از کپی

# ... (بخش ایجاد سوپریوزر اختیاری) ...

# اجرای دستوری که به عنوان CMD به اسکریپت پاس داده شده
exec "$@"