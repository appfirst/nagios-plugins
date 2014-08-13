#!/bin/bash

afPath="target"
dbUrl="jdbc:oracle:thin:@192.168.1.66:1521:oracle"
dbUser="orc_test"
dbPass="7012296AA"
logPath="af.oracle.metrics.log"
metricName="cpu"
#metricName="sqls"
interval="5"

##java -jar target/af.oracle.metrics-0.1.0-jar-with-dependencies.jar
java -jar  $afPath/af.oracle.metrics-0.1.0-jar-with-dependencies.jar -I $interval  -D $dbUrl -L $logPath -U $dbUser -P $dbPass -M $metricName


#command[oracle.io] java -jar  /home/appfirst/af.oracle/af.oracle.metrics-0.1.0-jar-with-dependencies.jar -D "jdbc:oracle:thin:@10.53.55.206:1521:ACRTEST" -U "hr" -P "AcrTek08" -M "custom" -N "User Transaction Per Sec"

