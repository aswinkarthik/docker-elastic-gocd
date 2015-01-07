#!/usr/bin/env bash
export DOCKER_HOST=tcp://192.168.59.103:2376
export DOCKER_CERT_PATH=/Users/aswinks/.boot2docker/certs/boot2docker-vm
export DOCKER_TLS_VERIFY=1
docker build -t go_agent .