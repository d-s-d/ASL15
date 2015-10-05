package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.clients.SimplePingClient;
import ch.ethz.inf.stefand.clients.SimpleRegisterClient;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by dsd on 9/26/15.
 */
public class ClientMain {
    public static String CLASS_NAME_PREFIX = "ch.ethz.inf.stefand.clients.";

    public static void main(String[] args) {
        System.out.println(SimplePingClient.class.getName());
        if(args.length > 2) {
            String clientClassName = args[2];
            try {
                AbstractClient clientInstance =
                        (AbstractClient) Class.forName(CLASS_NAME_PREFIX+clientClassName).newInstance();
                clientInstance.initialize("someName", args[0], Integer.parseInt(args[1]),
                        Arrays.copyOfRange(args, 3, args.length));
                clientInstance.start();
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("You must provide at least: <hostname> <portnumber> <clientClass>");
        }
    }
}
