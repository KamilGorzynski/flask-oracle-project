# Flask-Oracle-Project

## Stack:
- Python
- Flask
- Oracle
- Docker

## Requirements:
- docker-compose
- curl

## Installation:
I. Clone the project:
```
git clone https://github.com/KamilGorzynski/flask-oracle-project.git
```

II. Create .env.local file and fill up with example variables:
```
ORACLE_SID=ORCLCDB
ORACLE_PDB=ORCLPDB1
ORACLE_USR=system
ORACLE_PWD=oracle
ORACLE_ALLOW_REMOTE=true
SQLALCHEMY_DATABASE_URI=oracle+cx_oracle://system:oracle@db:1521/?service_name=xe
```

III. Run app:
```
make run
```

IV. Create objects in db:
```
make feed
```

## Testing:
I. Users list:
```
curl --location 'http://localhost:5000/users'
```

II. Create user with access:
```
curl --location 'http://localhost:5000/create_user' \
--header 'Content-Type: application/json' \
--data '{
    "resource": "5",
    "name": "O",
    "surname": "P"
    }'
```

III. Change rersource for specific user:
```
curl --location --request PATCH 'http://localhost:5000/change_resource/3' \
--header 'Content-Type: application/json' \
--data '{"resource": "24"}'
```

IV. All changes history list:
```
curl --location 'http://localhost:5000/history' \
--header 'Content-Type: application/json'
```

V. Changes history for specific user:
```
curl --location 'http://localhost:5000/history?user_id=3' \
--header 'Content-Type: application/json'
```

## TO DO:
- add pytest unit tests