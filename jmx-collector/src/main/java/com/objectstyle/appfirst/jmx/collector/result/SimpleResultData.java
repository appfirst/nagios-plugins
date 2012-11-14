package com.objectstyle.appfirst.jmx.collector.result;

public class SimpleResultData extends ResultData {
    public static final String DEFAULT_KEY = "val";

    private final String key;

    private final String value;

    public SimpleResultData(String key, String value) {
        this.key = key;
        this.value = value;
    }
    public SimpleResultData(String value) {
        this(DEFAULT_KEY, value);
    }

    @Override
    public String toString() {
        return String.format("%s=%s", key, value);
    }

    public String getValue() {
        return value;
    }
}
