package ch.ethz.inf.stefand.protocol;

import ch.ethz.inf.stefand.ConnectionPool;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.Arrays;

/**
 * Created by dsd on 10/2/15.
 */
public class RequestContext implements Runnable {
    protected Object command;
    protected Socket socket;
    protected ConnectionPool connectionPool;
    private static final Logger logger = LogManager.getLogger(RequestContext.class);

    private static final int MAX_DELTAS = 4;
    private long lastSplit;
    private long[] deltaTimes = new long[MAX_DELTAS];
    private int currentDeltaTimeIdx = -1;

    public void pushDelta() {
        if(currentDeltaTimeIdx > -1 && currentDeltaTimeIdx < MAX_DELTAS) {
            deltaTimes[currentDeltaTimeIdx] = System.currentTimeMillis() - lastSplit;
        }
        lastSplit = System.currentTimeMillis();
        currentDeltaTimeIdx++;
    }

    public RequestContext(Socket socket, ConnectionPool connectionPool) {
        this.socket = socket;
        this.connectionPool = connectionPool;
    }

    @Override
    public void run() {
        pushDelta(); // SPLIT TIME: start
        ObjectOutputStream objectOutputStream = null;
        ObjectInputStream objectInputStream = null;
        try {
            objectOutputStream = new ObjectOutputStream(this.socket.getOutputStream());
            try {
                objectInputStream = new ObjectInputStream(this.socket.getInputStream());
                final Command cmd = (Command) objectInputStream.readObject();
                pushDelta(); // SPLIT TIME 0: after read
                Object response = cmd.execute(this);
                objectOutputStream.writeObject(response);
                objectOutputStream.flush();
                pushDelta(); // SPLIT TIME 3: After write back
                logger.trace(Arrays.toString(deltaTimes));
            } catch (RuntimeException|EmptyResultException|ClassNotFoundException rt) {
                objectOutputStream.writeObject(rt);
            }  catch (Exception e) {
                logger.error(e);
            } finally {
                objectInputStream.close();
            }
            // TODO: log
            this.socket.close();
        } catch (IOException|ClassCastException e) {
            logger.error(e);
        } finally {
            if (objectOutputStream != null) {
                try {
                    objectOutputStream.close();
                } catch (IOException e) {
                    logger.error(e);
                }
            }
            try {
                this.socket.close();
            } catch (IOException e) {
                logger.error(e);
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
