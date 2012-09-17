package com.objectstyle.appfirst.jmx.collector.result;

import static java.lang.String.format;

public class UnsupportedDataTypeException extends Exception {
    private final String type;

    public UnsupportedDataTypeException(String type) {
        super(format("Unsupported data type '%s'", type));
        this.type = type;
    }

    public String getType() {
        return type;
    }
}
