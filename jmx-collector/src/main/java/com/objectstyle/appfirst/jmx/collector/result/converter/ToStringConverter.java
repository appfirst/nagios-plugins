package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.MBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;

public class ToStringConverter implements MBeanDataConverter<String, Object> {
    @Override
    public ResultData convert(String type, Object value) {
        return new SimpleResultData(new SimpleTypeToStringConverter<Object>().convert(value));
    }
}
