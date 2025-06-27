# Fabric Expo Management System

## Celery  

1. Start redis server
   > sudo service redis-server start
2. Start celery server  
    > celery -A fabric_expo_management_system worker --pool=solo -l info
    celery -A fabric_expo_management_system worker --loglevel=info
3. Start django server  
    > python manage.py runserver  
4. 