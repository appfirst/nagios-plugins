package com.objectstyle.appfirst.jmx.collector.config;

import com.google.common.io.InputSupplier;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class FileReaderInputSupplier implements InputSupplier<Readable> {
    private final File file;

    public FileReaderInputSupplier(File file) {
        this.file = file;
    }

    @Override
    public Readable getInput() throws IOException {
        return new FileReader(file);
    }
}
