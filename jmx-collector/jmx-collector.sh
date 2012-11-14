#!/bin/bash

if [ ! $JAVA_HOME ]
then
	echo 'You must privide JAVA_HOME enveronment variable'
	exit
fi


LD_LIBRARY_PATH=/usr/share/appfirst:$JAVA_HOME/jre/lib ${JAVA_HOME}/bin/java -cp .:${JAVA_HOME}/lib/jconsole.jar:${JAVA_HOME}/lib/tools.jar:appfirst-jmx-0.4-jar-with-dependencies.jar com.objectstyle.appfirst.jmx.collector.Application

