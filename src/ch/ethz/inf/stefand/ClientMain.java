package ch.ethz.inf.stefand;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.LogManager;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Paths;
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


    public static void main(String[] args) {
        Logger logger = null;
            if(args.length > 3) {
                try {
                    System.out.printf("Starting client: %s.\n", Arrays.toString(args));
                    String clienttype = args[0];
                    String clientname = args[1];
                    String mwhost = args[2];

                    File f = new File("log4j2-"+clientname+".xml");
                    URI uri = f.toURI();
                    LoggerContext context = (LoggerContext) LogManager.getContext(false);
                    context.setConfigLocation(uri);
                    //context.reconfigure();
                    logger = LogManager.getLogger(ClientMain.class);
                    
                    int msport = Integer.parseInt(args[3]);
                    AbstractClient clientInstance =
                            (AbstractClient) Class.forName(CLASS_NAME_PREFIX+clienttype).newInstance();
                    clientInstance.initialize(clientname, mwhost, msport,
                            Arrays.copyOfRange(args, 4, args.length));
                    System.out.printf("Starting client: %s.\n", clienttype);
                    clientInstance.start();
                    System.out.println("Finished client: " + clientname);

                } catch (InstantiationException|IllegalAccessException|ClassNotFoundException|
                        UnexpectedResponseTypeException|IOException e) {
                    logger.error(e);
                } catch (RemoteException e) {
                    // this can only happen during the initialization of the client.
                    // while the client is operating (after initialization), remote exceptions are expected to be dealt with
                    // by the concrete client class.
                    logger.error("Remote Exception: ", e.getException());
                }
            } else {
                System.out.println("You must provide at least: <hostname> <portnumber> <clientClass>");
            }
    }
}
