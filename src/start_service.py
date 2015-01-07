#!/usr/bin/env bash

import threading
import time
import json
import requests
import sqlite3
import signal
import sys
import os
import datetime

agent_name_template = "docker-agent-%s"

def init_db():

	global conn
	print "Initializing db..."

	conn = sqlite3.connect('db/spawned-agents.db', sqlite3.PARSE_COLNAMES)
	cur = conn.cursor()
	cur.execute(""" 
		CREATE TABLE IF NOT EXISTS docker_agents (agent_uuid, agent_name, agent_creation_time, agent_destroy_time)
	""")
	conn.commit()
	conn.close()
	print "Initializing db...[DONE]"


def clean_up(signum, frame):
	conn.close()
	print "Closing db connections..."
	sys.exit()


def execute():
	while True:
		print "Executing..."
		conn = sqlite3.connect('db/spawned-agents.db', sqlite3.PARSE_COLNAMES)
		cur = conn.cursor()
		idle_count = get_count_of_idle_agents()
		if (idle_count <= threshold):
			spawn_new_agent(cur)
		else:
			delete_useless_agents(cur)
			print "GO seems okay. So lets continue..."
		conn.commit()
		conn.close()
		time.sleep(10)
	

def spawn_new_agent(cur):
	print "Spawning..."
	agent_id = get_number_of_spawned_agents(cur)
	agent_name = agent_name_template % str(agent_id)
	command = "/bin/bash src/docker_run_container.sh %s" % agent_name
	os.system(command)
	uuid = enable_agent_and_get_uuid()
	if uuid != None:
		add_agent_to_db(cur, uuid, agent_name)


def enable_agent_and_get_uuid():
	ready = False
	while not ready:
		print "Trying to get information regarding the newly spawned agent. It must be provisioning so I will wait a while..."
		agents = json.loads(requests.get(go_agent_list_url).text)
		for agent in agents:
			if agent["status"].lower() == "pending":
				ready = True
				uuid = agent["uuid"]
				break
		time.sleep(10)
	print "UUID is %s" % uuid
	print "Enabling agent ..."
	response = requests.post(go_enable_agent_url % uuid)
	print "Enabling agent with status code %s" % response.status_code
	if response.status_code != 200:
		return None
	return uuid


def add_agent_to_db(cur, uuid, agent_name):
	now = datetime.datetime.now()
	delete_time = now + datetime.timedelta(minutes = 1)
	cur.execute("INSERT INTO docker_agents VALUES (\'%s\', \'%s\', \'%s\', \'%s\')" % (uuid, agent_name, str(now), str(delete_time) ))


def delete_useless_agents(cur):
	agents = json.loads(requests.get(go_agent_list_url).text)
	cur.execute("SELECT * FROM docker_agents")
	for row in cur.fetchall():
		agent_name = row[1]
		agent_uuid = row[0]
		delete_time = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
		now = datetime.datetime.now()
		if( now > delete_time ):
			for agent in agents:
				if agent["uuid"] == agent_uuid:
					if agent["status"].lower() == "idle":
						print "Time to delete agent %s with UUID %s" % (agent_name, agent_uuid)
						print "Disabling agent in GO"
						response = requests.post(go_disable_agent_url % agent_uuid)
						print "Disabling agent with status code %s" % response.status_code
						if response.status_code == 200:
							os.system("/bin/bash src/docker_delete_container.sh %s" % agent_name)
						response = requests.post(go_delete_agent_url % agent_uuid)
						print "Deleting agent with status code %s" % response.status_code
						if response.status_code == 200:
							cur.execute("DELETE FROM docker_agents WHERE agent_uuid=\'%s\'" % agent_uuid)
					else:
						delete_time = now + datetime.timedelta(minutes = 10)
						print "Extending planned delete time for agent %s with UUID %s" % (agent_name, agent_uuid)
						cur.execute("UPDATE docker_agents SET delete_time=\'%s\' WHERE agent_name=\'%s\'" % (str(delete_time),agent_name) )


def get_number_of_spawned_agents(cur):
	cur.execute("SELECT count(*) FROM docker_agents")
	return cur.fetchall()[0][0]
	

def get_count_of_idle_agents():
	agents = json.loads(requests.get(go_agent_list_url).text)
	count = 0
	for agent in agents:
		if agent["status"].lower() == "idle":
			count += 1
	return count
	

def setup_global_data():
	
	global config
	global go_server_url
	global go_agent_list_url
	global go_enable_agent_url
	global go_disable_agent_url
	global go_delete_agent_url
	global threshold

	with open('config') as config_file:
		config = json.load(config_file)
	if config["AUTH"].lower() == "true":
		go_server_url = "http://{0}:{1}@{2}:{3}".format(config["USERNAME"], config["PASSWORD"], config["GO_SERVER"], config["GO_SERVER_PORT"])
	else:
		go_server_url = "http://{0}:{1}".format(config["GO_SERVER"], config["GO_SERVER_PORT"])
		
	go_agent_list_url = "{0}/go/api/agents".format(go_server_url)
	go_enable_agent_url = "{0}/go/api/agents/%s/enable".format(go_server_url)
	go_disable_agent_url = "{0}/go/api/agents/%s/disable".format(go_server_url)
	go_delete_agent_url = "{0}/go/api/agents/%s/delete".format(go_server_url)
	threshold = int(config["THRESHOLD"])

if __name__ == '__main__':
	init_db()
	signal.signal(signal.SIGINT, clean_up)
	setup_global_data()
	execute()