package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.objectstyle.appfirst.jmx.collector.result.Primitives;
import org.apache.commons.collections.Transformer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PrimitiveToStringTransformer implements Transformer {
    private static final Logger LOGGER = LoggerFactory.getLogger(PrimitiveToStringTransformer.class);

    private final String errorMessage;

    public PrimitiveToStringTransformer(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    @Override
    public Object transform(Object input) {
        if (!Primitives.isPrimitiveOrWrapperType(input.getClass())) {
            LOGGER.error(String.format(errorMessage, input.getClass().getName()));
        }
        return new SimpleTypeToStringConverter<Object>().convert(input);
    }
}
