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
		JMXConnector connector = getConnector(url);
		if (connector == null) {
			LOGGER.debug("Creating new JMX connector for URL {}", url);
			connector = JMXConnectorFactory.connect(url);
			connectors.put(url, connector);
		}
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

	private JMXConnector getConnector(JMXServiceURL url) {
		JMXConnector connector = connectors.get(url);
		if (connector == null) {
			LOGGER.debug("JMX connector for URL {} was found", url);
			return null;
		}
		try {
			LOGGER.debug("Found JMX connector for URL {}", url);
			String connectionId = connector.getConnectionId();
			LOGGER.debug("Connection for URL {} with id {} is active.", url, connectionId);
			return connector;
		} catch (IOException e) {
			LOGGER.warn("Cannot get connection id. the connection was closed probably.", e);
			return null;
		}
	}
}
