package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.protocol.Command;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;

/**
 * Created by dsd on 9/30/15.
 */
public abstract class AbstractClient {
    protected static final Logger logger = LogManager.getLogger(AbstractClient.class);

    protected String name;
    protected String middlewareHostname;
    protected int middlewarePortNumber;
    protected String[] args;

    public void initialize(String name, String middlewareHostname, int middlewarePortNumber, String[] args) throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        this.name = name;
        this.middlewareHostname = middlewareHostname;
        this.middlewarePortNumber = middlewarePortNumber;
        this.args = args;
        logger.trace(System.currentTimeMillis());
    }

    public abstract void start()
            throws ClassNotFoundException, UnexpectedResponseTypeException, IOException;

    protected Object sendCommand(Command command)
            throws IOException, ClassNotFoundException, UnexpectedResponseTypeException, RemoteException {
        Socket socket = null;
        ObjectInputStream responseStream = null;
        ObjectOutputStream commandStream = null;
        Object response = null;
        long startTime;
        // open connection
        try {
            socket = new Socket(this.middlewareHostname, this.middlewarePortNumber);
            commandStream = new ObjectOutputStream(socket.getOutputStream());
            // TODO: Start
            startTime = System.currentTimeMillis();
            commandStream.writeObject(command);
            commandStream.flush();
            responseStream = new ObjectInputStream(socket.getInputStream());
            response = responseStream.readObject();
            // close resources
        } finally {
            if(commandStream != null) commandStream.close();
            if(responseStream != null) responseStream.close();
            if(socket != null) socket.close();
        }
        if(response instanceof Exception) {
            throw new RemoteException((Exception) response);
        }
        if(!command.responseType().isAssignableFrom(response.getClass())) {
            throw new UnexpectedResponseTypeException(command, response);
        }
        final long deltaTime = System.currentTimeMillis() - startTime;
        final Class cls = command.getClass();
        if( Config.LOGGED_COMMANDS.contains(cls) ) {
            logger.trace(cls.getSimpleName() + ": " + Long.toString(deltaTime));
        }
        return response;
    }

    // Reference: http://stackoverflow.com/questions/9655181/
    final protected static char[] hexArray = "0123456789ABCDEF".toCharArray();
    public static String bytesToHex(byte[] bytes) {
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
        }
        return new String(hexChars);
    }
}
