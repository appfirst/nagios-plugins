#!/usr/bin/env python

"""
Author: Tony Ling
Uses Elasticsearch HTTP API for cluster health metrics and parses the output
Metrics supported: status, number_of_nodes, number_of_data_nodes, active_primary_shards, active_shards, relocating_shards, initializing_shards, unassigned_shards
Warnings if metric value is less than threshold: number_of_nodes, number_of_data_nodes, active_primary_shards, active_shards
Warnings if metric value is greater than threshold: relocating_shards, initializing_shards, unassigned_shards

Example Usage:
  python check_elasticsearch.py -t status -H localhost -P 9200 -W 10 -C 20

Created on: 10/31/14
"""

import sys
import urllib2
import json
import argparse

status_code = 3

# metrics dict keys are script metric -t arguments
# key list values: element 0 = script output string, 1 = greater than/less than/status for critical/warning values
metrics = {}
metrics['status'] = ['Cluster health status', 'status']
metrics['number_of_nodes'] = ['Number of nodes', 'less']
metrics['number_of_data_nodes'] = ['Number of data nodes', 'less']
metrics['active_primary_shards']= ['Number of active primary shards', 'less']
metrics['active_shards']= ['Number of active shards', 'less']
metrics['relocating_shards']= ['Number of relocating shards', 'greater']
metrics['initializing_shards']= ['Number of initializing shards', 'greater']
metrics['unassigned_shards']= ['Number of unassigned shards', 'greater']

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=9200', default='9200')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()

if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)

try:
	array_value = metrics[args.metric]
	msg = array_value[0]
	cmp_method = array_value[1]
	output = urllib2.urlopen("http://{host}:{port}/_cluster/health?pretty=true".format(host=args.host, port=args.port))
	cluster_health = json.loads(output.read())
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)
except urllib2.URLError:
	print "Error: Connection Refused - Check host and port arguments"
	sys.exit(status_code)

try:
	value = cluster_health[args.metric]
except:
	print "Error: Returned cluster health does not include metric {_metric}".format(_metric=args.metric)
	status_code = 2
	sys.exit(status_code)

if cmp_method == 'status':
	if value == "red":
		status_code = 2
		print "CRITICAL - " + msg + ": " + value + "|" + args.metric + "=" + value
	elif value == "yellow":
		status_code = 1
		print "WARNING - " + msg + ": " + value + "|" + args.metric + "=" + value
	else:
		status_code = 0
		print "OK - " + msg + ": " + value + "|" + args.metric + "=" + value
elif cmp_method == 'less':
	if (args.critical and int(value) <= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and int(value) <= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0
elif cmp_method == 'greater':
	if (args.critical and int(value) >= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and int(value) >= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0

sys.exit(status_code)
