#!/bin/bash

. env.sh

docker build -t ${ENV_NAME}userapi .
