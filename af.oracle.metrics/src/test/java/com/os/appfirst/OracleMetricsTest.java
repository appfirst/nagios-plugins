package com.os.appfirst;

import static org.junit.Assert.*;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class OracleMetricsTest {

	private OracleMetrics metrics;

	@Before
	public void setUp() throws Exception {
		this.metrics = new OracleMetrics(null, null, null);
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testGetTag() {
		String sql = "SELECT COUNT(REGION_ID) FROM REGIONS";
		String tag = this.metrics.getTag(sql);
		
		assertEquals("tag", ":AF_SQL_Select:", tag);
		
		
		// select
		sql = " select LOCATION_ID, CITY, POSTAL_CODE, STATE_PROVINCE, STREET_ADDRESS, COUNTRY_ID FROM LOCATIONS WHERE (LOCATION_ID = :1 )";
		tag = this.metrics.getTag(sql);
		assertEquals("tag", ":AF_SQL_Select:", tag);
		
		
		// select
		sql = " select LOCATION_ID, CITY, POSTAL_CODE, STATE_PROVINCE, STREET_ADDRESS, COUNTRY_ID FROM LOCATIONS WHERE (LOCATION_ID = :1 ) update";
		tag = this.metrics.getTag(sql);
		assertEquals("tag", ":AF_SQL_Select:", tag);
		
		// --
		sql = " dsfnjwhfkjbdskvbskdbvkjejhqdjklnsv";
		tag = this.metrics.getTag(sql);
		assertEquals("tag", ":AF_SQL:", tag);
	}

}
