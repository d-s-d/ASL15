package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/6/15.
 */
public class RemoveQueueDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * from remove_queue(?)";
    protected int queueId;

    public RemoveQueueDBCommand(int queueId) {
        this.queueId = queueId;
    }

    @Override
    protected Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException {
        return rs.getInt(1);
    }

    @Override
    protected String getSQLStatement() {
        return SQL;
    }

    @Override
    protected void prepareStatement(PreparedStatement stmt) throws SQLException {
        stmt.setInt(1, this.queueId);
    }

    @Override
    public Class responseType() {
        return Integer.class;
    }
}
