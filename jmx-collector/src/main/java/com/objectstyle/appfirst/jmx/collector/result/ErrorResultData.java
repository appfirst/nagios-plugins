package com.objectstyle.appfirst.jmx.collector.result;

public class ErrorResultData extends ResultData {
    private final String message;

    public ErrorResultData(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return message;
    }
}
