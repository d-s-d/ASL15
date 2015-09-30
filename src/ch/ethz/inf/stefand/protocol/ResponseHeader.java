package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;

/**
 * Created by dsd on 9/30/15.
 */
public class ResponseHeader implements Serializable {
    public static int ERROR_STATE_SUCCESS = 0;
    public static int ERROR_STATE_GENERAL_ERROR = 1;

    public int errorState;

    public ResponseHeader(int errorState) {
        this.errorState = errorState;
    }
}