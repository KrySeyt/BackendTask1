# BackendTask1 ![CI](https://github.com/KrySeyt/backendtask1/actions/workflows/ci.yml/badge.svg)[![codecov](https://codecov.io/gh/KrySeyt/BackendTask1/branch/main/graph/badge.svg?token=V1H2036M7I)](https://codecov.io/gh/KrySeyt/BackendTask1)
*python 3.11.1*

Task - https://www.craft.do/s/n6OVYFVUpq0o6L

## Additional tasks:

✅ 1. Tests

✅ 2. Auto building and tests (*required GitLab CI, used Github Actions because I prefer portfolio here*)

*Tests and mypy performed on prebuilded image NOT rebuilding for every step*
- ✅ Building Docker image
- ✅ Mypy (`--strict`)
- ✅ Tests

✅ 3. Docker compose (*see below*)

✅ 5. Swagger (/docs/) and Redoc (/redoc/)

✅ 9. Handling incorrect external endpoint work

🕒 12. Logging
- ✅ API response & requests
- 🕒 etc

## Setup:

- Clone repo
```shell
git clone https://github.com/KrySeyt/BackendTask1.git
```

- Run

#### Production with your db:

*required env vars:*
- *BACKENDTASK1_POSTGRESQL_URL*
- *IMAGE_VERSION*

```shell
BACKENDTASK1_POSTGRESQL_URL=<YOUR_POSTGRES_URL> IMAGE_VERSION="1.0.0-929fb7f" docker compose -f docker-compose.yml -f production-nodb.yml up
```

#### Production with docker running db (bad idea):

*required env vars:*
- *IMAGE_VERSION*

```shell
IMAGE_VERSION="1.0.0-929fb7f" docker compose -f docker-compose.yml -f production-db.yml up
```

#### Dev with mounted local dir:
```shell
docker compose up
```

#### Dev `bash` with mounted local dir:
```shell
docker compose run mailing_service /bin/bash
```

## Configuration (Environment vars)

- ### IMAGE_VERSION
    Version of mailing_service, built by CI after commit or tag creation. Check repo packages for versions list
    
    #### There are two types of versions:
    - `main-12e214a` - `<branch>-<commit_sha>` - **FOR DEV** - dev image version for demo, 
    looking at new feature in work, etc. This builds on every commit in any branch. 
    Dev image passes all tests, mypy, etc like a prod version.
    **This is NOT for production**

    - `1.0.0-929fb7f` - `<tag>-<commit_sha>` - **FOR PROD** - prod image version. 
    Images with this versions pattern creates on every tag creation.
    After creation, this image passing all tests, mypy, etc.
    Versioning is verbose, u can find last tag version in repo releases
  
  ### **In short**:
  -  **BRANCHES - FOR DEV**
  -  **TAGS - FOR PROD**
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

- ### BACKENDTASK1_LOGGING__FORMAT
  Logging message pattern. This pattern supplements to final messages

  #### Default = "<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ!UTC}</green> | <level>{level:<8}</level>"

&ensp;&thinsp;&ensp;&thinsp;
`
BACKENDTASK1_LOGGING__FORMAT="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
`
## Postgres migrations:
### *All migrations automatically runs on service up*

### Run migrations manually:
```shell
alembic upgrade head
```

If u updated `app/models.py` you can generate new migrations before run them:
```shell
alembic revision --autogenerate
```

## Tests
  *All tests driving by <a href="https://github.com/pytest-dev/pytest">pytest</a>*
### Run tests manually
#### With built image: 
```shell
IMAGE_VERSION=main-12e214a docker compose -f docker-compose.yml -f tests.yml --abort-on-container-exit
```

```shell
IMAGE_VERSION=main-12e214a docker compose -f docker-compose.yml -f mypy.yml up
```

#### With local files:

Start dev container with `bash`:
```shell
docker compose run mailing_service /bin/bash
```

Run tests:
```shell
pytest tests
```

Tests with coverage report:
```shell
pytest tests --cov=src
```

Coverage report from `.coverage`:
*`-m`: show missing lines*
```shell
coverage report -m
```

Run mypy:
```shell
mypy src --strict
```

## CI
  On every commit to branch creates new **DEV** image with version like `<branch>-<commit_sha>` 
  This image passes all tests, mypy analysis with `--strict` and etc like prod image
  
  On every tag creation creates new **PROD** image with version like `<tag>-<commit_sha>`
  This image passes all tests, mypy analysis with `--strict` and etc
  
  - commit_sha - first 7 sha symbols of image commit
  - branch - branch name
  - tag - created tag name. Tags names is verbose versions
