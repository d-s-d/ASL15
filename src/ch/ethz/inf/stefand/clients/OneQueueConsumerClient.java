package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.AbstractRegisteredClient;
import ch.ethz.inf.stefand.ConnectionPool;
import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import ch.ethz.inf.stefand.protocol.EmptyResultException;
import ch.ethz.inf.stefand.protocol.Message;
import ch.ethz.inf.stefand.protocol.RemoveClientDBCommand;

import java.io.IOException;

/**
 * Created by dsd on 10/6/15.
 */
public class OneQueueConsumerClient extends AbstractRegisteredClient {

    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        String queuName = this.args[0];
        int queueId;
        Message msg;

        if(queuName.length() < 1)
            queuName = "queue";

        queueId = getQueue(queuName);

        try {
            while(true) {
                msg = popQueue(this.clientId, queueId, 0);
                System.out.printf("Received message %s (id: %d).\n", msg.text, msg.messageId);
            }
        } catch(RemoteException e) {
            if(!(e.getException() instanceof EmptyResultException))
                e.getException().printStackTrace();
        }
    }
}
