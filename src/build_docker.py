#!/usr/bin/env bash
from io import BytesIO
from docker import Client
from docker.utils import kwargs_from_env

def execute():
	print "Reading Dockerfile..."
	with open("Dockerfile") as dockerfile:
		data = BytesIO(dockerfile.read().encode('utf-8'))
		print "Sending to daemon..."
		cli = Client(**kwargs_from_env())
		response = [line for line in cli.build(
			fileobj=data, rm=True, tag='docker_builder/get_agent'
		)]
		print response.text
		print "Completed."


if __name__ == '__main__':
	execute()