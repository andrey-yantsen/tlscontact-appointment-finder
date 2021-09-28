FROM python:3.9-alpine
WORKDIR /usr/src/app
ENV PIPENV_VENV_IN_PROJECT=1
COPY Pipfile Pipfile.lock /usr/src/app/
RUN apk add --no-cache openssl-dev libffi-dev musl-dev make gcc && pip install --upgrade pip && pip3 install pipenv\
    && pipenv install && apk del openssl-dev libffi-dev musl-dev make gcc
COPY . /usr/src/app/
ENTRYPOINT ["pipenv", "run", "python3", "-u", "main.py"]
