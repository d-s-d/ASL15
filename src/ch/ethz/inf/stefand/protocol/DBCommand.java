package ch.ethz.inf.stefand.protocol;

import ch.ethz.inf.stefand.ConnectionPool;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Created by dsd on 10/5/15.
 */
public abstract class DBCommand implements Command {
    protected abstract Object executeDBCommand(RequestContext requestContext, ResultSet rs) throws SQLException;
    protected abstract String getSQLStatement();
    protected abstract void prepareStatement(PreparedStatement stmt) throws SQLException;

    public Object execute(RequestContext requestContext) throws Exception {
        ConnectionPool.PooledConnection pooledConnection = null;
        try {
            Connection conn = requestContext.connectionPool.getConnection().getConnection();
            PreparedStatement ps = conn.prepareStatement(getSQLStatement());
            prepareStatement(ps);
            ResultSet rs = ps.executeQuery();
            Object result = this.executeDBCommand(requestContext, rs);
            if(result == null)
                return new EmptyResultException();
            return result;
        } catch(SQLException e) {
            // TODO: Log
            return e;
        } finally {
            if(pooledConnection != null) pooledConnection.close();
        }
    }
}
