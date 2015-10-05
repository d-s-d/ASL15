package ch.ethz.inf.stefand.protocol;

import java.sql.Connection;

/**
 * Created by dsd on 10/5/15.
 */
public class DummyDBCommand extends DBCommand {
    @Override
    protected Object executeDBCommand(RequestContext requestContext, Connection conn) {
        return null;
    }
}
