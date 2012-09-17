package com.objectstyle.appfirst.jmx.collector.command;

import com.google.common.base.Objects;

public class ValueDefinition {
    private String name;

    private String attribute;

    public ValueDefinition(String name, String attribute) {
        this.name = name;
        this.attribute = attribute;
    }

    public String getName() {
        return name;
    }

    public String getAttribute() {
        return attribute;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("name", name)
                .add("attribute", attribute)
                .toString();
    }
}
