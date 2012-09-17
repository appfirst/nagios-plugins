package com.objectstyle.appfirst.jmx.collector.config;

public interface CommandLineProcessor {
    void startCommand(String commandName);

    void endCommand();

    void startVirtualMachineMatchPattern(String virtualMachineMatchPattern);

    void startVirtualMachineURL(String virtualMachineURL);

    void startMBeanName(String mBeanName);

    void startMBeanAttribute(String mBeanAttribute);

    void startMBeanAttributeKey(String mBeanAttributeKey);

    void startWarningThreshold(String value);

    void startCriticalThreshold(String value);
}
