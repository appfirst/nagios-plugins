package com.objectstyle.appfirst.jmx.collector.config;

import java.io.File;
import java.io.IOException;
import java.util.List;

public class FileCommandLinesSource extends SimpleCommandLinesSource {
    private final File file;

    private long lastModified = -1;

    public FileCommandLinesSource(File file) {
        super(new FileReaderInputSupplier(file));
        this.file = file;
    }

    @Override
    public boolean hasChanges() throws IOException {
        long newLastModified = file.lastModified();
        if (lastModified < newLastModified) {
            lastModified = newLastModified;
            return true;
        }
        return false;
    }

    @Override
    public List<String> readLines() throws IOException {
        lastModified = file.lastModified();
        return super.readLines();
    }
}
