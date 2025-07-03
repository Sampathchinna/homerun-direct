## SQLITE MODE
### Remove db.sqlite3 if need to from fresh

enviroment variable create command
`$ python3 -m venv venv`

enviroment variable activate command
`$ source ./venv/bin/activate`

`$ cp bak.env .env`

# Ensure in .env postgres config updated 
PG_DB_NAME=hr
PG_USER=postgres
PG_PASSWORD=admin123
PG_HOST=localhost
PG_PORT=5432

`$ python3 -m pip install -r requirements.txt`
`$ python3 manage.py makemigrations`

Docker File
`$ docker-compose -f docker-compose-sqlite3.yaml up `


`$ python3 manage.py migrate`
`$ python3 manage.py initiate_master_data`
`$ python manage.py shell < scripts/reindex_all.py`
`$ python3 manage.py runserver`

frontend login details
 > email: nishu.saxena@gmail.com username: nishu password: nishu
 > python3 manage.py createsuperuser # For new Superuser

dump.sql import command
`$ psql -h localhost -p 5432 -U postgres -d homerun -f "/Users/ukbit5/Desktop/homerun/nish/dump.sql"`


## In postman import

## Collection : postman/environment.json

## Environment : postman/collection.json

pytest --ds=homerun.settings --cov=backend --cov=core --cov=master --cov=organization --cov=rbac --cov-report=term-missing --cov-config=.coveragerc


python3 manage.py test


