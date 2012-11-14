#!/bin/bash

if [ ! $JAVA_HOME ]
then
	echo 'Please specify JAVA_HOME environment variable'
	exit
fi


LD_LIBRARY_PATH=/usr/share/appfirst:$JAVA_HOME/jre/lib ${JAVA_HOME}/bin/java -cp .:${JAVA_HOME}/lib/jconsole.jar:${JAVA_HOME}/lib/tools.jar:appfirst-jmx-0.4-jar-with-dependencies.jar com.objectstyle.appfirst.jmx.collector.Application

