package ch.ethz.inf.stefand.protocol;

import java.io.Serializable;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/5/15.
 */
public class RegisterClientDBCommand extends DBCommand implements Serializable {
    public static String SQL = "SELECT * from register_client(?)";

    public String clientName;

    public RegisterClientDBCommand(String clientName) {
        this.clientName = clientName;
    }

    @Override
    protected Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException {
        if(rs.next())
            return rs.getInt(1);
        return null;
    }

    @Override
    protected String getSQLStatement() {
        return SQL;
    }

    @Override
    protected void prepareStatement(PreparedStatement stmt) throws SQLException {
        stmt.setString(1, clientName);
    }
}
