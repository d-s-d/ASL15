package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.AbstractRegisteredClient;
import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;

import java.io.IOException;

/**
 * Created by dsd on 10/6/15.
 */
public class OneQueueProducerClient extends AbstractRegisteredClient {
    public static int DEFAULT_MESSAGE_COUNT = 10;

    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        // get queue name
        String queuName = this.args[0];
        int msgCount, queueId;

        if(queuName.length() < 1)
            queuName = "queue";

        try {
            msgCount = Integer.parseInt(this.args[1]);
        } catch( NumberFormatException e) {
            msgCount = DEFAULT_MESSAGE_COUNT;
        }

        queueId = createQueue(queuName);

        for(int i = 0; i < msgCount; i++) {
            long msgTag = System.currentTimeMillis();
            int msgId = sendMessage(queueId, this.clientId, 0, Long.toString(msgTag));
            System.out.printf("delivered message %d (id: %d)\n", msgTag, msgId);
        }

        //shutdown(); // shut down deletes all messages!
    }
}
