#!/usr/bin/env python

import json
import urllib
import os.path

def execute():
	with open('config') as config_file:
		config = json.load(config_file)

	for rpm_dep in config["RPM_DEP_URLS"]: 
		print "Pulling dependency %s" % rpm_dep
		file_name = 'bin/' + rpm_dep.split('/')[-1]
		if os.path.isfile(file_name) != True:
			print "Downloading ..."
			urllib.urlretrieve(rpm_dep,file_name)
		else:
			print "Using cached copy in bin"
		print "Completed"

if __name__ == '__main__':
	execute()