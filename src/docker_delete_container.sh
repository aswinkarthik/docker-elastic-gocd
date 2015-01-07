#!/usr/bin/env bash
export DOCKER_TLS_VERIFY=1
docker kill $1
docker rm $1