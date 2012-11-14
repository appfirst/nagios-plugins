package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.CompositeResultData;
import com.objectstyle.appfirst.jmx.collector.result.OpenMBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.UnsupportedOpenTypeException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.management.openmbean.CompositeData;
import javax.management.openmbean.CompositeType;
import javax.management.openmbean.OpenType;
import javax.management.openmbean.SimpleType;
import java.util.HashMap;
import java.util.Map;

import static java.lang.String.format;

public class CompositeTypeConverter implements OpenMBeanDataConverter<CompositeType, CompositeData> {
    private static final Logger LOGGER = LoggerFactory.getLogger(CompositeTypeConverter.class);

    private SimpleTypeToStringConverter<Object> toStringConverter = new SimpleTypeToStringConverter<Object>();

    @Override
    public ResultData convert(CompositeType type, CompositeData value) throws UnsupportedOpenTypeException {
        Map<String, String> valueMap = new HashMap<String, String>();
        for (String key : type.keySet()) {
            OpenType<?> itemType = type.getType(key);
            if (!(itemType instanceof SimpleType<?>)) {
                LOGGER.warn(format("Unsupported data type '%s' inside CompositeType bean.", itemType));
            }
            valueMap.put(key, toStringConverter.convert(value.get(key)));
        }
        return new CompositeResultData(valueMap);
    }
}
