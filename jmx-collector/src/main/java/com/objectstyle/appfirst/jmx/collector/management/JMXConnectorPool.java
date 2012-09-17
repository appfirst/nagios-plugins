package com.objectstyle.appfirst.jmx.collector.management;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.management.remote.JMXConnector;
import javax.management.remote.JMXConnectorFactory;
import javax.management.remote.JMXServiceURL;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

class JMXConnectorPool {
    private static final Logger LOGGER = LoggerFactory.getLogger(JMXConnectorPool.class);

    private Map<JMXServiceURL, JMXConnector> connectors = new HashMap<JMXServiceURL, JMXConnector>();

    public JMXConnector get(JMXServiceURL url) throws IOException {
        if (connectors.containsKey(url)) {
            LOGGER.debug("Found JMX connector for URL {}", url);
            return connectors.get(url);
        }
        LOGGER.debug("Creating new JMX connector for URL {}", url);
        JMXConnector connector = JMXConnectorFactory.connect(url);
        connectors.put(url, connector);
        return connector;
    }

    public void remove(JMXServiceURL url) {
        LOGGER.debug("Removing JMX connector from the pool for URL {}", url);
        JMXConnector connector = connectors.remove(url);
        if (connector != null) {
            try {
                connector.close();
            } catch (IOException e) {
                LOGGER.warn("Error while removing JMX connector from the pool", e);
            }
        }
    }
}
