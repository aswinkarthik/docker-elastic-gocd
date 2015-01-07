#!/usr/bin/env bash

export DOCKER_TLS_VERIFY=1
docker run -i -t --name $1 -d go_agent