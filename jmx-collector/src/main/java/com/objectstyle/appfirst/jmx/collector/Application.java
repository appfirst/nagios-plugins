package com.objectstyle.appfirst.jmx.collector;

import com.google.common.io.LineReader;
import com.objectstyle.appfirst.jmx.collector.config.CommandLinesSource;
import com.objectstyle.appfirst.jmx.collector.config.FileCommandLinesSource;
import com.objectstyle.appfirst.jmx.collector.execution.CommandsExecutionLifecycle;
import com.objectstyle.appfirst.jmx.collector.execution.CommandsUpdateLifecycle;
import com.objectstyle.appfirst.jmx.collector.management.ManagementConnectionFactory;
import com.objectstyle.appfirst.jmx.collector.output.AfCollectorOutput;
import com.objectstyle.appfirst.jmx.collector.output.Output;
import com.objectstyle.appfirst.jmx.collector.output.SysOutOutput;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class Application {
    private static final Logger LOGGER = LoggerFactory.getLogger(Application.class);

    private static final String APPFIRST_CONFIG_PATH_PROPERTY = "collector.appfirst.config";

    private static final String NAGIOS_CONFIG_PATH_PROPERTY = "collector.nagios.config";

    private static final String DEFAULT_APPFIRST_CONFIG_PATH = "/etc/AppFirst";

    private static final String OUTPUT_PROPERTY = "collector.output";

    private static final String SYSOUT_OUTPUT_KEY = "System.out";

    private static final int DEFAULT_CONFIGURATION_UPDATE_FREQUENCY = 30;

    private static final int DEFAULT_EXECUTION_FREQUENCY = 60;

    private static final String NAGIOS_CONFIG_PATH_KEY = "NagiosConfig";

    private static final String NAGIOS_FREQUENCY_KEY = "NagiosFreq";

    private static final String[] KNOWN_APPFIRST_PROPERTIES = {NAGIOS_CONFIG_PATH_KEY, NAGIOS_FREQUENCY_KEY};

    public static void main(String[] args) throws Exception {
        LOGGER.debug("Starting JMX collector");

        String nagiosConfigPath = System.getProperty(NAGIOS_CONFIG_PATH_PROPERTY);
        Map<String, String> appFirstProperties = getAppFirstProperties();

        if (nagiosConfigPath == null) {
            nagiosConfigPath = getNagiosConfigPath(appFirstProperties);
        }

        CommandLinesSource source;
        if (nagiosConfigPath != null) {
            source = new FileCommandLinesSource(new File(nagiosConfigPath));
        } else {
            LOGGER.error("Nagios config path should be provided. Exiting.");
            return;
        }

        Output output;
        String outputProperty = System.getProperty(OUTPUT_PROPERTY);
        if (outputProperty != null && outputProperty.equals(SYSOUT_OUTPUT_KEY)) {
            LOGGER.debug("Using System.out output");
            output = new SysOutOutput();
        } else {
            LOGGER.debug("Using AppFirst collector output");
            output = new AfCollectorOutput();
        }

        ManagementConnectionFactory managementConnectionFactory = new ManagementConnectionFactory();
        CommandsUpdateLifecycle updateLifecycle
                = new CommandsUpdateLifecycle(managementConnectionFactory, source, output);
        CommandsExecutionLifecycle executionLifecycle
                = new CommandsExecutionLifecycle(managementConnectionFactory, updateLifecycle.getCommands(), output);

        ScheduledExecutorService updateExecutorService = Executors.newSingleThreadScheduledExecutor(new ThreadFactory() {
            @Override
            public Thread newThread(Runnable runnable) {
                return new Thread(runnable, "update-lifecycle");
            }
        });
        LOGGER.debug("Scheduling update lifecycle");
        updateExecutorService.scheduleAtFixedRate(updateLifecycle,
                DEFAULT_CONFIGURATION_UPDATE_FREQUENCY, DEFAULT_CONFIGURATION_UPDATE_FREQUENCY, TimeUnit.SECONDS);

        ScheduledExecutorService executionExecutorService = Executors.newSingleThreadScheduledExecutor(new ThreadFactory() {
            @Override
            public Thread newThread(Runnable runnable) {
                return new Thread(runnable, "execution-lifecycle");
            }
        });
        LOGGER.debug("Scheduling execution lifecycle");
        final int executionFrequency = appFirstProperties.containsKey(NAGIOS_FREQUENCY_KEY)
                ? Integer.valueOf(appFirstProperties.get(NAGIOS_FREQUENCY_KEY)) : DEFAULT_EXECUTION_FREQUENCY;
        executionExecutorService.scheduleAtFixedRate(executionLifecycle,
                executionFrequency, executionFrequency, TimeUnit.SECONDS);
    }

    private static String getNagiosConfigPath(Map<String, String> properties) {
        String value = properties.get(NAGIOS_CONFIG_PATH_KEY);
        if (value != null) {
            // returning only first path
            value = value.split(",")[0].trim();
        }
        return value;
    }

    private static Map<String, String> getAppFirstProperties() throws IOException {
        String appfirstConfigPath = System.getProperty(APPFIRST_CONFIG_PATH_PROPERTY, DEFAULT_APPFIRST_CONFIG_PATH);

        Map<String, String> properties = new HashMap<String, String>();
        LineReader configReader = new LineReader(new FileReader(appfirstConfigPath));
        String configLine;
        while ((configLine = configReader.readLine()) != null) {
            configLine = configLine.trim();
            for (String key : KNOWN_APPFIRST_PROPERTIES) {
                if (configLine.startsWith(key)) {
                    String value = configLine.substring(key.length()).trim();
                    if (!value.isEmpty()) {
                        properties.put(key, value);
                    }
                }
            }
        }
        return properties;
    }
}
