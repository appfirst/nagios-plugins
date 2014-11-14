#!/usr/bin/env python

"""
Author: Tony Ling
Executes the nodetool script located within the cassandra bin directory
and parses the output depending on the metric argument.
The script requires the path of the nodetool script that comes with
apache-cassandra.  By default, it is located in the bin directory of
apache-cassandra.
For use with AppFirst collector

Usage Example:
  python /usr/share/appfirst/plugins/libexec/check_cassandra.py -L path/to/cassandra/bin -t pending_tasks -W 50 -C 100

Created on: 8/22/14
"""

import sys
import subprocess
import argparse

status_code = 3
value = 0

# metrics dict key is script argument
# values are array of metric to filter for and output string
metrics = {}
metrics['bloom_filter_space_used'] = ['Bloom Filter Space Used', 'Total Bloom Filter Space Used']
metrics['bloom_filter_false_positives'] = ['Bloom Filter False Positives', 'Total Bloom Filter False Positives']
metrics['bloom_filter_false_ratio'] = ['Bloom Filter False Ratio', 'Total Bloom Filter False Ratio']
metrics['pending_tasks'] = ['Pending Tasks', 'Total Pending Tasks']
metrics['memtable_switch_count'] = ['Memtable Switch Count', 'Total Switch Count']
metrics['memtable_data_size'] = ['Memtable Data Size', 'Total Data Size']
metrics['memtable_columns_count'] = ['Memtable Columns Count', 'Total Columns Count']

parser = argparse.ArgumentParser()
parser.add_argument('-L', '--location', help='Directory path of nodetool script, should be in same directory as cassdandra')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()
if (args.location):
	path = args.location + "/nodetool"
else:
	print "Error - option -L for NodeTool script directory required"
	sys.exit(2)
try:
	metric = args.metric
	cmd = metrics[metric][0]
	msg = metrics[metric][1]

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

cass_info = subprocess.Popen([path, 'cfstats'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
output, err = cass_info.communicate()
if (output is ""):
	sys.exit(status_code)
for line in output.split('\n\t\t'):
	tokens = line.split(':')
	if (tokens[0] == cmd):
		value += float(tokens[1])


if (args.critical and value>= args.critical):
	print "CRITICAL - " + msg + ": " + str(value) +  "|" +  metric + "=" + str(value)
	status_code = 2
elif (args.warning and value >= args.warning):
	print "WARNING - " + msg + ": " + str(value) +  "|" + metric + "=" + str(value)
	status_code = 1
else:
	print "OK - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
	status_code = 0

sys.exit(status_code)
