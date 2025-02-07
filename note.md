# install database url
> pip install dj-database-url
-- dj_database_url.parse("")

2. post gre driver install 
pip install psycopg2-binary 

-- migrate database

3. setup setting file and environments 
4. create requirements file 
5. pip install gunicorn (to run wsgi)

6. serving static files using whitenoise 
-- pip install whitenoise
-- setup staticfiles on setting.py 

7. 'django.contrib.sessions.middleware.SessionMiddleware', # whitenoise middleware  
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

run --> python manage.py collectstatic


8. create separate envirionment file
-- pip install python-decouple
import dj_database_url
from decouple import config, Csv
<!-- for host  -->
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
<!-- # DEBUG = True -->
DEBUG = config('DEBUG', default=False, cast=bool)

<!-- # Database -->
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}