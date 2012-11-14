package com.objectstyle.appfirst.jmx.collector.utils;

import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecuteResultHandler;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.ExecuteException;
import org.apache.log4j.Logger;
import sun.tools.jconsole.LocalVirtualMachine;

import java.io.IOException;
import java.util.Map;

public class JVMAttach {

	private final static Logger LOGGER = Logger.getLogger(JVMAttach.class);
	private static final String CMD_LINE = "sudo";
	private LocalVirtualMachine lvm;

	public static void main(String[] args) throws IOException {

		LOGGER.debug(String.format("try to attach vm with vmid = %s", args[0]));
		Map<Integer, LocalVirtualMachine> vms = LocalVirtualMachine.getAllVirtualMachines();
		LocalVirtualMachine lvm = vms.get(Integer.valueOf(args[0]));
		if (lvm != null)
		{
			LOGGER.debug(String.format("lvm.id = %d; lvm.displayName = %s, lvm.manageable = %b,lvm.attachable = %b",
					lvm.vmid(), lvm.displayName(), lvm.isManageable(), lvm.isAttachable()));
			lvm.startManagementAgent();
		}

	}

	public void attach()
	{
		String jvmExec = String.format("%s/../bin/java", System.getProperty("java.home"));
		String classPath = System.getProperty("java.class.path");

		UserGroupGetter getter = new UserGroupGetter();
		getter.setPid(lvm.vmid());
		getter.get();
		String group = getter.getGroup();
		String user = getter.getUser();
		LOGGER.debug(String.format("jvm %d started with user %s and group %s",lvm.vmid(), user,group));
		CommandLine commandLine = new CommandLine(String.format(CMD_LINE));
		commandLine.addArguments(new String[]{"-u", user,
				"-g", group,
				jvmExec, "-cp", classPath,
				JVMAttach.class.getSimpleName(),
				String.valueOf(lvm.vmid())});

		LOGGER.debug(String.format("try to attach with command \"%s\"",commandLine.toString()));
		DefaultExecutor executor = new DefaultExecutor();
		DefaultExecuteResultHandler resultHandler = new DefaultExecuteResultHandler();
		try {
			executor.execute(commandLine,resultHandler);
			resultHandler.waitFor();
			ExecuteException exception = resultHandler.getException();
			if (exception != null)
				LOGGER.error(exception);
		} catch (Throwable e) {
			LOGGER.error(e);
		}
	}

	public LocalVirtualMachine getLvm() {
		return lvm;
	}

	public void setLvm(LocalVirtualMachine lvm) {
		this.lvm = lvm;
	}
}
