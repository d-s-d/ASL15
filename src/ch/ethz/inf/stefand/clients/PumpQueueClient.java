package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import ch.ethz.inf.stefand.protocol.EmptyResultException;
import ch.ethz.inf.stefand.protocol.Message;

import java.io.IOException;
import java.util.ArrayDeque;

/**
 * Created by dsd on 11/1/15.
 *
 * Additional arguments: <msgLength> <phaseLength>
 * phaseLength: number of messages pushed/popped in each phase
 */
public class PumpQueueClient extends SingleQueueClient {
    public static final int DEFAULT_MESSAGE_SIZE = 200;
    public static final int DEFAULT_PHASE_LENGTH = 64;
    public static final int MAX_CONSUMPTION_RETRIES = 16;

    private ArrayDeque<String> localQueue;
    private int phaseLength;
    private int msgSize;

    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, IOException {
        long msgCount = 0;
        // get message size
        try {
            msgSize = Integer.parseInt(this.args[2]);
        } catch (NumberFormatException|IndexOutOfBoundsException e) {
            msgSize = DEFAULT_MESSAGE_SIZE;
            logger.warn("Falling back to default message size.");
        }

        try {
            phaseLength = Integer.parseInt(this.args[2]);
        } catch (NumberFormatException|IndexOutOfBoundsException e) {
            phaseLength = DEFAULT_PHASE_LENGTH;
            logger.warn("Falling back to default phase length ({}).", DEFAULT_PHASE_LENGTH);
        }

        localQueue = new ArrayDeque<>(phaseLength);
        // loop until time limit is reached
        while(System.currentTimeMillis() < this.stopTime) {
            // produce messages
            for(long phaseCount = 0; phaseCount < phaseLength; phaseCount++) {
                try {
                    sendMessage(this.queueId, this.clientId, 0, this.enqueueMessage(msgCount));
                    msgCount++;
                } catch (RemoteException e) {
                    popTail();
                    logger.error(e);
                } catch (IOException ioE) {
                    popTail();
                    logger.error(ioE);
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                        logger.error(e);
                    }
                }
            } // production loop

            int consumptionRetries = 0;

            // consume messages
            while(true) {
                try {
                    final Message msg = popQueue(this.clientId, this.queueId, 0);
                    final String localMsg = dequeueMessage();
                    if(!msg.text.equals(localMsg)) {
                        if(localMsg != null) {
                            logger.error("Queues out of sync. Received message: {} Local message: {}",
                                    msg.text.substring(Math.max(msg.text.length() - 16, 0)),
                                    localMsg.substring(Math.max(localMsg.length() - 16, 0)));
                        } else {
                            logger.error("Queues out of sync. Received message: {} Local queue empty.",
                                    msg.text.substring(Math.max(msg.text.length() - 16, 0)));
                        }
                    }
                } catch (RemoteException e) {
                    Exception rException = e.getException();
                    if(e.getException() instanceof EmptyResultException) {
                        break;
                    } else {
                        logger.error(rException);
                        if(consumptionRetries >= MAX_CONSUMPTION_RETRIES)
                            break;
                        consumptionRetries++;
                    }
                }
            } // consumption loop
        } // while before stopTime

        try {
            shutdown();
        } catch (RemoteException e) {
            logger.error(e.getException());
        }
    }

    private String enqueueMessage(long counter) {
        final String fmtString = String.format("%%0%dx", msgSize);
        final String msgString = String.format(fmtString, counter);

        localQueue.add(msgString);
        return msgString;
    }

    private String dequeueMessage() {
        return localQueue.pollFirst();
    }

    private void popTail() {
        localQueue.pollLast();
    }
}
