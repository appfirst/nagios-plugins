
![Appfirst](http://www.appfirst.com/img/appfirst-logo.png)
Nagios Plugins by [AppFirst](http://www.appfirst.com)
=====================================================

[Nagios Plugins](http://www.nagios.org/download/plugins) for popular services/servers hosted by different Cloud Services such as [EngineYard](http://engineyard.com), [Heroku](http://heroku.com). Seamless integration with [AppFirst Collector](https://wwws.appfirst.com/accounts/signup/). Now with support to streaming [Statsd](https://github.com/etsy/statsd/) Data with [Statsd_clients](https://github.com/appfirst/statsd_clients/) over [AFCollectorAPI](https://appfirst.fogbugz.com/default.asp?W213) or UDP protocol.

This README will cover the following topics:

- [Nagios Plugins](#nagios-plugins)
 	* check_postgresql
 	* check_mysql
 	* check_mongodb
 	* check_memcached
 	* check_redis
 	* check_resque
 	* check_passenger
- [Data Module and Base Classes](#data-module-and-base-classes)
- [StastD Wrapping](#stastd-wrapping)
- [AppFirst Integration](#appfirst-integration)

For further question, please email <yangming@appfirst.com>

##Nagios Plugins
------------------------------
To fetch the data for those plugins, there are mainly two kinds of way depends on what the service provides:

* **BATCH** to fetch multiple metrics in one query (such as return a dictionary or even a tree)
* **DEDICATED** to fetch individual metrics with dedicated queries.

At the moment, there are 2 kinds of statistical value in general.

- **STATUS** value, the value at the moment of checking.
- **DELTA** value, the changes between now and the last time of checking. In most cases, these values are not provided by the service/servers. The services are more likely to provide a value since the server is started. Those values, such as *total connections*, *total operations* or *total bytes received* are incremental values, so it's impossible to set a threshold for warning and critical (as eventually it will pass over any value given). Thus we'll have to calculate the delta by comparing the current value with previously checked value. And we'll also have to store the current one for future comparison. By defining a rootdir and a filename with `-d ROOTDIR -f FILENAME`, the data will be store on disk. By default, rootdir is `/tmp` and the filenames looks like `pd@cmd2get_data`. For the first time running the script or if the file is not accessible (removed, rootdir changed, etc), the output value will not be delta value since there is no previous value referrable.

Values are either one of:

- **SINGLE** Most data sources has one value for each metrics.
- **MULTIPLE** Some data sources have provided more than one statistical value, i.e. sub-performance value, such as values of individual databases or of different types. We usually trail those after the total value.

In order to use any of the plugin, make sure you have `nagios.py` and `statsd.py` in PYTHONPATH or in the same folder with the `check_*.py` plugins you'll use.

###PostgreSQL

Check status for various metrics of PostgresSQL, with commandline access:
	
	python check_postgresql.py <options>

the options are:	

	usage: check_postgresql.py [-h] [-w WARN] [-c CRIT] -t
                               {DATABASE_SIZE, TUPLES_UPDATED, LOCKS_ROW, LOCKS_ACCESS, TUPLES_READ, LOCKS_SHARE, CONNECTIONS_WAITING, CONNECTIONS_IDLE, CONNECTIONS_ACTIVE, LOCKS_EXCLUSIVE, TUPLES_INSERTED, TUPLES_DELETED}
                               [-d ROOTDIR] [-f FILENAME] [-u USER] [-p PORT]
                               [-z APPNAME]                               

**TUPLES_UPDATED**

*dedicated* | *multiple* | *delta*

This will check tuples updated in every databases of postgres since last check.  
Sample output:

	TUPLES_UPDATED OK: 0 tuples updated | total=0 template1=0 template0=0 postgres=0 appfirst=0

**TUPLES_READ**

*dedicated* | *multiple* | *delta*

This will check tuples fetched in every databases of postgres since last check.  
Sample output:

	TUPLES_READ OK: 505 tuples fetched | total=505 template1=0 template0=0 postgres=505 appfirst=0

**TUPLES_INSERTED**

*dedicated* | *multiple* | *delta*

This will check tuples inserted in every databases of postgres since last check.  
Sample output:

	TUPLES_INSERTED OK: 0 tuples inserted | total=0 template1=0 template0=0 postgres=0 appfirst=0

**TUPLES_DELETED**

*dedicated* | *multiple* | *delta*

This will check tuples deleted in every databases of postgres since last check.  
Sample output:

	TUPLES_DELETED OK: 0 tuples deleted | total=0 template1=0 template0=0 postgres=0 appfirst=0

**DATABASE_SIZE**

*dedicated* | *multiple* | *status*

This will check size (in MB) of every databases of postgres since last check.  
Sample output:

	DATABASE_SIZE OK: total dbsize: 22MB | total=22MB template1=5 template0=5 postgres=5 appfirst=5

**CONNECTIONS_WAITING**

*dedicated* | *single* | *status*

This will check how many connections are currently waiting.  
Sample output:

	CONNECTIONS_WAITING OK: 0 waiting conns | waiting=0;20;40

**CONNECTIONS_IDLE**

*dedicated* | *single* | *status*

This will check how many connections are currently idle.  
Sample output:

	CONNECTIONS_IDLE OK: 0 idle conns | idle=0;20;40

**CONNECTIONS_ACTIVE**

*dedicated* | *single* | *status*

This will check how many connections are currently active.  
Sample output:

	CONNECTIONS_ACTIVE OK: 1 active conns | active=1;100;500

###MySQL

Check status for various metrics of MySQL, with commandline access:

	python check_mysql.py <options>

the options are:  

	usage: check_mysql.py [-h] [-w WARN] [-c CRIT] -t
                          {TRANSACTIONS, SLOW_QUERIES, ROW_OPERATIONS, CONNECTIONS, REPLICATION, TOTAL_BYTES, NETWORK_TRAFFIC, QUERIES_PER_SECOND, SELECTS}
                          [-d ROOTDIR] [-f FILENAME] [-u USER] [-s PASSWORD]
                          [-H HOST] [-p PORT] [-z APPNAME]

**TRANSACTIONS**

*batch* | *multiple* | *delta*

This will check how many transtions

* *commit transoactions*
* *rollback transactions*

respectively.  
Sample output:

	TRANSACTIONS OK: 0 transactions | total=0 commit=0 rollback=0

**TOTAL_BYTES**

*batch* | *multiple* | *delta*

This will check how many

* *bytes received*
* *bytes sent*

respectively.  
Sample output:

	TOTAL_BYTES OK: 0.0557985305786MB in total | total=0.0557985305786MB bytes_received=0.000700950622559MB bytes_sent=0.0550975799561MB

**SLOW_QUERIES**

*batch* | *single* | *delta*

This will check how many slow queries.  
Sample output:

	SLOW_QUERIES OK: 0 slow queries | total=0

**SELECTS**

*batch* | *multiple* | *delta*

This will check selects including

* *select full join*
* *select full range join*
* *select range*
* *select range check*
* *select scan*

Sample output:

	SELECTS OK: 7 select | total=7 select_full_join=0 select_full_range_join=0 select_range=0 select_range_check=0 select_scan=7

**ROW_OPERATIONS**

*batch* | *multiple* | *delta*

This will check row operations including

* *rows deleted* 
* *rows inserted*
* *rows updated*
* *rows read*

Sample output:

	ROW_OPERATIONS OK: 0 row operations | total=0 rows_deleted=0 rows_inserted=0 rows_updated=0 rows_read=0

**REPLICATION**

This TYPE is incomplete.  
Sample output:

	REPLICATION UNKNOWN: mysterious status

**QUERIES_PER_SECOND**

*batch* | *single* | *delta*

This is the rate of queries (per sec) since last check.  
Sample output:

	QUERIES_PER_SECOND OK: 0.0448717948718 queries per second | total=0.0448717948718;100;300

**CONNECTIONS**

*batch* | *single* | *delta*

This checks the connections established since last check.
Sample output:

	CONNECTIONS OK: 7 new connections | conns=7;100;300

###MongoDB

Check status for various metrics of MongoDB, with commandline access:

	python check_mongodb.py <options>

the options are:	

	usage: check_mongodb.py [-h] [-w WARN] [-c CRIT] -t
                            {MEMORY_USED, INSERT, HITS, MISS_PERCENTAGE, LOCKED_PERCENTAGE, UPDATE, ACCESSES, CONNECTIONS, MISSES, COMMAND, QUERY, RESETS, DELETE}
                            [-d ROOTDIR] [-f FILENAME] [-u USER] [-s PASSWORD]
                            [-H HOST] [-p PORT] [-z APPNAME]

**CONNECTIONS**

*dedicated* | *single* | *status*

Sample output:

	CONNECTIONS OK: 1 new connections | conns=1;100;200

**MEMORY_USED**

*dedicated* | *single* | *status*

Sample output:

	MEMORY_USED OK: 12MB resident size | res=12MB

**INSERT**

*dedicated* | *single* | *delta*

Sample output:

	INSERT OK: 0 inserts | inserts=0

**UPDATE**

*dedicated* | *single* | *delta*

Sample output:

	UPDATE OK: 0 updates | updates=0

**COMMAND**

*dedicated* | *single* | *delta*

Sample output:

	COMMAND OK: 15168 commands | commands=15168
	
**QUERY**

*dedicated* | *single* | *delta*

Sample output:

	QUERY OK: 1 queries | queries=1

**DELETE**

*dedicated* | *single* | *delta*

Sample output:

	DELETE OK: 0 deletes | deletes=0

**LOCKED_PERCENTAGE**

*dedicated* | *single* | *delta*

Sample output:

	DELETE OK: 0 locked | ratio=0%

**MISS_PERCENTAGE**

*dedicated* | *single* | *delta*

Sample output:

	DELETE OK: 0 missed | ratio=0%

**RESETS**

*dedicated* | *single* | *delta*

Sample output:

	RESETS OK: 0 resets | resets=0

**HITS**

*dedicated* | *single* | *delta*

Sample output:

	HITS OK: 0 hits | hits=0

**MISSES**

*dedicated* | *single* | *delta*

Sample output:

	MISSES OK: 0 misses | misses=0

**ACCESSES**

*dedicated* | *single* | *delta*

Sample output:

	ACCESSES OK: 0 accesses | accesses=0

###MemcacheD

Check status for various metrics of MemcacheD, with commandline access:

	python check_memcached.py <options>

the options are:

    usage: check_memcached.py [-h] [-w WARN] [-c CRIT] -t
                              {TOTAL_ITEMS, BYTES_ALLOCATED, OPERATIONS_SET_REQUESTS, BYTES_WRITTEN, BYTES_READ, CURRENT_CONNECTIONS, OPERATIONS_GET_REQUESTS}
                              [-d ROOTDIR] [-f FILENAME] [-H HOST] [-p PORT]
                              [-z APPNAME]

**TOTAL_ITEMS**

*batch* | *single* | *status*

Sample output:

	TOTAL_ITEMS OK: 0 total items | items=0

**CURRENT_CONNECTIONS**

*batch* | *single* | *status*

Sample output:

	CURRENT_CONNECTIONS OK: 5 current connections | connections=5

**OPERATIONS_SET_REQUESTS**

*batch* | *single* | *delta*

Sample output:

	OPERATIONS_SET_REQUESTS OK: 0 set requests | set_requests=0

**OPERATIONS_GET_REQUESTS**

*batch* | *single* | *delta*

Sample output:

	OPERATIONS_GET_REQUESTS OK: 0 get resquests | get_requests=0

**BYTES_WRITTEN**

*batch* | *single* | *delta*

Sample output:

	BYTES_WRITTEN OK: 6171 bytes written | bytes_written=6171

**BYTES_READ**

*batch* | *single* | *delta*

Sample output:

	BYTES_READ OK: 66 bytes read | bytes_read=66

**BYTES_ALLOCATED**

*batch* | *single* | *status*

Sample output:

	BYTES_ALLOCATED OK: 0 bytes allocated | bytes_allocated=0

###Redis

Check status for various metrics of Redis, with commandline access:

	python check_redis.py <options>

the options are:

	usage: check_redis.py [-h] [-w WARN] [-c CRIT] -t
                          {MEMORY_USED, CURRENT_OPERATIONS, CHANGES_SINCE_LAST_SAVE, READ_WRITE_RATIO, AVERAGE_OPERATIONS_RATE, COMMAND_FREQUENCY, CURRENT_CHANGES, TOTAL_KEYS}
                          [-d ROOTDIR] [-f FILENAME] [-u USER] [-s PASSWORD]
                          [-H HOST] [-p PORT] [-n DATABASE] [-z APPNAME]

**TOTAL_KEYS**

*dedicated* | *single* | *status*

Sample output:

	TOTAL_KEYS OK: 8 total keys | total_keys=8;1000000;2000000

**MEMORY_USED**

*batch* | *single* | *status*

Sample output:

	MEMORY_USED OK: 0MB used_memory | used_memory=0MB;2;4

**AVERAGE_OPERATIONS_RATE**

*batch* | *single* | *status*

Sample output:

	AVERAGE_OPERATIONS_RATE OK: 0 commands per second | average_rate=0;20000;40000

**CURRENT_OPERATIONS**

*batch* | *single* | *delta*

Sample output:

	CURRENT_OPERATIONS OK: 10 commands | current_commands=10;20000;40000

**CURRENT_CHANGES**

*batch* | *single* | *delta*

Sample output:

	CURRENT_CHANGES OK: 0 changes | changes=0

**CHANGES_SINCE_LAST_SAVE**

*batch* | *single* | *status*

Sample output:

	CHANGES_SINCE_LAST_SAVE OK: 0 changes since last save | changes=0;100;300

###Resque

Check status for various metrics of Resque, with commandline access:

    python check_resque.py <options>

the options are:

    usage: check_resque.py [-h] [-w WARN] [-c CRIT] -t
                           {QUEUE_LENGTH,JOB_PROCESSED} [-d ROOTDIR] [-f FILENAME]
                           [-u USER] [-s PASSWORD] [-H HOST] [-p PORT]
                           [-n DATABASE] [-z APPNAME]

**QUEUE_LENGTH**

*dedicated* | *multiple* | *status*

Sample output:

	QUEUE_LENGTH OK: 0 jobs in queues | total=0 default=0 critical=0 failing=0

**JOB_PROCESSED**

*dedicated* | *single* | *delta*

Sample output:

	JOB_PROCESSED OK: 0 jobs in processed | total=133

###Passenger

Check status for various metrics of Passenger, with commandline access:

    python check_passenger.py <options>

the options are:

	usage: check_passenger.py [-h] [-w WARN] [-c CRIT] -t
                              {ACTIVE_PROCESSES,MAX_PROCESSES,RUNNING_PROCESSES}
                              [-d ROOTDIR] [-f FILENAME] [-p PID] [-z APPNAME]

**RUNNING_PROCESSES**

*batch* | *single* | *status*

Sample output:

	RUNNING_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

**MAX_PROCESSES**

*batch* | *single* | *status*

Sample output:

	MAX_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

**ACTIVE_PROCESSES**

*batch* | *single* | *status*

Sample output:

	ACTIVE_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

##Data Module and Base Classes
------------------------------
*nagios.py* holds all the datatype class and base class for plugins.

    @plugin.command("BYTES_WRITTEN")
    
    


##StatsD Wrapping
------------------------------

*statsd.py* provides plugins an easy way to send performance value as statsd message. This module requires those files in [statsd_clients](https://github.com/appfirst/statsd_clients/)/python in PYTHON_PATH.

There are currently three statsd wrapper: `statsd.gauge`, `statsd.counter`, `statsd.timer`. The usage is quite intuitive, just add it to any method that returns a `nagios.Result` with a performance value. The wrapper will intercept the return value of the method, make the bucket name from the **BUCKET_PATTERN** (by default it's "**sys.app.%(appname)s.%(type)s**"). You can

	statsd.set_bucket_pattern(pattern)

to your own pattern. Available items from Result are: `appname`, `type`, `status_code`, `status`, `message`, `value` (the first of performance values).
By default this wrapper will send statsd to AppFirst Collector through AFTransport, but you can pass in your own transport by

	statsd.set_transport(transport)

Please reference details to [Statsd_clients](https://github.com/appfirst/statsd_clients/).

For plugins that has **STATUS** value, `gauge` is most likely to be suitable, those usually include memory usage, rate, active connection and total keys in databses.  
For plugins that has **DELTA** value, `counter` is most likely to be suitable, those usually include bytes transfered, operations, errors, newly established connections.

Here's an example of counter:

	@nagios.CommandBasedPlugin.command("BYTES_WRITTEN")
    @statsd.counter
    def get_bytes_written(self, request):
        return nagios.Result(type, status_code)

Note that the statsd descriptor should be applied after the `nagios.CommandBasedPlugin.command` descriptor in order to be executed if you are writing an CommandBasedPlugin.

##AppFirst Integration
------------------------------


##Appendix:
------------------------------

Here's TABLE OF COMPARISON OF METRICS:

[Service]      | [Metrics]               | [FetchMode] | [ValuMode] | [ValueType] | [Statsd]
:------------- | :---------------------- | :---------: | :--------: | :---------: | :------:
**PostgreSQL** | TUPLES_UPDATED          | dedicated   | multiple   | delta       | counter
               | TUPLES_READ             | dedicated   | multiple   | delta       | counter
               | TUPLES_INSERTED         | dedicated   | multiple   | delta       | counter
               | TUPLES_DELETED          | dedicated   | multiple   | delta       | counter
               | LOCKS_ACCESS            | dedicated   | multiple   | status      | gauge
               | LOCKS_ROW               | dedicated   | multiple   | status      | gauge
               | LOCKS_SHARE             | dedicated   | multiple   | status      | gauge
               | LOCKS_EXCLUSIVE         | dedicated   | multiple   | status      | gauge
               | DATABASE_SIZE           | dedicated   | multiple   | status      | gauge
               | CONNECTIONS_WAITING     | dedicated   | single     | status      | gauge
               | CONNECTIONS_IDLE        | dedicated   | single     | status      | gauge
               | CONNECTIONS_ACTIVE      | dedicated   | single     | status      | gauge
**MySQL**      | TRANSACTIONS            | batch       | multiple   | delta       | counter
               | TOTAL_BYTES             | batch       | multiple   | delta       | counter
               | SLOW_QUERIES            | batch       | single     | delta       | counter
               | SELECTS                 | batch       | multiple   | delta       | counter
               | ROW_OPERATIONS          | batch       | multiple   | delta       | counter
               | QUERIES_PER_SECOND      | batch       | single     | delta       | gauge
               | CONNECTIONS             | batch       | single     | delta       | counter
**MongoDB**    | CONNECTIONS             | dedicated   | single     | status      | gauge
               | MEMORY_USED             | dedicated   | single     | status      | gauge
               | INSERT                  | dedicated   | single     | status      | counter
               | UPDATE                  | dedicated   | single     | status      | counter
               | COMMAND                 | dedicated   | single     | status      | counter
               | QUERY                   | dedicated   | single     | status      | counter
               | DELETE                  | dedicated   | single     | status      | counter
               | LOCKED_PERCENTAGE       | batch       | single     | status      | gauge
               | MISS_PERCENTAGE         | dedicated   | single     | status      | gauge
               | HITS                    | dedicated   | single     | status      | counter
               | MISSES                  | dedicated   | single     | status      | counter
               | RESETS                  | dedicated   | single     | status      | counter
               | ACCESSES                | dedicated   | single     | status      | counter
**Memcached**  | TOTAL_ITEMS             | batch       | single     | status      | gauge
               | CURRENT_CONNECTIONS     | batch       | single     | status      | gauge
               | OPERATIONS_SET_REQUESTS | batch       | single     | delta       | counter
               | OPERATIONS_GET_REQUESTS | batch       | single     | delta       | counter
               | BYTES_WRITTEN           | batch       | single     | delta       | counter
               | BYTES_READ              | batch       | single     | delta       | counter
               | BYTES_ALLOCATED         | batch       | single     | status      | gauge
**Redis**      | TOTAL_ITEMS             | dedicated   | single     | status      | gauge
               | MEMORY_USED             | batch       | single     | status      | gauge
               | AVERAGE_OPERATIONS_RATE | batch       | single     | status      | gauge
               | CURRENT_OPERATIONS      | batch       | single     | status      | gauge
               | CURRENT_CHANGES         | batch       | single     | delta       | counter
               | CHANGES_SINCE_LAST_SAVE | batch       | single     | status      | gauge
**Resque**     | QUEUE_LENGTH            | dedicated   | multiple   | status      | gauge
               | JOB_PROCESSED           | batch       | single     | delta       | counter
**Passenger**  | RUNNING_PROCESSES       | batch       | single     | status      | gauge
               | MAX_PROCESSES           | batch       | single     | status      | gauge
               | ACTIVE_PROCESSES        | batch       | single     | status      | gauge