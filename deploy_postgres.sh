#!/bin/bash

. env.sh

if [ -z "$(docker ps --filter name==${ENV_NAME}userapi_postgres_volumes)" ]; then
    docker create --name ${ENV_NAME}userapi_postgres_volumes \
        postgres
fi

if [ -z "$(docker ps --filter name==${ENV_NAME}userapi_postgres)" ]; then
    docker run --name ${ENV_NAME}userapi_postgres \
        -d --restart always \
        --volumes-from ${ENV_NAME}userapi_postgres_volumes \
        -e POSTGRES_USER=${POSTGRES_USER} \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
        -e POSTGRES_DB=${POSTGRES_DB} \
        postgres
fi