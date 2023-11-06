pip freeze > requirements.txt
chmod +x ./entrypoint.sh
http://localhost:8001/
docker-compose up -d --build
docker exec -it django /bin/sh
python manage.py collectstatic
python manage.py tailwind start