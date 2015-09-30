package ch.ethz.inf.stefand.clients;

import java.io.Closeable;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import ch.ethz.inf.stefand.AbstractClient;
import ch.ethz.inf.stefand.protocol.RequestHeader;
import ch.ethz.inf.stefand.protocol.ResponseHeader;

/**
 * Created by dsd on 9/30/15.
 */
public class SimplePingClient extends AbstractClient {
    @Override
    public void initialize(String name, String middlewareHostname, int middlewarePortNumber) {
        super.initialize(name, middlewareHostname, middlewarePortNumber);
    }

    @Override
    public void start() {
        Socket socket = null;
        RequestHeader reqHeader = null;
        ObjectOutputStream protoOutStream = null;
        ObjectInputStream protoInStream = null;
        try {
            socket = new Socket(this.middlewareHostname, this.middlewarePortNumber);
            reqHeader = new RequestHeader(RequestHeader.REQUEST_TYPE_PING);
            protoOutStream = new ObjectOutputStream(socket.getOutputStream());
            protoOutStream.writeObject(reqHeader);
            protoOutStream.writeObject(String.format("%d", System.currentTimeMillis()));
            protoOutStream.flush();
            // socket.getOutputStream().flush();
            try {
                protoInStream = new ObjectInputStream(socket.getInputStream());
                final ResponseHeader respHeader = (ResponseHeader) protoInStream.readObject();
                if( respHeader.errorState == ResponseHeader.ERROR_STATE_SUCCESS ) {
                    final String ts = (String) protoInStream.readObject();
                    final long delta = System.currentTimeMillis() - Long.parseLong(ts);
                    System.out.println(String.format("Successful ping, round trip time: %d ms", delta));
                } else {
                    System.out.println("Received general error. :-(");
                }
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            Closeable[] closeables = new Closeable[] {socket, protoOutStream, protoInStream};
            for(Closeable closeable: closeables) {
                if(closeable != null) {
                    try {
                        closeable.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }
}
