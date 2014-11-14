#!/usr/bin/env python

"""
Author: Tony Ling
Checks couch _stats page and parses the output depending on the argument.
For use with AppFirst collector

Example Usage: python /usr/share/appfirst/plugins/libexec/check_couchdb.py -t average_requests -W 50 -C 100

Created on: 8/22/14
"""

import sys
import argparse
import urllib2
import json

status_code = 3

# metrics dict key value is an array of 4 strings.
# Elements: 0=part 1 of url pth, 1=part 2 of url path, 3=json key, 4=message
metrics = {}
metrics['total_requests'] = ['httpd','requests','current','Total httpd requests since server started']
metrics['average_requests'] = ['httpd','requests','mean','Httpd requests per second']
metrics['total_bulk_requests'] = ['httpd','bulk_requests','current','Total httpd bulk requests since server started']
metrics['average_bulk_requests'] = ['httpd','bulk_requests','mean','Httpd bulk requests per second']
metrics['average_COPY_requests'] = ['httpd_request_methods','COPY','mean','Httpd COPY requests per second']
metrics['average_DELETE_requests'] = ['httpd_request_methods','DELETE','mean','Httpd DELETE requests per second']
metrics['average_GET_requests'] = ['httpd_request_methods','GET','mean','Httpd GET requests per second']
metrics['average_HEAD_requests'] = ['httpd_request_methods','HEAD','mean','Httpd HEAD requests per second']
metrics['average_MOVE_requests'] = ['httpd_request_methods','MOVE','mean','Httpd MOVE requests per second']
metrics['average_POST_requests'] = ['httpd_request_methods','POST','mean','Httpd POST requests per second']
metrics['average_PUT_requests'] = ['httpd_request_methods','PUT','mean','Httpd PUT requests per second']

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=5984', default='5984')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()
try:
	metric_path = metrics[args.metric]
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)
if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)

#default url = http://127.0.0.1:5984/_stats
url = "http://{host}:{port}/_stats/{_path1}/{_path2}".format(host=args.host,port=args.port, 
								_path1=metric_path[0], _path2=metric_path[1])

couchdb_obj   = json.loads(urllib2.urlopen(url).read())
metric_value  = couchdb_obj[metric_path[0]][metric_path[1]][metric_path[2]]
if (metric_value is None):
	metric_value = 0

if (args.critical and metric_value >= args.critical):
	print "CRITICAL - " + metric_path[3] + ": " + str(metric_value) + "|" + args.metric + "=" + str(metric_value)
	status_code = 2
elif (args.warning and metric_value >= args.warning):
	print "WARNING - " + metric_path[3] + ": " + str(metric_value) + "|" + args.metric + "=" + str(metric_value)
	status_code = 1
else:
	print "OK - " + metric_path[3] + ": " + str(metric_value) + "|" + args.metric + "=" + str(metric_value)
	status_code = 0

sys.exit(status_code)
