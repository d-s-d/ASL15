package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;

/**
 * Created by dsd on 10/2/15.
 */
public class ErrorResponse implements Serializable {
    public int error_code;
    public String error_msg;

}
