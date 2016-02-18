#!/bin/bash

. env.sh

. build_api.sh

. userapi_db.sh create-tables

. run_api.sh
