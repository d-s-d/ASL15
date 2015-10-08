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
            pooledConnection = requestContext.connectionPool.getConnection();
            Connection conn = pooledConnection.getConnection();
            PreparedStatement ps = conn.prepareStatement(getSQLStatement());
            prepareStatement(ps);
            ResultSet rs = null;
            while(rs == null) {
                try {
                    rs = ps.executeQuery();
                } catch (SQLException sqlE) {
                    if (!sqlE.getMessage().contains("could not serialize"))
                        throw sqlE;
                }
            }
            if(rs.next()) {
                return this.executeDBCommand(requestContext, rs);
            } else
                return new EmptyResultException("Command Name: " + this.getClass().getName());
        } catch(SQLException e) {
            // TODO: Log
            return e;
        } finally {
            if(pooledConnection != null) pooledConnection.close();
        }
    }
}
