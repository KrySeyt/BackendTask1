FROM python:3.11.2-slim-bullseye
RUN apt-get update && \
    rm -rf /var/lib/apt
WORKDIR /mailing_service/
ENV VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY .coveragerc .
COPY alembic.ini .
COPY mypy.ini .
COPY alembic/ alembic/
COPY src/ src/
COPY tests/ tests/

CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
