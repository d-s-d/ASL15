package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.AbstractRegisteredClient;
import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;

import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;


/**
 * Created by dsd on 10/20/15.
 *
 * arguments: <queueName> <duration> [subclass arguments]
 */
public abstract class SingleQueueClient extends AbstractRegisteredClient {
    protected String queueName;
    protected int queueId;
    protected long duration;
    protected long stopTime;
    protected MessageDigest md;
    public static final long DEFAULT_DURATION = 10000; // ten seconds
    public static final String DEFAULT_QUEUE_NAME = "queue";
    public static final String STOP_STRING = "STOP";

    @Override
    public void initialize(String name, String middlewareHostname, int middlewarePortNumber, String[] args) throws
            ClassNotFoundException, UnexpectedResponseTypeException, RemoteException, IOException {
        super.initialize(name, middlewareHostname, middlewarePortNumber, args);
        // get queue name
        try {
            queueName = this.args[0];
            if(queueName.length() < 1)
                queueName = DEFAULT_QUEUE_NAME;
        } catch(IndexOutOfBoundsException e) {
            queueName = DEFAULT_QUEUE_NAME;
            logger.warn("Falling back to default queue name.");
        }

        // get duration
        try {
            duration = Long.parseLong(this.args[1]) * 1000;
        } catch (NumberFormatException|IndexOutOfBoundsException e) {
            duration = DEFAULT_DURATION;
            logger.warn("Falling back to default duration.");
        }

        stopTime = System.currentTimeMillis() + duration;
        queueId = createQueue(queueName);

        try {
            md = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
        md.update(queueName.getBytes("UTF-8"));
    }
}
