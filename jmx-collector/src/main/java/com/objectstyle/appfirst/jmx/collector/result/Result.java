package com.objectstyle.appfirst.jmx.collector.result;

public class Result {
    private final String name;

    private final ResultStatus status;

    private final ResultData data;

    public Result(String name, ResultStatus status, ResultData data) {
        this.name = name;
        this.status = status;
        this.data = data;
    }

    public String getName() {
        return name;
    }

    public ResultStatus getStatus() {
        return status;
    }

    public ResultData getData() {
        return data;
    }

    @Override
    public String toString() {
        StringBuilder stringBuilder = new StringBuilder();
        stringBuilder.append(String.format("%s %s", name, status.getNagiosStringValue()));
        if (data instanceof ErrorResultData) {
            stringBuilder.append(": ").append(data.toString());
        } else if (!(data instanceof NoResultData)) {
            stringBuilder.append(" | ").append(data.toString());
        }
        return stringBuilder.toString();
    }
}
