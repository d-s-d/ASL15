package ch.ethz.inf.stefand;

import java.io.Serializable;

/**
 * Created by dsd on 9/26/15.
 *
 * The network protocol is as follows:
 *
 * All communication between a client and a middleware node are essentially streams of objects. The corresponding
 * classes are contained in Protocol.
 *
 * The client establishes a connection with the middleware and sends a request. Each request begins with a
 * RequestHeader, specifying the type of request (i.e. the operation to be executed by the middleware node).
 *
 * Depending on the request type, the RequestHeader is followed by an object which is specific to the request.
 *
 * The middleware waits for the request header to be received and the corresponding payload (if any), processes the
 * request, sends a corresponding response and closes the connection. Similar to the request, a repsonse consists of at
 * least the ResponseHeader, indicating the error state. The ResponseHeader is followed by a payload specific to the
 * request sent by the client (i.e. the dequeued message when issues a pop-request).
 *
 */
public class Protocol {
    public static int RESPONSE_TYPE_PONG = 0;

    public static int ERROR_STATE_SUCCESS = 0;




}
