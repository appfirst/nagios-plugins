mvn clean package && mvn cargo:redeploy
mvn clean compile assembly:single


# AppFirst StatsD
    https://github.com/appfirst/statsd_clients/tree/stable/java

# v$sysstat names
    https://sites.google.com/site/oraclemonitor/v-sysstat-names
    
## physical reads
    This statistic stores the number of I/O requests to the operating system to retrieve a database block from the disk subsystem.
    This is a buffer cache miss. Logical reads is consistent gets + database block gets. Logical reads and physical reads is used 
    to calculate the buffer cache hit ratio.

## physical writes
    This statistic stores the number of I/O requests to the operating system to write a database block to the disk subsystem.
    The bulk of the writes are performed either by DBWR or LGWR.

# v$sysmetric_history , v$sysmetric , and v$sysmetric_summary
    displays the system metric values captured for the most current time interval for both the 
    long duration (60-second) and short duration (15-second) system metrics.
    
    
# v$session

    list of all sessions to identify active sessions with STATUS='ACTIVE' and how long it was running LAST_CALL_ET
    see running sql with SQL_ID or SQL_ADDR
    If session is waiting check WAIT columns for current wait details.
    V$PROCCES is mostly with SESS_ADDR to find process ID of Oracle background process and application process ID.
    V$SQLAREA and V$SQL provide text of SQL and more details for each SQL still in cache. 
    
    
#v$sql 
    ELAPSED_TIME/EXECUTIONS


http://www.pythian.com/blog/do-you-know-if-your-database-slow/