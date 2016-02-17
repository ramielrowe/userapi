#!/bin/bash

. env.sh

docker create --name ${ENV_NAME}userapi_postgres_volumes \
    postgres

docker run --name ${ENV_NAME}userapi_postgres \
    -d --restart always \
    --volumes-from ${ENV_NAME}userapi_postgres_volumes \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    postgres
