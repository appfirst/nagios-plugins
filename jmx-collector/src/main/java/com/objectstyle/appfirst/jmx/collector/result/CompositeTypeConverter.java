package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.openmbean.CompositeData;
import javax.management.openmbean.CompositeType;
import javax.management.openmbean.OpenType;
import javax.management.openmbean.SimpleType;
import java.util.HashMap;
import java.util.Map;

public class CompositeTypeConverter implements OpenMBeanDataConverter<CompositeType, CompositeData> {
    private SimpleTypeToStringConverter<Object> toStringConverter = new SimpleTypeToStringConverter<Object>();

    @Override
    public ResultData convert(CompositeType type, CompositeData value) throws UnsupportedOpenTypeException {
        Map<String, String> valueMap = new HashMap<String, String>();
        for (String key : type.keySet()) {
            OpenType<?> itemType = type.getType(key);
            if (!(itemType instanceof SimpleType<?>)) {
                throw new UnsupportedOpenTypeException(itemType);
            }
            valueMap.put(key, toStringConverter.convert(value.get(key)));
        }
        return new CompositeResultData(valueMap);
    }
}
