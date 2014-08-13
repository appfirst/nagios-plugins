package com.os.appfirst;

import java.sql.DriverManager;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.apache.log4j.Logger;

public class OracleSqlQuerys {

	static final Logger logger = Logger.getLogger(App.class);
	private Connection connection = null;

	public Boolean connect(String oracleDbUrl, String user, String pass) {

		logger.debug("Oracle JDBC Connecting");

		try {

			Class.forName("oracle.jdbc.driver.OracleDriver");

		} catch (ClassNotFoundException e) {

			logger.fatal("Oracle JDBC Driver not found "  + e.getMessage());
			return false;

		}

		logger.debug("Oracle JDBC Driver Registered!");

		try {
			
			//"jdbc:oracle:thin:@192.168.1.66:1521:oracle"
			connection = DriverManager.getConnection(oracleDbUrl, user, pass);

		} catch (SQLException e) {

			logger.debug("Connection Failed! Check output console " + e.getMessage());
			return false;

		}

		if (connection != null) {
			logger.debug("connection established to Oracle DB");
		} else {
			logger.fatal("Failed to make connection!");
			return false;
		}
		
		return true;
	}

	public ResultSet makeQuery(String sql) {
		Statement stmt = null;
		try {
			if (this.connection != null) {
				stmt = this.connection.createStatement();

				if (stmt != null) {
					if (sql != null) {
						ResultSet rs = stmt.executeQuery(sql);
						return rs;
					} else {
						logger.fatal("sql query not set");
					}

				} else {
					logger.fatal("createStatement error");
				}
			}
		} catch (SQLException e) {
			try {
				stmt.close();
				this.connection.close();
				logger.fatal("SQL error: " + e.getMessage());
			} catch (SQLException err) {
				logger.fatal("Exception in closing DB resources " + err.getMessage());
			}
		}
		return null;

	}

}
