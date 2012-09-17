package com.objectstyle.appfirst.jmx.collector.command;

import com.google.common.base.Objects;

public class CompositeValueDefinition extends ValueDefinition {
    private String attributeKey;

    public CompositeValueDefinition(String name, String attribute, String attributeKey) {
        super(name, attribute);
        this.attributeKey = attributeKey;
    }

    public String getAttributeKey() {
        return attributeKey;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("name", getName())
                .add("attribute", getAttribute())
                .add("attributeKey", attributeKey)
                .toString();
    }
}
