python3 -m flask db upgrade
python3 -m flask seed
python3 -m gunicorn --chdir=/home/site/wwwroot app:app
