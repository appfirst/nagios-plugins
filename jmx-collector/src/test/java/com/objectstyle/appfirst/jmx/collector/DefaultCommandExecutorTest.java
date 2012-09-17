package com.objectstyle.appfirst.jmx.collector;

import static com.google.common.collect.Collections2.transform;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
//import static org.junit.Assert.fail;

import java.util.HashSet;
import java.util.Set;

import org.junit.Test;

import com.google.common.base.Function;
import com.google.common.primitives.Primitives;

public class DefaultCommandExecutorTest {

//	@Test
//	public final void testDefaultCommandExecutor() {
//		fail("Not yet implemented"); // TODO
//	}
//
//	@Test
//	public final void testExecute() {
//		fail("Not yet implemented"); // TODO
//	}

	@Test
	public final void isPrimitiveOrWrapperType() {
        String type = "java.lang.Integer";
        Set<Class<?>> allTypes = new HashSet<Class<?>>();
        Function<Class<?>, String> classToString = new Function<Class<?>, String>() {
            @Override
            public String apply(Class<?> input) {
                return input.getName();
            }
        };

        // only Primitive Types:
        allTypes.addAll(Primitives.allPrimitiveTypes());
        assertFalse(transform(allTypes, classToString).contains(type));
        System.out.println(allTypes);

        // with Wrapper Types:
        allTypes.addAll(Primitives.allWrapperTypes());
        assertTrue(transform(allTypes, classToString).contains(type));
        System.out.println(allTypes);
    }
}
