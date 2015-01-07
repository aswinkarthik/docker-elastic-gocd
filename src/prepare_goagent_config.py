#!/usr/bin/env python
from string import Template
import json

def execute():

	with open('config') as config_file:
		config = json.load(config_file)

	with open ("templates/go-agent.template") as go_agent_template:
		template = Template(go_agent_template.read())

	data = template.safe_substitute(config)

	with open('bin/go-agent', 'w') as go_agent_config:
		go_agent_config.write(data)

	print "Prepared go-agent config"

if __name__ == "__main__":
	execute()