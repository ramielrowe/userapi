#!/bin/bash

. env.sh

docker stop -t 5 ${ENV_NAME}userapi_api
docker rm -fv ${ENV_NAME}userapi_api

docker run -d --name ${ENV_NAME}userapi_api \
    --restart always \
    -p 8001:8000 \
    --link ${ENV_NAME}userapi_postgres \
    -e POSTGRES_HOST=${ENV_NAME}userapi_postgres \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    ${ENV_NAME}userapi
