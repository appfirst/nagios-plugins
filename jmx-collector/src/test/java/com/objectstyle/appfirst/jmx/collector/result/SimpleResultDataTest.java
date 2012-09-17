package com.objectstyle.appfirst.jmx.collector.result;

import org.junit.Test;

import static junit.framework.Assert.assertEquals;

public class SimpleResultDataTest {
    @Test
    public void testToString() throws Exception {
        assertEquals("val=1", new SimpleResultData("val", "1").toString());
        assertEquals("key=2", new SimpleResultData("key", "2").toString());
    }
}
