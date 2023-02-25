FROM python

WORKDIR /mailing_service/

ENV VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8888

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8888"]
