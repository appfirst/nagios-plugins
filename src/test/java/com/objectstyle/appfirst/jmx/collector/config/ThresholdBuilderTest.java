package com.objectstyle.appfirst.jmx.collector.config;

import com.objectstyle.appfirst.jmx.collector.command.RangeThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ThresholdDefinition;
import org.junit.Test;

import static org.junit.Assert.*;

public class ThresholdBuilderTest {
    @Test
    public void testFromString() throws Exception {
        ThresholdBuilder builder = new ThresholdBuilder();
        ThresholdDefinition thresholdDefinition = builder.fromString("10");
        assertTrue(thresholdDefinition instanceof RangeThresholdDefinition);

        RangeThresholdDefinition definition = ((RangeThresholdDefinition) thresholdDefinition);
        assertEquals(0, definition.getLeftBorder());
        assertEquals(10, definition.getRightBorder());
        assertFalse(definition.isInside());

        definition = (RangeThresholdDefinition) builder.fromString("10:");
        assertEquals(10, definition.getLeftBorder());
        assertEquals(Long.MAX_VALUE, definition.getRightBorder());
        assertFalse(definition.isInside());

        definition = (RangeThresholdDefinition) builder.fromString("~:10");
        assertEquals(Long.MIN_VALUE, definition.getLeftBorder());
        assertEquals(10, definition.getRightBorder());
        assertFalse(definition.isInside());

        definition = (RangeThresholdDefinition) builder.fromString("10:20");
        assertEquals(10, definition.getLeftBorder());
        assertEquals(20, definition.getRightBorder());
        assertFalse(definition.isInside());

        definition = (RangeThresholdDefinition) builder.fromString("@10:20");
        assertEquals(10, definition.getLeftBorder());
        assertEquals(20, definition.getRightBorder());
        assertTrue(definition.isInside());


    }
}
