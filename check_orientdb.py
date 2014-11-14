#!/usr/bin/env python

"""
Author: Tony Ling
Uses OrientDB HTTP API for server metrics and parses the output.
Username and password arguments are required if orientdb-server-config.xml is
not configured to allow default username and password access to resources.

Metrics supported: databases, classes, clusters, connections, records
Warnings if metric value is less than threshold: databases, classes, clusters
Warnings if metric value is greater than threshold: connections, records

Example Usage:
  python check_orientdb.py -t databases -H localhost -P 2480 -W 2 -C 1

Created on: 11/07/14
"""

import sys
import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=2480', default='2480')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-U', '--user', help='User name', default="guest")
parser.add_argument('-p', '--password', help='Password', default="guest")
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)
args = parser.parse_args()

def check_thresholds():
	if (args.critical and args.critical < 0):
		print "Error: -C Critical cannot be negative"
		sys.exit(status_code)
	elif (args.warning and args.warning < 0):
		print "Error: -W Warning cannot be negative"
		sys.exit(status_code)

def cmp_less(msg, value):
	check_thresholds()
	if (args.critical and float(value) <= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) <= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0
	sys.exit(status_code)

def cmp_greater(msg, value):
	check_thresholds()
	if (args.critical and float(value) >= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) >= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0
	sys.exit(status_code)

def get_databases():
	return get_orientdb_metrics("listDatabases")["databases"]

def get_database_classes():
	msg = "Total databases classes"
	dbs = get_databases()
	value = 0
	for db in dbs:
		db_metrics = get_orientdb_metrics("database/{db}".format(db=db))
		value += len(db_metrics['classes'])
	cmp_less(msg, value)

def get_database_clusters():
	msg = "Total databases clusters"
	dbs = get_databases()
	value = 0
	for db in dbs:
		db_metrics = get_orientdb_metrics("database/{db}".format(db=db))
		value += len(db_metrics['clusters'])
	cmp_less(msg, value)

def get_database_records():
	msg = "Total databases records"
	dbs = get_databases()
	value = 0
	for db in dbs:
		clusters = get_orientdb_metrics("database/{db}".format(db=db))['clusters']
		for ele in clusters:
			value += int(ele['records'])
	cmp_greater(msg, value)

def get_databases_count():
	msg = "Number of databases"
	value = len(get_databases())
	check_thresholds()
	cmp_less(msg, value)

def get_server_connections():
	metrics = get_orientdb_metrics("server")
	msg = "Number of server connections"
	value = len(metrics["connections"])
	cmp_greater(msg, value)

def get_orientdb_metrics(url):
	try:
		output = requests.get("http://{host}:{port}/{url}".format(host=args.host, port=args.port, url=url),
		 auth=('{user}'.format(user=args.user), '{passw}'.format(passw=args.password)))
		orientdb_metrics = json.loads(output.text)
		
	except ValueError:
		print "Error: Connection Refused - Check host, port, username and password"
		sys.exit(status_code)
	return orientdb_metrics

# metrics dict keys are script metric -t arguments
# key values are functions called when the keys are matched
metrics = { "databases": get_databases_count,
            "connections": get_server_connections,
            "classes": get_database_classes,
            "clusters": get_database_clusters,
            "records": get_database_records
            }

# Program entry starts here
status_code = 3
try:
	metrics[args.metric]()
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)
