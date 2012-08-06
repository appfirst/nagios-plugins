Nagios Plugins by [AppFirst](http://www.appfirst.com)
=====================================================

[Nagios Plugins](http://www.nagios.org/download/plugins) for popular services hosted by different Cloud Services such as [EngineYard](http://engineyard.com), [Heroku](http://heroku.com). Seamless integration with [AppFirst Collector](https://wwws.appfirst.com/accounts/signup/). Now with support to streaming [Statsd](https://github.com/etsy/statsd/) Data with [Statsd_clients](https://github.com/appfirst/statsd_clients/) over UDP protocol or [AFCollectorAPI](https://appfirst.fogbugz.com/default.asp?W213).

##nagios plugins
****************************

###PostgreSQL

*python check_postgres.py \<options\>*

**TUPLES_UPDATED**
this will check all

	TUPLES_UPDATED OK: 0 tuples updated | total=0 template1=0 template0=0 postgres=0 appfirst=0

**TUPLES_READ**

	TUPLES_READ OK: 505 tuples fetched | total=505 template1=0 template0=0 postgres=505 appfirst=0

**TUPLES_INSERTED**

	TUPLES_INSERTED OK: 0 tuples inserted | total=0 template1=0 template0=0 postgres=0 appfirst=0

**TUPLES_DELETED**

	TUPLES_DELETED OK: 0 tuples deleted | total=0 template1=0 template0=0 postgres=0 appfirst=0

**DATABASE_SIZE**

	DATABASE_SIZE OK: total dbsize: 22MB | total=22MB template1=5 template0=5 postgres=5 appfirst=5

**CONNECTIONS_WAITING**

	CONNECTIONS_WAITING OK: 0 waiting conns | waiting=0;20;40

**CONNECTIONS_IDLE**

	CONNECTIONS_IDLE OK: 0 idle conns | idle=0;20;40

**CONNECTIONS_ACTIVE**

	CONNECTIONS_ACTIVE OK: 1 active conns | active=1;100;500

###MySQL

*python check_memcached.py \<options\>*

**TRANSACTIONS**

	TRANSACTIONS OK: 0 transactions | total=0 commit=0 rollback=0

**TOTAL_BYTES**

	TOTAL_BYTES OK: 0.0557985305786MB in total | total=0.0557985305786MB bytes_received=0.000700950622559MB bytes_sent=0.0550975799561MB

**SLOW_QUERIES**

	SLOW_QUERIES OK: 0 slow queries | total=0

**SELECTS**

	SELECTS OK: 7 select | total=7 select_full_join=0 select_full_range_join=0 select_range=0 select_range_check=0 select_scan=7

**ROW_OPERATIONS**

	ROW_OPERATIONS OK: 0 row operations | total=0 rows_deleted=0 rows_inserted=0 rows_updated=0 rows_read=0

**REPLICATION**

	REPLICATION UNKNOWN: mysterious status

**QUERIES_PER_SECOND**

	QUERIES_PER_SECOND OK: 0.0448717948718 queries per second | total=0.0448717948718;100;300

**CONNECTIONS**

	CONNECTIONS OK: 7 new connections | conns=7;100;300

### Check MongoDB

*python check_mongodb.py \<options\>*

**UPDATE**

	UPDATE OK: 0 updates | updates=0

**QUERY**

	QUERY OK: 1 queries | queries=1

**MEMORY_USED**

	MEMORY_USED OK: 12MB resident size | res=12MB

**INSERT**

	INSERT OK: 0 inserts | inserts=0

**DELETE**

	DELETE OK: 0 deletes | deletes=0

**CONNECTIONS**

	CONNECTIONS OK: 1 new connections | conns=1;100;200

**COMMAND**

	COMMAND OK: 15168 commands | commands=15168

### Check Memcached

*python check_memcached.py \<options\>*

**TOTAL_ITEMS**

	TOTAL_ITEMS OK: 0 total items | items=0

**OPERATIONS_SET_REQUESTS**

	OPERATIONS_SET_REQUESTS OK: 0 set requests | set_requests=0

**OPERATIONS_GET_REQUESTS**

	OPERATIONS_GET_REQUESTS OK: 0 get resquests | get_requests=0

**BYTES_WRITTEN**

	BYTES_WRITTEN OK: 6171 bytes written | bytes_written=6171

**BYTES_READ**

	BYTES_READ OK: 66 bytes read | bytes_read=66

**BYTES_ALLOCATED**

	BYTES_ALLOCATED OK: 0 bytes allocated | bytes_allocated=0

### Check Redis

*python check_redis.py \<options\>*

**TOTAL_KEYS**

	TOTAL_KEYS OK: 8 total keys | total_keys=8;1000000;2000000

**MEMORY_USED**

	MEMORY_USED OK: 0MB used_memory | used_memory=0MB;2;4

**CURRENT_OPERATIONS**

	CURRENT_OPERATIONS OK: 10 commands | current_commands=10;20000;40000

**CHANGES_SINCE_LAST_SAVE**

	CHANGES_SINCE_LAST_SAVE OK: 0 changes since last save | changes=0;100;300

**AVERAGE_OPERATIONS_RATE**

	AVERAGE_OPERATIONS_RATE OK: 0 commands per second | average_rate=0;20000;40000

### Check Resque

*python check_resque.py \<options\>*

**QUEUE_LENGTH**

	QUEUE_LENGTH OK: 0 jobs in queues | total=0 default=0 critical=0 failing=0

**JOB_PROCESSED**

	JOB_PROCESSED OK: 0 jobs in processed | total=133

### Check Passenger

*python check_passegner.py \<options\>*

	usage: check_passenger.py [-h] [-w WARN] [-c CRIT] -t
                          {ACTIVE_PROCESSES,MAX_PROCESSES,RUNNING_PROCESSES}
                          [-d ROOTDIR] [-f FILENAME] [-p PID] [-z APPNAME]

**RUNNING_PROCESSES**

	RUNNING_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

**MAX_PROCESSES**

	MAX_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

**ACTIVE_PROCESSES**

	ACTIVE_PROCESSES UNKNOWN: ERROR: Phusion Passenger doesn't seem to be running.

##basic class to inherit from



##statsd wrapping

statsd.py