package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/6/15.
 */
public class SendMessageDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * from send_message(?,?,?,?)";

    protected int queueId;
    protected int senderId;
    protected int receiverId;
    protected String text;

    public SendMessageDBCommand(int queueId, int senderId, int receiverId, String text) {
        this.queueId = queueId;
        this.senderId = senderId;
        this.receiverId = receiverId;
        this.text = text;
    }

    @Override
    protected Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException {
        // return the global message identifier
        return rs.getInt(1);
    }

    @Override
    protected String getSQLStatement() {
        return SQL;
    }

    @Override
    protected void prepareStatement(PreparedStatement stmt) throws SQLException {
        stmt.setInt(1, queueId);
        stmt.setInt(2, senderId);
        stmt.setInt(3, receiverId);
        stmt.setString(4, text);
    }

    @Override
    public Class responseType() {
        return Integer.class;
    }
}
