package ch.ethz.inf.stefand;

import java.io.Serializable;

/**
 * Created by dsd on 9/26/15.
 */
public class Network {
    public static int REQUEST_TYPE_PING = 0;

    public class Request implements Serializable{
        public int requestType;

        public Request(int type) {
            this.requestType = type;
        }
    }

    public class ResponseCode implements Serializable {
        public int responseCode;

        public ResponseCode(int code) {
            this.responseCode = code;
        }
    }
}
