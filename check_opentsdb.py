#!/usr/bin/env python

"""
Author: Tony Ling
Uses OpenTSDB HTTP API for server metrics and parses the output
Metrics supported: open_connections, http, telnet,total_connections, get, put,
    delete, scan, increment, flushes, compactions, timeouts, resets
Warnings trigger if metric values are greater than or equal to threshold.

Example Usage:
  python check_opentsdb.py -t open_connections -H localhost -P 10101

Created on: 11/07/14
"""

import sys
import urllib2
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=10101', default='10101')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
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

def cmp_greater(msg, value):
	check_thresholds()
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


def get_total_connections():
	msg = "Number of total connections"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.connectionmgr.connections':
				if metric['tags']['type'] == 'total':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain total connections"
	cmp_greater(msg, value)

def get_current_connections(metrics):
	msg = "Number of open connections"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.connectionmgr.connections':
				if metric['tags']['type'] == 'open':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain open connections"
	cmp_greater(msg, value)

def get_connections_timeout(metrics):
	msg = "Number of connections timeouts"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.connectionmgr.exceptions':
				if metric['tags']['type'] == 'timeout':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain connections timeouts"
	cmp_greater(msg, value)

def get_connections_reset(metrics):
	msg = "Number of connections resets"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.connectionmgr.exceptions':
				if metric['tags']['type'] == 'reset':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain connections resets"
	cmp_greater(msg, value)

def get_rpc_telnet(metrics):
	msg = "Number of telnet rpcs recieved"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.rpc.received':
				if metric['tags']['type'] == 'telnet':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain telnet rpcs recieved"
	cmp_greater(msg, value)

def get_rpc_http(metrics):
	msg = "Number of http rpcs recieved"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.rpc.received':
				if metric['tags']['type'] == 'http':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain http rpcs recieved"
	cmp_greater(msg, value)

def get_rpc_hbase_get(metrics):
	msg = "Number of hbase get rpcs"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.rpcs':
				if metric['tags']['type'] == 'get':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase get rpcs"
	cmp_greater(msg, value)

def get_rpc_hbase_put(metrics):
	msg = "Number of hbase put rpcs"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.rpcs':
				if metric['tags']['type'] == 'put':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase put rpcs"
	cmp_greater(msg, value)

def get_rpc_hbase_delete(metrics):
	msg = "Number of hbase delete rpcs"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.rpcs':
				if metric['tags']['type'] == 'delete':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase delete rpcs"
	cmp_greater(msg, value)

def get_rpc_hbase_scan(metrics):
	msg = "Number of hbase scan rpcs"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.rpcs':
				if metric['tags']['type'] == 'scan':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase scan rpcs"
	cmp_greater(msg, value)

def get_rpc_hbase_increment(metrics):
	msg = "Number of hbase increment rpcs"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.rpcs':
				if metric['tags']['type'] == 'increment':
					value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase increment rpcs"
	cmp_greater(msg, value)

def get_rpc_hbase_flushes(metrics):
	msg = "Number of hbase flushes"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.hbase.flushes':
				value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain hbase flush"
	cmp_greater(msg, value)

def get_compactions(metrics):
	msg = "Number of tsd compactions"
	value = 0
	for metric in metrics:
		try:
			if metric['metric'] == 'tsd.compaction.count':
				value += int(metric['value'])
		except:
			print "ERROR - Cannot obtain tsd compaction"
	cmp_greater(msg, value)

def get_opentsdb_metrics():
	try:
		output = urllib2.urlopen("http://{host}:{port}/api/stats".format(host=args.host, port=args.port))
		opentsdb_metrics = json.loads(output.read())
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
	return opentsdb_metrics

# metrics dict keys are script metric -t arguments
# key values are functions called when the keys are matched
metrics = { "open_connections": get_current_connections,
            "http": get_rpc_http,
            "telnet": get_rpc_telnet,
            "total_connections": get_total_connections,
            "get": get_rpc_hbase_get,
            "put": get_rpc_hbase_put,
            "delete": get_rpc_hbase_delete,
            "scan": get_rpc_hbase_scan,
            "increment": get_rpc_hbase_increment,
            "flushes": get_rpc_hbase_flushes,
            "compactions": get_compactions,
            "timeouts": get_connections_timeout,
            "resets": get_connections_reset
            }

# Program entry starts here
status_code = 3
try:
	metrics[args.metric](get_opentsdb_metrics())
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)
