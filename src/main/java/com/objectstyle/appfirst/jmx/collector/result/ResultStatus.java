package com.objectstyle.appfirst.jmx.collector.result;

public enum ResultStatus {
    REGULAR(0, "OK"),
    WARNING_THRESHOLD(1, "Warning"),
    CRITICAL_THRESHOLD(2, "Critical"),
    EXECUTION_ERROR(3, "Unknown");

    private final int nagiosIntValue;

    private final String nagiosStringValue;

    private ResultStatus(int nagiosIntValue, String nagiosStringValue) {
        this.nagiosIntValue = nagiosIntValue;
        this.nagiosStringValue = nagiosStringValue;
    }

    public int getNagiosIntValue() {
        return nagiosIntValue;
    }

    public String getNagiosStringValue() {
        return nagiosStringValue;
    }
}
