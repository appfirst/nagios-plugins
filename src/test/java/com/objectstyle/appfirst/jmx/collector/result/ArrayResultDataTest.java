package com.objectstyle.appfirst.jmx.collector.result;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import static junit.framework.Assert.assertEquals;

public class ArrayResultDataTest {
    @Test
    public void testToString() throws Exception {
        ArrayResultData data = new ArrayResultData("val", ImmutableList.of("1", "2", "3"));
        assertEquals("val0=1 val1=2 val2=3", data.toString());
        // yes. we are calling it two times...
        assertEquals("val0=1 val1=2 val2=3", data.toString());
    }
}
