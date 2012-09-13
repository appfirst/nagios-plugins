package com.objectstyle.appfirst.jmx.collector.output.af;

import com.sun.jna.Library;
import com.sun.jna.Native;

public class AfCollector {

    private static String AFCollectorAPIName = "/afcollectorapi";
    private static String LibName = "rt";
    private static int O_WRONLY = 01;
    private static int APICollectorMaxMsgSize = 2048;

    public enum AFCollectorMsgSeverity {
        AFCSeverityInformation,
        AFCSeverityWarning,
        AFCSeverityCritical,
        AFCSeverityStatsd,
        AFCSeverityPolled;

        public static int toInt(AFCollectorMsgSeverity en) {
            switch (en) {
                case AFCSeverityInformation: {
                    return 0;
                }
                case AFCSeverityWarning: {
                    return 1;
                }
                case AFCSeverityCritical: {
                    return 2;
                }
                case AFCSeverityStatsd: {
                    return 3;
                }
                case AFCSeverityPolled: {
                    return 4;
                }
            }
            return -1;

        }
    }

    public enum AFCollectorReturnCode {
        AFCSuccess,
        AFCNoMemory,
        AFCBadParam,
        AFCOpenError,
        AFCPostError,
        AFCWouldBlock,
        AFCCloseError;

        public static AFCollectorReturnCode fromInt(int i) {
            switch (i) {
                case 0: {
                    return AFCSuccess;
                }
                case 1: {
                    return AFCNoMemory;
                }
                case 2: {
                    return AFCBadParam;
                }
                case 3: {
                    return AFCOpenError;
                }
                case 4: {
                    return AFCPostError;
                }
                case 5: {
                    return AFCWouldBlock;
                }
                case 6: {
                    return AFCCloseError;
                }
            }
            return AFCSuccess;
        }
    }

    public interface CLibrary extends Library {
        CLibrary INSTANCE = (CLibrary)
                Native.loadLibrary("c", CLibrary.class);

        int getpid();
    }

    public interface MQ extends Library {
        public int mq_open(String filename, int mode);

        public int mq_close(int mqd);

        public int mq_send(int mqd, String msg, int len, int prio);
    }


    public static AFCollectorReturnCode postAFCollectorMessage(AFCollectorMsgSeverity severity, String msg) {
        int len = msg.length();
        if (len > APICollectorMaxMsgSize) {
            return AFCollectorReturnCode.AFCBadParam;
        }

        int pid = CLibrary.INSTANCE.getpid();
        int prio = AFCollectorMsgSeverity.toInt(severity);
        int rv = 0;

        MQ mq = (MQ) Native.loadLibrary(LibName, MQ.class);

        int mqd = mq.mq_open(AFCollectorAPIName, O_WRONLY);

        String incident = pid + ":" + msg;
        len = incident.length();

        rv = mq.mq_send(mqd, incident, len, prio);

        mq.mq_close(mqd);

        return AFCollectorReturnCode.fromInt(rv);
    }
}

