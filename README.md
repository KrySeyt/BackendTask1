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