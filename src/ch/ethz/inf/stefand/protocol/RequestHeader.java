package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;

/**
 * Created by dsd on 9/30/15.
 */
public final class RequestHeader implements Serializable {
    public static int REQUEST_TYPE_PING = 0;

    public int requestType;

    public RequestHeader(int type) {
        this.requestType = type;
    }
}