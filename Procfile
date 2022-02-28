web: gunicorn parrainage.project.wsgi -c gunicorn_config.py
postdeploy: python manage.py migrate && python manage.py create_initial_admin_user
