package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.protocol.*;

import java.io.IOException;

/**
 * Created by dsd on 10/6/15.
 */
public abstract class AbstractRegisteredClient extends AbstractClient {
    protected int clientId;

    @Override
    public void initialize(String name, String middlewareHostname, int middlewarePortNumber, String[] args)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        super.initialize(name, middlewareHostname, middlewarePortNumber, args);
        this.clientId = (Integer) this.sendCommand(new RegisterClientDBCommand(this.name));
        // TODO: Log
    }

    public void shutdown()
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        this.sendCommand(new RemoveClientDBCommand(this.clientId));
    }

    /**
     * Convenience method to send messages.
     * @param q queueId
     * @param s senderId
     * @param r receiverId (0 means public)
     * @param t text
     * @return message id
     * @throws ClassNotFoundException
     * @throws UnexpectedResponseTypeException
     * @throws RemoteException
     * @throws IOException
     */
    public int sendMessage(int q, int s, int r, String t)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Integer) this.sendCommand(new SendMessageDBCommand(q,s,r,t));
    }

    public int createQueue(String queueName)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Integer) this.sendCommand(new CreateQueueDBCommand(queueName));
    }

    public int getQueue(String queueName)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Integer) this.sendCommand(new GetQueueDBCommand(queueName));
    }

    public int removeQueue(int queueId)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Integer) this.sendCommand(new RemoveQueueDBCommand(queueId));
    }

    public Message popQueue(int receiverId, int queueId, int senderId)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Message) this.sendCommand(new PopDBCommand(queueId, receiverId, senderId));
    }

    public Message peekQueue(int receiverId, int queueId, int senderId)
            throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        return (Message) this.sendCommand(new PeekDBCommand(queueId, receiverId, senderId));
    }
}
