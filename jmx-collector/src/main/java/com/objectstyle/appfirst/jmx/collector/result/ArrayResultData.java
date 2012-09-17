package com.objectstyle.appfirst.jmx.collector.result;

import com.google.common.base.Function;
import com.google.common.base.Joiner;
import com.google.common.collect.Maps;

import javax.annotation.Nullable;
import java.util.List;

public class ArrayResultData extends ResultData {
    private final String keyPrefix;

    private final List<String> values;

    public ArrayResultData(String keyPrefix, List<String> values) {
        this.keyPrefix = keyPrefix;
        this.values = values;
    }

    @Override
    public String toString() {
        return Joiner.on(" ").withKeyValueSeparator("=").join(Maps.uniqueIndex(values, new Function<String, String>() {
            private int keyIndex = 0;

            @Override
            public String apply(@Nullable String input) {
                return String.format("%s%d", keyPrefix, keyIndex++);
            }
        }));
    }
}
