package com.objectstyle.appfirst.jmx.collector.result;

public class Primitives {

    public static boolean isPrimitiveOrWrapperType(Class<?> clazz){
        return isPrimitiveType(clazz) || isWrapperType(clazz);
    }

    public static boolean isWrapperType(Class<?> clazz) {
        return clazz.equals(Boolean.class) ||
               clazz.equals(Integer.class) ||
               clazz.equals(Character.class) ||
               clazz.equals(Byte.class) ||
               clazz.equals(Short.class) ||
               clazz.equals(Double.class) ||
               clazz.equals(Long.class) ||
               clazz.equals(Void.class) ||
               clazz.equals(String.class) ||
               clazz.equals(Float.class);
    }

    public static boolean isPrimitiveType(Class<?> clazz) {
        return clazz.equals(boolean.class) ||
               clazz.equals(int.class) ||
               clazz.equals(char.class) ||
               clazz.equals(byte.class) ||
               clazz.equals(short.class) ||
               clazz.equals(double.class) ||
               clazz.equals(long.class) ||
               clazz.equals(void.class) ||
               clazz.equals(float.class);
    }
}
