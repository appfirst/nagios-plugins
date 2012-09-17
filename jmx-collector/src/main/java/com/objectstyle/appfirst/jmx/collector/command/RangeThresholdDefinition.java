package com.objectstyle.appfirst.jmx.collector.command;

public class RangeThresholdDefinition extends ThresholdDefinition {
    private final long leftBorder;

    private final long rightBorder;

    private final boolean inside;

    public RangeThresholdDefinition(long leftBorder, long rightBorder) {
        this(leftBorder, rightBorder, false);
    }

    public RangeThresholdDefinition(long leftBorder, long rightBorder, boolean inside) {
        this.leftBorder = leftBorder;
        this.rightBorder = rightBorder;
        this.inside = inside;
    }

    public long getLeftBorder() {
        return leftBorder;
    }

    public long getRightBorder() {
        return rightBorder;
    }

    public boolean isInside() {
        return inside;
    }
}
