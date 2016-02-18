#!/bin/bash

. env.sh

docker run --rm \
    --link ${ENV_NAME}userapi_postgres \
    -e POSTGRES_HOST=${ENV_NAME}userapi_postgres \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    --entrypoint userapi-db \
    ${ENV_NAME}userapi_api \
    $@
