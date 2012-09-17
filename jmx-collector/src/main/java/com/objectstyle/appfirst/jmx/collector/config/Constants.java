package com.objectstyle.appfirst.jmx.collector.config;

class Constants {
    static final String COMMAND_KEYWORD = "jmx_command";
    static final String ATTRIBUTE_KEY_PREFIX = "-";
    static final String VIRTUAL_MACHINE_MATCH_PATTERN_KEY = ATTRIBUTE_KEY_PREFIX + "P";
    static final String MBEAN_NAME_KEY = ATTRIBUTE_KEY_PREFIX + "O";
    static final String MBEAN_ATTRIBUTE_KEY = ATTRIBUTE_KEY_PREFIX + "A";
    static final String MBEAN_ATTRIBUTE_KEY_KEY = ATTRIBUTE_KEY_PREFIX + "K";
    static final String VIRTUAL_MACHINE_URL_KEY = ATTRIBUTE_KEY_PREFIX + "U";
    static final String WARNING_THRESHOLD_KEY = ATTRIBUTE_KEY_PREFIX + "W";
    static final String CRITICAL_THRESHOLD_KEY = ATTRIBUTE_KEY_PREFIX + "C";
}
