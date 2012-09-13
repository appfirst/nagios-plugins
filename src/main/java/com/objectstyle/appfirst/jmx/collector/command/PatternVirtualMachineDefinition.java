package com.objectstyle.appfirst.jmx.collector.command;

import com.google.common.base.Objects;

public class PatternVirtualMachineDefinition extends VirtualMachineDefinition {
    private final String matchPattern;

    public PatternVirtualMachineDefinition(String matchPattern) {
        this.matchPattern = matchPattern;
    }

    public String getMatchPattern() {
        return matchPattern;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("matchPattern", matchPattern)
                .toString();
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(matchPattern);
    }
}
