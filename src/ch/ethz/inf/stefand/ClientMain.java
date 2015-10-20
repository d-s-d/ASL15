package ch.ethz.inf.stefand;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.LogManager;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Arrays;


/**
 * Created by dsd on 9/26/15.
 *
 * Arguments;
 * <client_type_name> <client_name> <middleware_hostname> <middleware_port> [client type specific arguments]
 *
 */
public class ClientMain {
    public static String CLASS_NAME_PREFIX = "ch.ethz.inf.stefand.clients.";

    protected static Logger logger;

    static {
        try {
            URI uri = ClientMain.class.getClassLoader().getResource("log4j2-client.xml").toURI();
            LoggerContext context = (LoggerContext) LogManager.getContext(false);
            context.setConfigLocation(uri);
            //context.reconfigure();
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }

        logger = LogManager.getLogger(ClientMain.class);
    }

    public static void main(String[] args) {
        if(args.length > 3) {
            try {
                logger.warn("some warning");
                System.out.printf("Starting client: %s, %s, %s, %s.\n", args[0], args[1], args[2], args[3]);
                String clienttype = args[0];
                String clientname = args[1];
                String mwhost = args[2];
                int msport = Integer.parseInt(args[3]);
                AbstractClient clientInstance =
                        (AbstractClient) Class.forName(CLASS_NAME_PREFIX+clienttype).newInstance();
                clientInstance.initialize(clientname, mwhost, msport,
                        Arrays.copyOfRange(args, 4, args.length));
                System.out.printf("Starting client: %s.\n", clienttype);
                clientInstance.start();
            } catch (InstantiationException|IllegalAccessException|ClassNotFoundException|
                    UnexpectedResponseTypeException|IOException e) {
                logger.error(e.getMessage());
            } catch (RemoteException e) {
                // this can only happen during the initialization of the client.
                // while the client is operating (after initialization), remote exceptions are expected to be dealt with
                // by the concrete client class.
                logger.error("Remote Exception: " + e.getMessage());
            }
        } else {
            System.out.println("You must provide at least: <hostname> <portnumber> <clientClass>");
        }
    }
}
