package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.CompositeResultData;
import com.objectstyle.appfirst.jmx.collector.result.MBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.Primitives;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import static java.lang.String.format;

public class SetConverter implements MBeanDataConverter<String, Set> {
    private static final Logger LOGGER = LoggerFactory.getLogger(SetConverter.class);

    private SimpleTypeToStringConverter<Object> toStringConverter = new SimpleTypeToStringConverter<Object>();

    @Override
    public ResultData convert(String type, Set value) {
        Map<String, String> compositeValue = new HashMap<String, String>(value.size());

        int index = 1;
        for (Object item : value) {
            if (!Primitives.isPrimitiveOrWrapperType(item.getClass())) {
                LOGGER.warn(format("Unsupported data type '%s' inside java.lang.Set type", item.getClass().getName()));
            }
            compositeValue.put(SimpleResultData.DEFAULT_KEY + index, toStringConverter.convert(item));
            index++;
        }
        return new CompositeResultData(compositeValue);
    }
}
