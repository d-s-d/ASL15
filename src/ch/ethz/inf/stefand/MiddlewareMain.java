package ch.ethz.inf.stefand;

import java.net.URI;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.util.concurrent.Executors;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.LoggerContext;

public class MiddlewareMain {
    private static final Logger logger;

    static {
        try {
            URI uri = ClientMain.class.getClassLoader().getResource("log4j2-mw.xml").toURI();
            LoggerContext context = (LoggerContext) LogManager.getContext(false);
            context.setConfigLocation(uri);
            //context.reconfigure();
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }

        logger = LogManager.getLogger(MiddlewareMain.class);
    }

    public static void main(String[] args) {
        if(args.length > 0) {
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
                logger.error(e);
            }
        } else {
            System.err.println("required arguments: <name> <dbhost> <dbname> <dbuser> <dbpass> <listenPort> [<poolSize>]");
        }
    }
}
