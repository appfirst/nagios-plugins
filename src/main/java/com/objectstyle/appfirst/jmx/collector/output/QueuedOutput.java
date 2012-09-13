package com.objectstyle.appfirst.jmx.collector.output;

import com.objectstyle.appfirst.jmx.collector.result.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;

public abstract class QueuedOutput implements Output {
    private static final Logger LOGGER = LoggerFactory.getLogger(QueuedOutput.class);

    private final BlockingQueue<Result> results;

    private class ResultsWriteRunnable implements Runnable {
        @Override
        public void run() {
            while (true) {
                try {
                    LOGGER.debug("Waiting for result to write");
                    Result result = results.take();
                    LOGGER.debug("Took result from the queue: {}", result);
                    doWrite(result);
                } catch (InterruptedException e) {
                    LOGGER.warn("Result send has been interrupted", e);
                } catch (Throwable th) {
                    LOGGER.error("Error while writing result", th);
                }
            }
        }
    }

    protected QueuedOutput() {
        this.results = new LinkedBlockingQueue<Result>();
        ExecutorService writeExecutor = Executors.newSingleThreadExecutor();
        writeExecutor.submit(new ResultsWriteRunnable());
    }

    @Override
    public final void write(Result result) {
        try {
            LOGGER.debug("Putting result to the queue: {}", result);
            results.put(result);
        } catch (InterruptedException e) {
            LOGGER.warn("Interrupted while putting result to the queue");
        }
    }

    protected abstract void doWrite(Result result);
}
