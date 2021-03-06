package ch.ethz.inf.stefand.protocol;

import org.omg.CORBA.INTERNAL;

import java.io.Serializable;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/5/15.
 */
public class RemoveClientDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * from remove_client(?)";

    public int clientId;

    public RemoveClientDBCommand(int clientId) {
        this.clientId = clientId;
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
        stmt.setInt(1, this.clientId);
    }

    @Override
    public Class responseType() {
        return Integer.class;
    }
}
