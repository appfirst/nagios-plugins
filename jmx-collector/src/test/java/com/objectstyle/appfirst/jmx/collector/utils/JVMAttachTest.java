package com.objectstyle.appfirst.jmx.collector.utils;

import org.junit.Test;
import sun.tools.jconsole.LocalVirtualMachine;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;


public class JVMAttachTest {

	@Test
	public void test() throws Exception {
		JVMAttach jvmAttach = spy(new JVMAttach());
		UserGroupGetter getter = mock(UserGroupGetter.class);

		when(getter.getGroup()).thenReturn("group");
		when(getter.getUser()).thenReturn("user");


		LocalVirtualMachine lvm = mock(LocalVirtualMachine.class);
		when(lvm.isManageable()).thenReturn(true);
		when(lvm.connectorAddress()).thenReturn("address");

		jvmAttach.setLvm(lvm);

		when(jvmAttach.getUserGroupGetter()).thenReturn(getter);
		when(jvmAttach.getLocalVirtualMachine(0)).thenReturn(lvm);
		when(jvmAttach.execCommand(JVMAttach.CommandStrategy.Su)).thenReturn(0);
		when(jvmAttach.execCommand(JVMAttach.CommandStrategy.Sudo)).thenReturn(0);
		when(jvmAttach.execCommand(JVMAttach.CommandStrategy.SudoWithGroup)).thenReturn(0);


		jvmAttach.attach();
		String[] args = jvmAttach.getArgumentsBy(JVMAttach.CommandStrategy.Su);
		assertEquals(5, args.length);
		for (String arg : args) {
			assertNotNull(arg);
		}
		args = jvmAttach.getArgumentsBy(JVMAttach.CommandStrategy.Sudo);
		assertEquals(9, args.length);
		for (String arg : args) {
			assertNotNull(arg);
		}
		args = jvmAttach.getArgumentsBy(JVMAttach.CommandStrategy.SudoWithGroup);
		assertEquals(7, args.length);
		for (String arg : args) {
			assertNotNull(arg);
		}
	}
}
