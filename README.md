# BackendTask1
Task - https://www.craft.do/s/n6OVYFVUpq0o6L

## ✅ Checked by mypy by GitHub Actions:
```shell
mypy app --strict
```

## Migrations:
```shell
alembic revision --autogenerate
alembic upgrade head
```

## Additional tasks:

⏱1. Tests

⏱2. CI (required GitLab, but I prefer portfolio here)
- ✅ MyPy
- ✅ Deepsource (https://deepsource.io/)
- ⏱ Unit-tests

✅ 5. Swagger (/docs/) and Redoc (/redoc/)

✅ 9. Handling incorrect external endpoint work

## Setup:

- Clone repo
```shell
git clone https://github.com/KrySeyt/BackendTask1.git
```

- Create venv
```shell
python -m venv BackendTask1
```

- Activate venv
```shell
BackendTask1/Scripts/activate
```

- Install dependencies
```shell
pip install -r -requirements.txt
```

- Run server
```shell
BACKENDTASK1_POSTGRESQL_URL=<POSTGRESQL_URL> uvicorn app.main:app
```

## Configuration (Environment vars)
    Varibles names case doesn't matter

- ### BACKENDTASK1_POSTGRESQL_URL
    Url to your postgresql database without driver

&ensp;&thinsp;&ensp;&thinsp;
✅
`
BACKENDTASK1_POSTGRESQL_URL='postgresql://scott:tiger@localhost:5432/mydatabase'
`

&ensp;&thinsp;&ensp;&thinsp;
❌
`
BACKENDTASK1_POSTGRESQL_URL='postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase'
`

- ### BACKENDTASK1_ENDPOINT_URL
  Any http/https url for post requests according to https://probe.fbrq.cloud/docs#/send/sendMsg doc

  #### Default = `None`
  ##### If value is `None`, messages will "sends" just to console

&ensp;&thinsp;&ensp;&thinsp;
`
BACKENDTASK1_ENDPOINT_URL='https://httpbin.org/post'
`

- ### BACKENDTASK1_SUCCESSFUL_STATUS_CODES
  list of status codes which will be considered as the result of a successful sending

  #### Default = [200]

&ensp;&thinsp;&ensp;&thinsp;
`
BACKENDTASK1_SUCCESSFUL_STATUS_CODES='["200", "418"]'
`

- ### BACKENDTASK1_MAX_REQUESTS_AT_TIME
  number of requests to external endpoint that can be processed at one time
  
  #### Default = 20

&ensp;&thinsp;&ensp;&thinsp;
`
BACKENDTASK1_MAX_REQUESTS_AT_TIME='50'
`
