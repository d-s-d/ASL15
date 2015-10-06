package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/6/15.
 */
public class PopDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * FROM pop(?, ?, ?)";

    protected int queueId;
    protected int receiverId;
    protected int senderId;

    public PopDBCommand(int queueId, int receiverId, int senderId) {
        this.queueId = queueId;
        this.receiverId = receiverId;
        this.senderId = senderId;
    }

    @Override
    protected Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException {
        return new Message(rs.getInt(1), rs.getInt(2), rs.getInt(3), rs.getInt(4), rs.getString(5));
    }

    @Override
    protected String getSQLStatement() {
        return SQL;
    }

    @Override
    protected void prepareStatement(PreparedStatement stmt) throws SQLException {
        stmt.setInt(1, receiverId);
        stmt.setInt(2, queueId);
        stmt.setInt(3, senderId);
    }

    @Override
    public Class responseType() {
        return Message.class;
    }
}
