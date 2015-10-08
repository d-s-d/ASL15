package ch.ethz.inf.stefand;

import java.sql.SQLException;
import java.util.concurrent.Executors;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MiddlewareMain {
    private static final Logger logger = LogManager.getLogger(MiddlewareMain.class);

    public static void main(String[] args) {
        if(args.length > 0) {
            int portNumber = Integer.parseInt(args[0]);
            /*for(int i = 0; i < 1024; i++)
                logger.trace("Middleware started."); */
            ClientDispatcher clientDispatcher;
            int poolSize = 5;
            try {
                clientDispatcher = new ClientDispatcher(
                        portNumber, Executors.newFixedThreadPool(poolSize), new ConnectionPool(Config.DBURL,
                        Config.DBUSERNAME, Config.DBPASSWORD, poolSize));
                clientDispatcher.run();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("you must provide at least the portnumber.");
        }
        System.out.println("This is the middleware.");
    }
}
