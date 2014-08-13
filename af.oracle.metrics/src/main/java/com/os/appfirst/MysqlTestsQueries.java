package com.os.appfirst;


import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.concurrent.atomic.AtomicLong;

 
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.sql.DataSource;

import org.apache.log4j.Logger;


public class MysqlTestsQueries {
	
	static final Logger logger = Logger.getLogger(MysqlTestsQueries.class);	
	private final AtomicLong counter = new AtomicLong();

	public MysqlTestsQueries() {
		// TODO Auto-generated constructor stub
	}
	
	public void doTest() {
		
		Context ctx = null;
        Connection con = null;
        Statement stmt = null;
        ResultSet rs = null;
        try{
            ctx = new InitialContext();
            DataSource ds = (DataSource) ctx.lookup("java:/comp/env/jdbc/MyLocalDB");
             
            con = ds.getConnection();
            stmt = con.createStatement();
            if (stmt != null){
                rs = stmt.executeQuery("SELECT * FROM users;");
            } else {
            	logger.fatal("createStatement error");
            }
             

            
//            while(rs.next()){
//
//            	logger.debug(rs.getInt("id"));
//            	logger.debug(rs.getString("name"));
//            	logger.debug("---");
//            }

             
        }catch(NamingException e){
            e.printStackTrace();
        } catch (SQLException e) {
            e.printStackTrace();
        }finally{
            try {
                rs.close();
                stmt.close();
                con.close();
                ctx.close();
            } catch (SQLException e) {
                System.out.println("Exception in closing DB resources");
            } catch (NamingException e) {
                System.out.println("Exception in closing Context");
            }
             
        }
	}
	
	
	public void doTest1() {
        String dbURL = "jdbc:mysql://localhost:3306/af_tests";
        String username ="root";
        String password = "7012296";
       
        Connection dbCon = null;
        Statement stmt = null;
        ResultSet rs;
        long i = this.counter.incrementAndGet();
        //String query ="INSERT INTO `users` (`name`) VALUES ('name-" + i + "');";
        String query ="SELECT * FROM users;";
       
        try {
        	Class.forName("com.mysql.jdbc.Driver");
        
            //getting database connection to MySQL server
            dbCon = DriverManager.getConnection(dbURL, username, password);
           
            //getting PreparedStatment to execute query
            stmt = dbCon.prepareStatement(query);
           
            //Resultset returned by query
//            rs = stmt.executeUpdate(query);
            rs = stmt.executeQuery(query);
            
            dbCon.close();
           
        } catch (SQLException ex) {
        	logger.debug(ex);
        } catch (ClassNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally{
			if (dbCon != null){
				try {
					dbCon.close();
				} catch (SQLException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
           //close connection ,stmt and resultset here
        }
       
    }  

}

