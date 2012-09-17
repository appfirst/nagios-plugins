package com.objectstyle.appfirst.jmx.collector.result;

public class SimpleResultData extends ResultData {
    private final String key;

    private final String value;

    public SimpleResultData(String key, String value) {
        this.key = key;
        this.value = value;
    }

    @Override
    public String toString() {
        return String.format("%s=%s", key, value);
    }

    public String getValue() {
        return value;
    }
}
