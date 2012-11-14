package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.CompositeResultData;
import com.objectstyle.appfirst.jmx.collector.result.MBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import org.apache.commons.collections.MapUtils;

import java.util.Map;

public class MapConverter implements MBeanDataConverter<String, Map> {
    @Override
    @SuppressWarnings("unchecked")
    public ResultData convert(String type, Map value) {
        Map<String, String> result = MapUtils.transformedMap(
                value,
                new PrimitiveToStringTransformer("Unsupported data type '%s' for key inside java.lang.Map type"),
                new PrimitiveToStringTransformer("Unsupported data type '%s' for value inside java.lang.Map type")
        );
        return new CompositeResultData(result);
    }
}
