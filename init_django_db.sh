#!/bin/bash
set -e

DJANGOPASS=$(cat /run/secrets/django-password)

# Postgresql 15 no longer grants access to the public schema automatically.
# The following will create a database and (non-super-)user for the django
# application, with the specified password. Then it creates a schema for that
# user. Since the schema is set to the same name as the user name, it will be
# on the user's search path by default.
# TODO: might want to try to pull the postgres user and dbname from env vars,
# if they get set there rather than using the defaults, e.g.
# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
  CREATE DATABASE voterguide;
  CREATE USER vguser WITH PASSWORD '${DJANGOPASS}';
  \connect voterguide;
  CREATE SCHEMA vguser AUTHORIZATION vguser;
  ALTER ROLE vguser SET client_encoding TO 'utf8';
  ALTER ROLE vguser SET default_transaction_isolation TO 'read committed';
  ALTER ROLE vguser SET timezone TO 'UTC';
EOSQL
