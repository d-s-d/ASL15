package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.security.MessageDigest;

/**
 * Created by dsd on 10/6/15.
 *
 * arguments: <queueName> <duration> (in seconds!) <messageSize>
 *
 */
public class OneQueueProducerClient extends SingleQueueClient {

    Logger logger = LogManager.getLogger();
    public static final int DEFAULT_MESSAGE_SIZE = 200;

    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, IOException {
        MessageDigest md = null;
        int msgSize;
        long msgNo = 0;

        // get message size
        try {
            msgSize = Integer.parseInt(this.args[2]);
        } catch (NumberFormatException|IndexOutOfBoundsException e) {
            msgSize = DEFAULT_MESSAGE_SIZE;
            logger.error(e.getMessage());
            logger.warn("Falling back to default duration.");
        }

        // when sending messages, receiving any kind of remote exception is considered to be irrecoverable.
        try {
            final String fmtString = String.format("%%0%dx", msgSize);
            while(System.currentTimeMillis() < stopTime) {
                final String msgCountString = String.format(fmtString, msgNo);
                sendMessage(queueId, this.clientId, 0, msgCountString);
                md.update(msgCountString.getBytes("UTF-8"));
                msgNo++;
            }
        } catch (RemoteException e) {
            logger.error("Remote Exception: " + e.getException().getMessage());
        } finally {
            try {
                final String hexDigest = bytesToHex(md.digest());
                sendMessage(queueId, clientId, 0, STOP_STRING + hexDigest);
                logger.trace("sending succeeded, client state: " + hexDigest);
            } catch (RemoteException e) {
                logger.error("Remote Exception: " + e.getException().getMessage());
            }
        }
        //shutdown(); // shut down deletes all messages!
    }
}
