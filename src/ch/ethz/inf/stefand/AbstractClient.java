package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.protocol.Command;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;

/**
 * Created by dsd on 9/30/15.
 */
public abstract class AbstractClient {
    protected String name;
    protected String middlewareHostname;
    protected int middlewarePortNumber;
    protected String[] args;

    public void initialize(String name, String middlewareHostname, int middlewarePortNumber, String[] args) {
        this.name = name;
        this.middlewareHostname = middlewareHostname;
        this.middlewarePortNumber = middlewarePortNumber;
        this.args = args;
    }

    public abstract void start();

    protected Object sendCommand(Command command) throws IOException, ClassNotFoundException {
        Socket socket = null;
        ObjectInputStream responseStream = null;
        ObjectOutputStream commandStream = null;
        Object response = null;
        // open connection
        try {
            socket = new Socket(this.middlewareHostname, this.middlewarePortNumber);
            commandStream = new ObjectOutputStream(socket.getOutputStream());
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
        return response;
    }
}
