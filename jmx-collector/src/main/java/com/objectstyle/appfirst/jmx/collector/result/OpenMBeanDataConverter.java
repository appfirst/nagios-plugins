package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.openmbean.OpenType;

public interface OpenMBeanDataConverter<T extends OpenType<V>, V> extends MBeanDataConverter<T, V> {
}
