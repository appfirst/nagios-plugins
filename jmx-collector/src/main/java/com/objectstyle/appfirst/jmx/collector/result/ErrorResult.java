package com.objectstyle.appfirst.jmx.collector.result;

public class ErrorResult extends Result {
    public ErrorResult(String name, String message) {
        this(name, new ErrorResultData(message));
    }

    public ErrorResult(String name, ErrorResultData errorResultData) {
        super(name, ResultStatus.EXECUTION_ERROR, errorResultData);
    }

    @Override
    public String toString() {
        return super.toString();
    }
}
