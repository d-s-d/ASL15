package ch.ethz.inf.stefand;

import java.io.Closeable;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.EmptyStackException;
import java.util.Stack;

/**
 * Created by dsd on 10/4/15.
 */
public class ConnectionPool {
    public static class PooledConnection implements Closeable {
        protected ConnectionPool pool;
        protected Connection connection;
        protected boolean open = true;

        public PooledConnection(Connection connection, ConnectionPool pool) {
            this.pool = pool;
            this.connection = connection;
        }

        @Override
        public void close() throws IOException {
            this.pool.putBack(this);
        }

        public Connection getConnection() {
            if(!open) throw new ClosedConnectionException();
            return connection;
        }

        public void setConnection(Connection connection) {
            this.connection = connection;
        }

        public void reopen() {
            this.open = true;
        }
    }

    protected Stack<PooledConnection> connections;

    public ConnectionPool(String url, String username, String password, int size) throws SQLException {
        this.connections = new Stack<>();

        for(int i = 0; i < size; i++) {
            final Connection conn = DriverManager.getConnection(url, username, password);
            this.connections.push(new PooledConnection(conn, this));
        }
    }

    public void putBack(PooledConnection pooledConnection) {
        if(!connections.contains(pooledConnection))
            this.connections.push(pooledConnection);
        pooledConnection.open = false;
    }

    public PooledConnection getConnection() throws EmptyStackException {
        final PooledConnection pooledConnection = this.connections.pop();
        pooledConnection.reopen();
        return pooledConnection;
    }

    public void close() {
        for(PooledConnection conn: this.connections) {
            try {
                conn.getConnection().close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
