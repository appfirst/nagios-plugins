AppFirst's Oracle DB metrics 
=====================

A module for pulling metrics of Oracle DB in Nagios format to AF and to get a list of SQLs that was executed at Oracle DB.
To get metrics you should add to "Polled Data Config" command:
`command[oracle.metric_name]=/usr/share/appfirst/plugins/libexec/af.oracle.metrics/get_oracle_metric.sh`

or 

`command[oracle.metric_name] java -jar  /usr/share/appfirst/plugins/libexec/af.oracle.metrics/af.oracle.metrics-0.1.0-jar-with-dependencies.jar`
    -D "DB url" -L "/path/to/log/file.log" -U "user" -P "password" -M "standart_metric_name" -N "specific_metric_name1;specific_metric_name2"`

* Recommended install path: `/usr/share/appfirst/plugins/libexec/`
* ` -h` will detail configuration flags


Common Metrics
-----------
`java -jar  af.oracle.metrics-0.1.0-jar-with-dependencies.jar -D "DB url" -L "/path/to/log/file.log" -U "user" -P "password" -M "standart_metric_name" -N "specific_metric_name"`

## Options
 `-D` - Oracle Database path in format: jdbc:oracle:thin:@[host]:[port:1521]:[DB name]
 `-U` - Oracle Database user
 `-P` - Oracle Database password
 `-M` - Common metric name to get
 `-N` - Specific metric name to get, for exmple "Current Logons Count"
 `-L` - Path to output log file can be used in debug mode


# List of specific metrics:
* Buffer Cache Hit Ratio 100: % (LogRead - PhyRead)/LogRead
* Memory Sorts Ratio 100: % MemSort/(MemSort + DiskSort)
* Redo Allocation Hit Ratio 100: % (#Redo - RedoSpaceReq)/#Redo
* User Transaction Per Sec 0: Transactions Per Second
* Physical Reads Per Sec 0: Reads Per Second
* Physical Reads Per Txn 0: Reads Per Txn
* Physical Writes Per Sec 0: Writes Per Second
* Physical Writes Per Txn 1: Writes Per Txn
* Physical Reads Direct Per Sec 0: Reads Per Second
* Physical Reads Direct Per Txn 0: Reads Per Txn
* Physical Writes Direct Per Sec 0: Writes Per Second
* Physical Writes Direct Per Txn 0: Writes Per Txn
* Physical Reads Direct Lobs Per Sec 0: Reads Per Second
* Physical Reads Direct Lobs Per Txn 0: Reads Per Txn
* Physical Writes Direct Lobs Per Sec 0: Writes Per Second
* Physical Writes Direct Lobs  Per Txn 0: Writes Per Txn
* Redo Generated Per Sec 248: Bytes Per Second
* Redo Generated Per Txn 2489: Bytes Per Txn
* Logons Per Sec 0: Logons Per Second
* Logons Per Txn 0: Logons Per Txn
* Open Cursors Per Sec 2: Cursors Per Second
* Open Cursors Per Txn 28: Cursors Per Txn
* User Commits Per Sec 0: Commits Per Second
* User Commits Percentage 100: % (UserCommit/TotalUserTxn)
* User Rollbacks Per Sec 0: Rollbacks Per Second
* User Rollbacks Percentage 0: % (UserRollback/TotalUserTxn)
* User Calls Per Sec 0: Calls Per Second
* User Calls Per Txn 2: Calls Per Txn
* Recursive Calls Per Sec 30: Calls Per Second
* Recursive Calls Per Txn 308: Calls Per Txn
* Logical Reads Per Sec 11: Reads Per Second
* Logical Reads Per Txn 119: Reads Per Txn
* DBWR Checkpoints Per Sec 0: Check Points Per Second
* Background Checkpoints Per Sec 0: Check Points Per Second
* Redo Writes Per Sec 0: Writes Per Second
* Redo Writes Per Txn 1: Writes Per Txn
* Long Table Scans Per Sec 0: Scans Per Second
* Long Table Scans Per Txn 0: Scans Per Txn
* Total Table Scans Per Sec 0: Scans Per Second
* Total Table Scans Per Txn 3: Scans Per Txn
* Full Index Scans Per Sec 0: Scans Per Second
* Full Index Scans Per Txn 0: Scans Per Txn
* Total Index Scans Per Sec 4: Scans Per Second
* Total Index Scans Per Txn 40: Scans Per Txn
* Total Parse Count Per Sec 1: Parses Per Second
* Total Parse Count Per Txn 10: Parses Per Txn
* Hard Parse Count Per Sec 0: Parses Per Second
* Hard Parse Count Per Txn 0: Parses Per Txn
* Parse Failure Count Per Sec 0: Parses Per Second
* Parse Failure Count Per Txn 0: Parses Per Txn
* Cursor Cache Hit Ratio 190: % CursorCacheHit/SoftParse
* Disk Sort Per Sec 0: Sorts Per Second
* Disk Sort Per Txn 0: Sorts Per Txn
* Rows Per Sort 1: Rows Per Sort
* Execute Without Parse Ratio 66: % (ExecWOParse/TotalExec)
* Soft Parse Ratio 98: % SoftParses/TotalParses
* User Calls Ratio 0: % UserCalls/AllCalls
* Host CPU Utilization (%) 6: % Busy/(Idle+Busy)
* Network Traffic Volume Per Sec 67: Bytes Per Second
* Enqueue Timeouts Per Sec 0: Timeouts Per Second
* Enqueue Timeouts Per Txn 0: Timeouts Per Txn
* Enqueue Waits Per Sec 0: Waits Per Second
* Enqueue Waits Per Txn 0: Waits Per Txn
* Enqueue Deadlocks Per Sec 0: Deadlocks Per Second
* Enqueue Deadlocks Per Txn 0: Deadlocks Per Txn
* Enqueue Requests Per Sec 9: Requests Per Second
* Enqueue Requests Per Txn 99: Requests Per Txn
* DB Block Gets Per Sec 1: Blocks Per Second
* DB Block Gets Per Txn 15: Blocks Per Txn
* Consistent Read Gets Per Sec 10: Blocks Per Second
* Consistent Read Gets Per Txn 104: Blocks Per Txn
* DB Block Changes Per Sec 1: Blocks Per Second
* DB Block Changes Per Txn 15: Blocks Per Txn
* Consistent Read Changes Per Sec 0: Blocks Per Second
* Consistent Read Changes Per Txn 0: Blocks Per Txn
* CPU Usage Per Sec 0: CentiSeconds Per Second
* CPU Usage Per Txn 4: CentiSeconds Per Txn
* CR Blocks Created Per Sec 0: Blocks Per Second
* CR Blocks Created Per Txn 0: Blocks Per Txn
* CR Undo Records Applied Per Sec 0: Undo Records Per Second
* CR Undo Records Applied Per Txn 0: Records Per Txn
* User Rollback UndoRec Applied Per Sec 0: Records Per Second
* User Rollback Undo Records Applied Per Txn 0: Records Per Txn
* Leaf Node Splits Per Sec 0: Splits Per Second
* Leaf Node Splits Per Txn 0: Splits Per Txn
* Branch Node Splits Per Sec 0: Splits Per Second
* Branch Node Splits Per Txn 0: Splits Per Txn
* PX downgraded 1 to 25% Per Sec 0: PX Operations Per Second
* PX downgraded 25 to 50% Per Sec 0: PX Operations Per Second
* PX downgraded 50 to 75% Per Sec 0: PX Operations Per Second
* PX downgraded 75 to 99% Per Sec 0: PX Operations Per Second
* PX downgraded to serial Per Sec 0: PX Operations Per Second
* Physical Read Total IO Requests Per Sec 1: Requests Per Second
* Physical Read Total Bytes Per Sec 29471: Bytes Per Second
* GC CR Block Received Per Second 0: Blocks Per Second
* GC CR Block Received Per Txn 0: Blocks Per Txn
* GC Current Block Received Per Second 0: Blocks Per Second
* GC Current Block Received Per Txn 0: Blocks Per Txn
* Global Cache Average CR Get Time 0: CentiSeconds Per Get
* Global Cache Average Current Get Time 0: CentiSeconds Per Get
* Physical Write Total IO Requests Per Sec 0: Requests Per Second
* Global Cache Blocks Corrupted 0: Blocks
* Global Cache Blocks Lost 0: Blocks
* Current Logons Count 24: Logons
* Current Open Cursors Count 28: Cursors
* User Limit % 0: % Sessions/License_Limit
* SQL Service Response Time 0: CentiSeconds Per Call
* Database Wait Time Ratio 0: % Wait/DB_Time
* Database CPU Time Ratio 122: % Cpu/DB_Time
* Response Time Per Txn 3: CentiSeconds Per Txn
* Row Cache Hit Ratio 100: % Hits/Gets
* Row Cache Miss Ratio 0: % Misses/Gets
* Library Cache Hit Ratio 98: % Hits/Pins
* Library Cache Miss Ratio 1: % Misses/Gets
* Shared Pool Free % 14: % Free/Total
* PGA Cache Hit % 99: % Bytes/TotalBytes
* Process Limit % 18: % Processes/Limit
* Session Limit % 12: % Sessions/Limit
* Executions Per Txn 31: Executes Per Txn
* Executions Per Sec 3: Executes Per Second
* Txns Per Logon 1: Txns Per Logon
* Database Time Per Sec 0: CentiSeconds Per Second
* Physical Write Total Bytes Per Sec 12305: Bytes Per Second
* Physical Read IO Requests Per Sec 0: Requests Per Second
* Physical Read Bytes Per Sec 0: Bytes Per Second
* Physical Write IO Requests Per Sec 0: Requests Per Second
* Physical Write Bytes Per Sec 1091: Bytes Per Second
* DB Block Changes Per User Call 5: Blocks Per Call
* DB Block Gets Per User Call 5: Blocks Per Call
* Executions Per User Call 11: Executes Per Call
* Logical Reads Per User Call 42: Reads Per Call
* Total Sorts Per User Call 15: Sorts Per Call
* Total Table Scans Per User Call 1: Tables Per Call
* Current OS Load 0: Number Of Processes
* Streams Pool Usage Percentage 0: % Memory allocated / Size of Streams pool
* PQ QC Session Count 0: Sessions
* PQ Slave Session Count 0: Sessions
* Queries parallelized Per Sec 0: Queries Per Second
* DML statements parallelized Per Sec 0: Statements Per Second
* DDL statements parallelized Per Sec 0: Statements Per Second
* PX operations not downgraded Per Sec 0: PX Operations Per Second
* Session Count 31: Sessions
* Average Synchronous Single-Block Read Latency 0: Milliseconds
* I/O Megabytes per Second 0: Megabtyes per Second
* I/O Requests per Second 2: Requests per Second
* Average Active Sessions 0: Active Sessions
* Active Serial Sessions 1: Sessions
* Active Parallel Sessions 0: Sessions
* Captured user calls 0: calls
* Replayed user calls 0: calls
* Workload Capture and Replay status 0: status
* Background CPU Usage Per Sec 0: CentiSeconds Per Second
* Background Time Per Sec 0: Active Sessions
* Host CPU Usage Per Sec 24: CentiSeconds Per Second
* Cell Physical IO Interconnect Bytes 2508288: bytes
* Temp Space Used 11534336: bytes
* Total PGA Allocated 72461312: bytes
* Total PGA Used by SQL Workareas 0: bytes
