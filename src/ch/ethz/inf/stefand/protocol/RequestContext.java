package ch.ethz.inf.stefand.protocol;

import ch.ethz.inf.stefand.ConnectionPool;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;

/**
 * Created by dsd on 10/2/15.
 */
public class RequestContext implements Runnable {
    protected Object command;
    protected Socket socket;
    protected ConnectionPool connectionPool;

    public RequestContext(Socket socket, ConnectionPool connectionPool) {
        this.socket = socket;
        this.connectionPool = connectionPool;
    }

    @Override
    public void run() {
        ObjectOutputStream objectOutputStream = null;
        ObjectInputStream objectInputStream = null;
        try {
            objectOutputStream = new ObjectOutputStream(this.socket.getOutputStream());
            try {
                objectInputStream = new ObjectInputStream(this.socket.getInputStream());

                Object response = ((Command) objectInputStream.readObject()).execute(this);

                objectOutputStream.writeObject(response);
                objectOutputStream.flush();
            } catch (RuntimeException rt) {
                objectOutputStream.writeObject(rt);
            } catch (EmptyResultException e) {
                objectOutputStream.writeObject(e);
            } catch (ClassNotFoundException e) {
                objectOutputStream.writeObject(e);
                e.printStackTrace();
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                objectInputStream.close();
            }
            // TODO: log
            this.socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        } catch(ClassCastException e) {
            e.printStackTrace();
        } finally {
            if (objectOutputStream != null) {
                try {
                    objectOutputStream.close();
                } catch (IOException e) {
                    // log
                    e.printStackTrace();
                }
            }
            try {
                this.socket.close();
            } catch (IOException e) {
                // log
                e.printStackTrace();
            }
        }
    }

    public Object getCommand() {
        return command;
    }

    public void setCommand(Object command) {
        this.command = command;
    }

    public Socket getSocket() {
        return socket;
    }

    public void setSocket(Socket socket) {
        this.socket = socket;
    }

}
