package ch.ethz.inf.stefand;

import java.io.Closeable;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.concurrent.Callable;

import ch.ethz.inf.stefand.protocol.*;

/**
 * Created by dsd on 9/30/15.
 */
public class ClientDispatcher {
    protected int portNumber;
    protected CommandDispatcher commandDispatcher;

    public ClientDispatcher(int portNumber) {
        this.portNumber = portNumber;
        this.commandDispatcher = new CommandDispatcher();
    }

    public void run() {
        try {
            ServerSocket serverSocket = new ServerSocket(this.portNumber);
            Socket client = serverSocket.accept();
            RequestContext reqContext = new RequestContext(client, this.commandDispatcher);
            reqContext.run();
        } catch(IOException e) {
            e.printStackTrace();
        }
    }
}
