package ch.ethz.inf.stefand;

import java.io.Closeable;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class MiddlewareMain {

    public static void main(String[] args) {
        if(args.length > 0) {
            int portNumber = Integer.parseInt(args[0]);
            ClientDispatcher clientDispatcher = new ClientDispatcher(portNumber);
            clientDispatcher.run();
        } else {
            System.out.println("you must provide at least the portnumber.");
        }
        System.out.println("This is the middleware.");
        /*
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            conn = DriverManager.getConnection(Config.DBURL, Config.DBUSERNAME, Config.DBPASSWORD);
            stmt = conn.createStatement();
            rs = stmt.executeQuery("SELECT * FROM messages");
            while( rs.next() ) {
                System.out.println(rs.getString(5));
            }
        } catch (SQLException e) {
            System.out.println("Caught SQLException: " + e.getMessage());
        } finally {
            try {
                if (conn != null) {
                    conn.close();
                }
                if ( stmt != null ) {
                    stmt.close();
                }
                if( rs != null ) {
                    rs.close();
                }
            } catch (SQLException e) {
                System.out.println("Caught exception while closing resources: " + e.getMessage());
            }
        }*/
    }
}
