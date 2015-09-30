package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.clients.SimplePingClient;

import java.util.HashMap;
import java.util.Map;

/**
 * Created by dsd on 9/26/15.
 */
public class ClientMain {
    public static String CLASS_NAME_PREFIX = "ch.ethz.inf.stefand.clients.";
    public static Map<String, Class> CLIENT_CLASSES = new HashMap<>();

    static {
        CLIENT_CLASSES.put(SimplePingClient.class.getName(), SimplePingClient.class);
    }

    public static void main(String[] args) {
        System.out.println(SimplePingClient.class.getName());
        if(args.length > 2) {
            String clientClassName = args[2];
            Class clientClass = CLIENT_CLASSES.get(CLASS_NAME_PREFIX+clientClassName);
            try {
                AbstractClient clientInstance = (AbstractClient) clientClass.newInstance();
                clientInstance.initialize("someName", args[0], Integer.parseInt(args[1]));
                clientInstance.start();
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("You must provide at least: <hostname> <portnumber> <clientClass>");
        }
    }
}
