package com.objectstyle.appfirst.jmx.collector.result;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;

import static junit.framework.Assert.assertEquals;

public class CompositeResultDataTest {
    @Test
    public void testToString() throws Exception {
        assertEquals("key1=1 key2=2 key3=3",
                new CompositeResultData(ImmutableMap.of("key1", "1", "key2", "2", "key3", "3")).toString());
    }
}
