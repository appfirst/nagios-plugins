package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.openmbean.SimpleType;

public class SimpleTypeConverter<V> implements OpenMBeanDataConverter<SimpleType<V>, V> {
    private SimpleTypeToStringConverter<V> toStringConverter = new SimpleTypeToStringConverter<V>();

    @Override
    public ResultData convert(SimpleType<V> type, V value) throws UnsupportedOpenTypeException {
        return new SimpleResultData("val", toStringConverter.convert(value));
    }
}
