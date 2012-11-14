package com.objectstyle.appfirst.jmx.collector.utils;

import org.apache.commons.exec.*;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import sun.tools.jconsole.LocalVirtualMachine;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Map;

public class JVMAttach {

	private static final String CMD_LINE = "sudo";
	private LocalVirtualMachine lvm;
	private Logger LOGGER = Logger.getLogger(JVMAttach.class);

	public static void main(String[] args) throws IOException {

		//we cannot use log4j in this place because the main is started with not root permissions
		System.out.println(String.format("try to attach vm with vmid = %s", args[0]));
		Map<Integer, LocalVirtualMachine> vms = LocalVirtualMachine.getAllVirtualMachines();
		LocalVirtualMachine lvm = vms.get(Integer.valueOf(args[0]));
		if (lvm != null)
		{
			System.out.println(String.format("lvm.id = %d; lvm.displayName = %s, lvm.manageable = %b,lvm.attachable = %b",
					lvm.vmid(), lvm.displayName(), lvm.isManageable(), lvm.isAttachable()));
			lvm.startManagementAgent();
		}

	}

	public void attach()
	{
		Logger LOGGER = Logger.getLogger(JVMAttach.class);

		String jvmExec = String.format("%s/../bin/java", System.getProperty("java.home"));
		String classPath = System.getProperty("java.class.path");

		UserGroupGetter getter = new UserGroupGetter();
		getter.setPid(lvm.vmid());
		getter.get();
		String group = getter.getGroup();
		String user = getter.getUser();
		LOGGER.debug(String.format("jvm %d started with user %s and group %s", lvm.vmid(), user, group));
		CommandLine commandLine = new CommandLine(String.format(CMD_LINE));
		commandLine.addArguments(new String[]{"-u", user,
				"-g", group,
				jvmExec, "-cp", classPath,
				JVMAttach.class.getName(),
				String.valueOf(lvm.vmid())});

		LOGGER.debug(String.format("try to attach with command \"%s\"",commandLine.toString()));
		DefaultExecutor executor = new DefaultExecutor();
		DefaultExecuteResultHandler resultHandler = new DefaultExecuteResultHandler();
		ByteArrayOutputStream std = new ByteArrayOutputStream();
		ByteArrayOutputStream err = new ByteArrayOutputStream();
		PumpStreamHandler handler = new PumpStreamHandler(std, err);
		executor.setStreamHandler(handler);
		try {
			executor.execute(commandLine,resultHandler);
			resultHandler.waitFor();
			ExecuteException exception = resultHandler.getException();
			if (exception != null)
				LOGGER.error(exception);
			else
				logging(std, err);
		} catch (Throwable e) {
			LOGGER.error(e);
		}
		finally {
			IOUtils.closeQuietly(std);
			IOUtils.closeQuietly(err);
		}
	}

	private void logging(ByteArrayOutputStream std, ByteArrayOutputStream err) {
		String stdOut = std.toString();
		LOGGER.debug(stdOut);
		String errOut = err.toString();
		if (StringUtils.trimToNull(errOut) != null)
			LOGGER.error(errOut);
	}

	public LocalVirtualMachine getLvm() {
		return lvm;
	}

	public void setLvm(LocalVirtualMachine lvm) {
		this.lvm = lvm;
	}
}
