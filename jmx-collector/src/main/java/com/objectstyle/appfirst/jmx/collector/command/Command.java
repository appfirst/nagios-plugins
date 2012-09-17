package com.objectstyle.appfirst.jmx.collector.command;

import com.google.common.base.Objects;

public class Command {
    private final String name;

    private final VirtualMachineDefinition virtualMachineDefinition;

    private final ValueDefinition valueDefinition;

    private final ThresholdDefinition warningThresholdDefinition;

    private final ThresholdDefinition criticalThresholdDefinition;

    public Command(String name, VirtualMachineDefinition virtualMachineDefinition, ValueDefinition valueDefinition,
                   ThresholdDefinition warningThresholdDefinition, ThresholdDefinition criticalThresholdDefinition) {
        this.name = name;
        this.virtualMachineDefinition = virtualMachineDefinition;
        this.valueDefinition = valueDefinition;
        this.warningThresholdDefinition = warningThresholdDefinition;
        this.criticalThresholdDefinition = criticalThresholdDefinition;
    }

    public Command(String name, VirtualMachineDefinition virtualMachineDefinition, ValueDefinition valueDefinition) {
        this(name, virtualMachineDefinition, valueDefinition, new NoThresholdDefinition(), new NoThresholdDefinition());
    }

    public String getName() {
        return name;
    }

    public VirtualMachineDefinition getVirtualMachineDefinition() {
        return virtualMachineDefinition;
    }

    public ValueDefinition getValueDefinition() {
        return valueDefinition;
    }

    public ThresholdDefinition getWarningThresholdDefinition() {
        return warningThresholdDefinition;
    }

    public ThresholdDefinition getCriticalThresholdDefinition() {
        return criticalThresholdDefinition;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("name", name)
                .add("virtualMachineDefinition", virtualMachineDefinition)
                .add("valueDefinition", valueDefinition)
                .toString();
    }
}
