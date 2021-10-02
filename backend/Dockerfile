FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY . .
CMD ["pipenv", "run", "start"]

# TODO: use wsgi-server in production
