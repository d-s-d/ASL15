package ch.ethz.inf.stefand.protocol;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/5/15.
 */
public class PeekDBCommand extends DBCommand {
    protected int queueId;

    @Override
    protected Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException {
        return null;
    }

    @Override
    protected String getSQLStatement() {
        return null;
    }

    @Override
    protected void prepareStatement(PreparedStatement stmt) throws SQLException {

    }

    @Override
    public Class responseType() {
        return null;
    }
}
