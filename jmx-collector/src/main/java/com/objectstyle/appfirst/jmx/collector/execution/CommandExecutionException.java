package com.objectstyle.appfirst.jmx.collector.execution;

public class CommandExecutionException extends Exception {
    public CommandExecutionException(String s) {
        super(s);
    }

    public CommandExecutionException(String s, Throwable throwable) {
        super(s, throwable);
    }

    public CommandExecutionException(Throwable throwable) {
        super(String.format("Error while executing command"), throwable);
    }
}
