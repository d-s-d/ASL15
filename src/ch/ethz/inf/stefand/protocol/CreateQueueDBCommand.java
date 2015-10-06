package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/6/15.
 */
public class CreateQueueDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * from create_queue(?)";

    public String queueName;

    public CreateQueueDBCommand(String queueName) {
        this.queueName = queueName;
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
        stmt.setString(1, this.queueName);
    }

    @Override
    public Class responseType() {
        return Integer.class;
    }
}
