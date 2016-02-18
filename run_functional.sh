#!/bin/bash

. env.sh

API_HOST_PORT=$(docker port ${ENV_NAME}userapi_api 8000)

export API_URL="http://${API_HOST_PORT}"
tox -efunctional
