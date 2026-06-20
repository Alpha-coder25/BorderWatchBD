release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn borderwatch.wsgi --log-file -
