#!/bin/sh

. env.sh

docker run --rm -ti \
    --link ${ENV_NAME}userapi_postgres \
    -e PGHOST=${ENV_NAME}userapi_postgres \
    -e PGUSER=${POSTGRES_USER} \
    -e PGPASSWORD=${POSTGRES_PASSWORD} \
    -e PGDATABASE=${POSTGRES_DB} \
    postgres \
    psql
