package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;

/**
 * Created by dsd on 10/6/15.
 */
public class Message implements Serializable {
    public int messageId;
    public int queueId;
    public int senderId;
    public int receiverId;
    public String text;

    public Message(int messageId, int queueId, int senderId, int receiverId, String text) {
        this.messageId = messageId;
        this.queueId = queueId;
        this.senderId = senderId;
        this.receiverId = receiverId;
        this.text = text;
    }
}
