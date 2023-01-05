# BackendTask1
Task - https://www.craft.do/s/n6OVYFVUpq0o6L

### ✅ Checked by mypy by GitHub Actions:
```shell
mypy app --strict
```

### Migrations:
```shell
alembic revision --autogenerate
alembic upgrade head
```

### Additional tasks:

⏱1. Tests

⏱2. CI (required GitLab, but I prefer portfolio here)
- ✅ MyPy
- ⏱ Unit-tests

✅ 5. Swagger (/docs/) and Redoc (/redoc/)

✅ 9. Handling incorrect external endpoint work

### Setup:

Clone repo
```shell
git clone https://github.com/KrySeyt/BackendTask1.git
```

Create venv
```shell
python -m venv BackendTask1
```

Activate venv
```shell
BackendTask1/Scripts/activate
```

Install dependencies
```shell
pip install -r -requirements.txt
```

Run server
```shell
uvicorn app.main:app
```

### Configuration

#### External endpoint

By default app "sends" messages just to console (`EXTERNAL_ENDPOINT = None`), to choose your endpoint open `main.py` and set EXTERNAL_ENDPOINT to your endpoint

`
EXTERNAL_ENDPOINT: str | None = r"https://httpbin.org/post"
`

#### Postgresql

Set environment variable `BackendTask1HerokuPostgresURL` with Heroku or another url to postresql database

##### Renaming environment variable:
`
app/database.py:
`

`
DATABASE_POSTGRESQL_ENV_VAR_NAME: str = "AnyNameForYourPostgresqlURLEnvVar"
`

#### Endpoint successful response codes

By default:
- 200

##### Setup your own successful status codes set

`
app/sending.py:
`

`
SUCCESSFUL_RESPONSE_CODES: set[int] = set(status.HTTP_200_OK, status.HTTP_418_IM_A_TEAPOT)
`