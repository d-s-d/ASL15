package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;

/**
 * Created by dsd on 10/2/15.
 */
public class PingCommand implements Command, Serializable {
    public String payload;

    public PingCommand(String payload) {
        this.payload = payload;
    }

    @Override
    public Object execute(RequestContext requestContext) throws Exception {
        final PongResponse pongResponse = new PongResponse();
        pongResponse.payload = this.payload;
        return pongResponse;
    }
}
