package ch.ethz.inf.stefand.clients;


import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import ch.ethz.inf.stefand.protocol.EmptyResultException;
import ch.ethz.inf.stefand.protocol.Message;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;

/**
 * Created by dsd on 10/6/15.
 *
 * Arguments: <queueName> <duration>
 *
 */
public class OneQueueConsumerClient extends SingleQueueClient {
    Logger logger = LogManager.getLogger();

    long msgCount = 0;
    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, IOException {
        Message msg = new Message(0,0,0,0,"");
        while(System.currentTimeMillis() < stopTime) {
            try {
                msg = popQueue(clientId, queueId, 0);
                if(msg.text.startsWith(STOP_STRING))
                    break;
                md.update(msg.text.getBytes("UTF-8"));
                msgCount++;
            } catch(RemoteException e) {
                if(!(e.getException() instanceof EmptyResultException))
                    logger.error(e.getException());
                // in case of popping messages from a queue... an empty result exception is acceptable.
            }
        }

        if (msg.text.length() > STOP_STRING.length()) {
            final String hexDigest = msg.text.substring(STOP_STRING.length());
            if(hexDigest.equals(bytesToHex(md.digest()))) {
                logger.trace(String.format("Transmission succeeded: %d messages, client state: %s",
                        msgCount, hexDigest));
            } else {
                logger.warn(String.format("Message trace incomplete for client %s and queue %s. %d messages consumed."+
                        "producer client state %s, local state %s", name, queueName, msgCount,
                        hexDigest, bytesToHex(md.digest())));
            }
        }
    }
}
