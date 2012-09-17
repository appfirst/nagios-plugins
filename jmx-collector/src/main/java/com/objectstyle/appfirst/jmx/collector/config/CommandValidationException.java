package com.objectstyle.appfirst.jmx.collector.config;

public class CommandValidationException extends Exception {
    public CommandValidationException(String s) {
        super(s);
    }

    public CommandValidationException(String s, Throwable throwable) {
        super(s, throwable);
    }
}
