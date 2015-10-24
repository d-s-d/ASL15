package ch.ethz.inf.stefand;

import java.io.Closeable;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;

import ch.ethz.inf.stefand.protocol.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Created by dsd on 9/30/15.
 */
public class ClientDispatcher {
    private static final Logger logger = LogManager.getLogger(ClientDispatcher.class);

    protected int portNumber;
    protected ExecutorService threadPool;
    protected ConnectionPool connectionPool;

    public ClientDispatcher(int portNumber, ExecutorService threadPool, ConnectionPool connectionPool) {
        this.portNumber = portNumber;
        this.threadPool = threadPool;
        this.connectionPool = connectionPool;
    }

    public void run() {
        ServerSocket serverSocket = null;
        try {
            serverSocket = new ServerSocket(this.portNumber);
            while(true) {
                try {
                    Socket client = serverSocket.accept();
                    RequestContext reqContext = new RequestContext(client, connectionPool);
                    threadPool.submit(reqContext);
                } catch (IOException e) {
                    logger.error(e);
                }
            }
        } catch (IOException e) {
            logger.error(e);
        }
    }
}
