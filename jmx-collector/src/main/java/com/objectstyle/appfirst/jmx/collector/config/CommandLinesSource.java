package com.objectstyle.appfirst.jmx.collector.config;

import java.io.IOException;
import java.util.List;

public interface CommandLinesSource {
    List<String> readLines() throws IOException;

    boolean hasChanges() throws IOException;
}
