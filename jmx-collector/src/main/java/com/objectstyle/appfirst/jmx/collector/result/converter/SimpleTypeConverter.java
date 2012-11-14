package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.OpenMBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;
import com.objectstyle.appfirst.jmx.collector.result.UnsupportedOpenTypeException;

import javax.management.openmbean.SimpleType;

public class SimpleTypeConverter<V> implements OpenMBeanDataConverter<SimpleType<V>, V> {
    private SimpleTypeToStringConverter<V> toStringConverter = new SimpleTypeToStringConverter<V>();

    @Override
    public ResultData convert(SimpleType<V> type, V value) throws UnsupportedOpenTypeException {
        return new SimpleResultData(toStringConverter.convert(value));
    }
}
