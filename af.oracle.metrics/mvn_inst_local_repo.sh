#!/bin/bash

mvn install:install-file -DgroupId=com.appfirst -DartifactId=java_statsd_client -Dversion=0.3 -Dpackaging=jar -Dfile=libs/java_statsd_client-0.0.3-jar-with-dependencies.jar