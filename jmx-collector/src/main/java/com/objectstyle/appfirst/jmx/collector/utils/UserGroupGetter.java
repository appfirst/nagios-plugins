package com.objectstyle.appfirst.jmx.collector.utils;

import org.apache.commons.exec.*;
import org.apache.commons.lang3.StringUtils;


import javax.swing.*;
import java.io.*;
import java.util.List;

public class UserGroupGetter {

	private static final String CMD_LINE = "ps -p %d -o user,group";

	private int pid;

	private String user;
	private String group;


	public void get()
	{
		CommandLine cmdLine = CommandLine.parse(String.format(CMD_LINE,getPid()));
		ByteArrayOutputStream std = new ByteArrayOutputStream();
		ByteArrayOutputStream err = new ByteArrayOutputStream();
		PumpStreamHandler handler = new PumpStreamHandler(std, err);
		DefaultExecuteResultHandler resultHandler = new DefaultExecuteResultHandler();

		DefaultExecutor executor = new DefaultExecutor();
		executor.setStreamHandler(handler);
		try {
			executor.execute(cmdLine,resultHandler);

			resultHandler.waitFor();

			parse(std.toString());


		} catch (IOException e) {
			throw new IllegalArgumentException(e);
		} catch (InterruptedException e)
		{
			e.printStackTrace();
		}
	}

	private void parse(String output)
	{
		String[] strings = StringUtils.split(output);
		if (strings.length == 4)
		{
			user = strings[2];
			group = strings[3];
		}
	}




	public String getUser() {
		return user;
	}

	public String getGroup() {
		return group;
	}

	public int getPid() {
		return pid;
	}

	public void setPid(int pid) {
		this.pid = pid;
	}
}
