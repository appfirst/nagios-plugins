#!/bin/bash

if [ ! $JAVA_HOME ]
then
	echo 'You must privide JAVA_HOME enveronment variable'
	exit
fi

cd `dirname $0`
LD_LIBRARY_PATH=/usr/share/appfirst/ ${JAVA_HOME}/bin/java -cp .:${JAVA_HOME}/lib/tools.jar:appfirst-jmx-0.2-jar-with-dependencies.jar:appfirst-jmx-0.2.jar com.objectstyle.appfirst.jmx.collector.Application
