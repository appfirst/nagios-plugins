package com.objectstyle.appfirst.jmx.collector.config;

import com.objectstyle.appfirst.jmx.collector.command.*;

import javax.management.remote.JMXServiceURL;
import java.net.MalformedURLException;

public class CommandBuilder implements CommandLineProcessor {
    private final ThresholdBuilder thresholdBuilder = new ThresholdBuilder();

    private String commandName;

    private String mBeanName;

    private String mBeanAttribute;

    private String mBeanAttributeKey;

    private String virtualMachineMatchPattern;

    private String virtualMachineURL;

    private String warningThreshold;

    private String criticalThreshold;

    private boolean built;

    @Override
    public void startCommand(String commandName) {
        this.commandName = commandName;
        mBeanName = null;
        mBeanAttribute = null;
        mBeanAttributeKey = null;
        virtualMachineMatchPattern = null;
        virtualMachineURL = null;
        warningThreshold = null;
        criticalThreshold = null;
        built = false;
    }

    @Override
    public void endCommand() {
        built = true;
    }

    @Override
    public void startVirtualMachineMatchPattern(String virtualMachineMatchPattern) {
        this.virtualMachineMatchPattern = virtualMachineMatchPattern;
    }

    @Override
    public void startVirtualMachineURL(String virtualMachineURL) {
        this.virtualMachineURL = virtualMachineURL;
    }

    @Override
    public void startMBeanName(String mBeanName) {
        this.mBeanName = mBeanName;
    }

    @Override
    public void startMBeanAttribute(String mBeanAttribute) {
        this.mBeanAttribute = mBeanAttribute;
    }

    @Override
    public void startMBeanAttributeKey(String mBeanAttributeKey) {
        this.mBeanAttributeKey = mBeanAttributeKey;
    }

    @Override
    public void startWarningThreshold(String value) {
        this.warningThreshold = value;
    }

    @Override
    public void startCriticalThreshold(String value) {
        this.criticalThreshold = value;
    }

    public Command buildCommand() throws CommandValidationException {
        if (!built) {
            throw new IllegalStateException("Command has not been built yet");
        }
        VirtualMachineDefinition virtualMachineDefinition;
        if (virtualMachineMatchPattern != null) {
            virtualMachineDefinition = new PatternVirtualMachineDefinition(virtualMachineMatchPattern);
        } else if (virtualMachineURL != null) {
            try {
                virtualMachineDefinition = new URLVirtualMachineDefinition(new JMXServiceURL(virtualMachineURL));
            } catch (MalformedURLException e) {
                throw new CommandValidationException("Malformed URL", e);
            }
        } else {
            throw new CommandValidationException("Virtual machine pattern or URL are not provided");
        }
        ValueDefinition valueDefinition;
        if (mBeanName == null) {
            throw new CommandValidationException("Object name is not provided");
        }
        if (mBeanAttribute == null) {
            throw new CommandValidationException("Object attribute name is not provided");
        }
        if (mBeanAttributeKey != null) {
            valueDefinition = new CompositeValueDefinition(mBeanName, mBeanAttribute, mBeanAttributeKey);
        } else {
            valueDefinition = new ValueDefinition(mBeanName, mBeanAttribute);
        }
        ThresholdDefinition warningThresholdDefinition = thresholdBuilder.fromString(warningThreshold);
        ThresholdDefinition criticalThresholdDefinition = thresholdBuilder.fromString(criticalThreshold);
        return new Command(commandName, virtualMachineDefinition, valueDefinition,
                warningThresholdDefinition, criticalThresholdDefinition);
    }
}
