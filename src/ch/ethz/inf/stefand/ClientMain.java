package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.clients.SimplePingClient;
import ch.ethz.inf.stefand.clients.SimpleRegisterClient;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by dsd on 9/26/15.
 */
public class ClientMain {
    public static String CLASS_NAME_PREFIX = "ch.ethz.inf.stefand.clients.";

    public static void main(String[] args) {
        System.out.println("asdf");
        if(args.length > 3) {
            try {
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
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            } catch (UnexpectedResponseTypeException e) {
                e.printStackTrace();
            } catch (RemoteException e) {
                e.getException().printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("You must provide at least: <hostname> <portnumber> <clientClass>");
        }
    }
}
