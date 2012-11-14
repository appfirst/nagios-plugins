package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.openmbean.OpenType;

import static java.lang.String.format;

public class UnsupportedOpenTypeException extends UnsupportedDataTypeException {
    public UnsupportedOpenTypeException(OpenType<?> type) {
        super(format("Unsupported data type '%s'", type.getTypeName()));
    }
}
