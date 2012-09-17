package com.objectstyle.appfirst.jmx.collector.result;

import com.google.common.base.Function;
import com.google.common.base.Joiner;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;

import java.util.Map;

import static com.google.common.collect.Collections2.transform;
import static java.lang.String.format;

public class CompositeResultData extends ResultData {
    private final Map<String, String> values;

    public CompositeResultData(Map<String, String> values) {
        this.values = values;
    }

    public boolean containsKey(String key) {
        return values.containsKey(key);
    }

    @Override
    public String toString() {
        return Joiner.on(" ").withKeyValueSeparator("=").join(transform(values.entrySet(), new Function<Map.Entry<String, String>, Map.Entry<String, String>>() {
            @Override
            public Map.Entry<String, String> apply(Map.Entry<String, String> input) {
                return Maps.immutableEntry(format("%s", input.getKey()), input.getValue());
            }
        }));
    }

    public CompositeResultData forSingleKey(String key) {
        return new CompositeResultData(ImmutableMap.of(key, values.get(key)));
    }
}
