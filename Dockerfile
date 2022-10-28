FROM python:3.10.7-slim-bullseye

# TODO: should these be ARGs instead?
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
ENV DEBUG=$DEBUG
ENV DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS
ENV DATABASE_ENGINE=$DATABASE_ENGINE
ENV DATABASE_NAME=$DATABASE_NAME
ENV DATABASE_USERNAME=$DATABASE_USERNAME
ENV DATABASE_PASSWORD=$DATABASE_PASSWORD
ENV DATABASE_HOST=$DATABASE_HOST
ENV DATABASE_PORT=$DATABASE_PORT

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install psycopg2 dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY ./ /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "voterguide.wsgi"]
