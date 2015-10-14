package ch.ethz.inf.stefand;

import java.sql.SQLException;
import java.util.concurrent.Executors;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MiddlewareMain {
    private static final Logger logger = LogManager.getLogger(MiddlewareMain.class);

    public static void main(String[] args) {
        if(args.length > 0) {
            /*for(int i = 0; i < 1024; i++)
                logger.trace("Middleware started."); */
            String mwname = args[0];
            String dbhost = args[1];
            String dbname = args[2];
            String dbuser = args[3];
            String dbpass = args[4];
            System.out.println(dbpass);
            int portNumber = Integer.parseInt(args[5]);
            int poolSize = Config.DEFAULT_POOL_SIZE;
            if(args.length > 6) {
                poolSize = Integer.parseInt(args[6]);
            }
            String dburl = "jdbc:postgresql://" + dbhost + "/" + dbname;
            ClientDispatcher clientDispatcher;
            try {
                clientDispatcher = new ClientDispatcher(
                        portNumber, Executors.newFixedThreadPool(poolSize), new ConnectionPool(dburl,
                        dbuser, dbpass, poolSize));
                System.out.printf("Middleware started: %s.\n", mwname);
                clientDispatcher.run();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        } else {
            System.err.println("required arguments: <name> <dbhost> <dbname> <dbuser> <dbpass> <listenPort> [<poolSize>]");
        }
    }
}
