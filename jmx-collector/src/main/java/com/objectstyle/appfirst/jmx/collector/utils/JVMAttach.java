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

	private static final  Logger LOGGER = Logger.getLogger(JVMAttach.class);

	private String jvmExec = String.format("%s/../bin/java", System.getProperty("java.home"));
	private String classPath = System.getProperty("java.class.path");
	private String user;
	private String group;
	private LocalVirtualMachine lvm;


	public static void main(String[] args) throws IOException {

		//we cannot use log4j in this place because the main is started with not root permissions
		System.out.println(String.format("try to attach vm with vmid = %s", args[0]));
		Map<Integer, LocalVirtualMachine> vms = LocalVirtualMachine.getAllVirtualMachines();
		LocalVirtualMachine lvm = vms.get(Integer.valueOf(args[0]));
		if (lvm != null) {
			System.out.println(String.format("lvm.id = %d; lvm.displayName = %s, lvm.manageable = %b,lvm.attachable = %b",
					lvm.vmid(), lvm.displayName(), lvm.isManageable(), lvm.isAttachable()));
			lvm.startManagementAgent();
		}

	}

	UserGroupGetter getUserGroupGetter()
	{
		return new UserGroupGetter();
	}

	LocalVirtualMachine getLocalVirtualMachine(int vmid)
	{
		return LocalVirtualMachine.getLocalVirtualMachine(vmid);
	}


	public LocalVirtualMachine attach() {
		UserGroupGetter getter = getUserGroupGetter();
		getter.setPid(lvm.vmid());
		getter.get();
		group = getter.getGroup();
		user = getter.getUser();
		LOGGER.debug(String.format("jvm %d started with user %s and group %s", lvm.vmid(), user, group));

		for (CommandStrategy commandStrategy : CommandStrategy.values()) {

			execCommand(commandStrategy);
			lvm = getLocalVirtualMachine(lvm.vmid());
			if (lvm.isManageable() && lvm.connectorAddress() != null)
				return lvm;
		}
		LOGGER.error("All attach attempts are failed.");
		return null;
	}

	int execCommand(CommandStrategy commandStrategy) {
		 int result = -1;
		CommandLine commandLine = commandStrategy.getCommandLine(getArgumentsBy(commandStrategy));

		LOGGER.debug(String.format("try to attach with command \"%s\"", commandLine.toString()));
		DefaultExecutor executor = new DefaultExecutor();
		DefaultExecuteResultHandler resultHandler = new DefaultExecuteResultHandler();
		ByteArrayOutputStream std = new ByteArrayOutputStream();
		ByteArrayOutputStream err = new ByteArrayOutputStream();
		PumpStreamHandler handler = new PumpStreamHandler(std, err);
		executor.setStreamHandler(handler);
		try {
			executor.execute(commandLine, resultHandler);
			resultHandler.waitFor();
			ExecuteException exception = resultHandler.getException();
			if (exception != null)
				LOGGER.error(exception);
			else
				logging(std, err);
			result = resultHandler.getExitValue();
		} catch (Throwable e) {
			LOGGER.error(e);
		} finally {
			IOUtils.closeQuietly(std);
			IOUtils.closeQuietly(err);
		}
		return result;
	}


	private void logging(ByteArrayOutputStream std, ByteArrayOutputStream err) {
		String stdOut = std.toString();
		LOGGER.debug(stdOut);
		String errOut = err.toString();
		if (StringUtils.trimToNull(errOut) != null)
			LOGGER.warn(errOut);
	}

	public LocalVirtualMachine getLvm() {
		return lvm;
	}

	public void setLvm(LocalVirtualMachine lvm) {
		this.lvm = lvm;
	}

	public String[] getArgumentsBy(CommandStrategy commandStrategy) {
		switch (commandStrategy) {

			case Sudo:
				return new String[]{"-u", user,
						"-g", group,
						jvmExec, "-cp", classPath,
						JVMAttach.class.getName(),
						String.valueOf(lvm.vmid())};
			case SudoWithGroup:
				return new String[]{"-u", user,
						jvmExec, "-cp", classPath,
						JVMAttach.class.getName(),
						String.valueOf(lvm.vmid())};
			case Su:
				/**
				 * example:	su -s /bin/sh hbase -c "/usr/java/jdk1.6.0_25/jre/../bin/java -cp .:/usr/java/latest//lib/jconsole.jar:/usr/java/latest//lib/tools.jar:appfirst-jmx-0.4-jar-with-dependencies.jar:appfirst-jmx-0.4.jar com.objectstyle.appfirst.jmx.collector.utils.JVMAttach 5084"
				 */
				return new String[]{"-s", "/bin/sh",
						user, "-c",
						String.format("%s -cp %s %s %d", jvmExec, classPath, JVMAttach.class.getName(), lvm.vmid())};
			default:
				throw new IllegalArgumentException();
		}
	}

	 enum CommandStrategy {
		Sudo("sudo"),
		SudoWithGroup("sudo"),
		Su("su");

		private String command;

		private CommandStrategy(String command) {
			this.command = command;
		}

		public CommandLine getCommandLine(String[] arguments) {
			CommandLine commandLine = new CommandLine(this.getCommand());
			commandLine.addArguments(arguments);
			return commandLine;
		}

		 public String getCommand() {
			 return command;
		 }
	 }
}
