package com.os.appfirst;

public class Metric {
	public String name = null;
	public long val = 0;
	public String unit = null;
	
	public Metric(String name, long val, String unit){
		this.name = name;
		this.val = val;
		this.unit = unit;
	}
}
