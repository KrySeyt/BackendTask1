# BackendTask1 ![Mypy](https://github.com/KrySeyt/backendtask1/actions/workflows/mypy.yml/badge.svg)[![codecov](https://codecov.io/gh/KrySeyt/BackendTask1/branch/main/graph/badge.svg?token=V1H2036M7I)](https://codecov.io/gh/KrySeyt/BackendTask1)
*python 3.11.1*

Task - https://www.craft.do/s/n6OVYFVUpq0o6L

## Additional tasks:

✅ 1. Tests

✅ 2. CI (required GitLab, but I prefer portfolio here)
- ✅ Mypy (`--strict`)
- ✅ Deepsource (https://deepsource.io/)
- ✅ Tests

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
BACKENDTASK1_POSTGRESQL_URL=<POSTGRESQL_URL> uvicorn src.main:app
```

## Postgresql migrations:
Create database schema from `app/models.py`:
```shell
alembic revision --autogenerate
alembic upgrade head
```

## Configuration (Environment vars)
###  *Variables names case doesn't matter*

- ### BACKENDTASK1_POSTGRESQL_URL (*required*)
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

## Testing
  *All tests driving by <a href="https://github.com/pytest-dev/pytest">pytest</a>*

  Run tests my command:

  ```shell
  pytest tests/
  ```

  Tests with coverage report:

  ```shell
  pytest tests/ --cov=src
  ```

  Coverage report from `.coverage`:

  *`-m`: show missing lines*
  ```shell
  coverage report -m
  ```

### Some about testing process
For testing production `postgresql+asyncpg` database replacing with `sqlite3+aiosqlite`.\
On test session start, `pytest`'s fixture creates `test.sqlite3` file and delete on testing session end.
In the future may be added, switch to `postgresql+asyncpg` (like in production), 
that provides by <a href="https://github.com/eradman/ephemeralpg">pg_tmp</a> (*Linux only*)
