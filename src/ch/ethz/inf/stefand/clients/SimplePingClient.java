package ch.ethz.inf.stefand.clients;

import java.io.Closeable;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import ch.ethz.inf.stefand.AbstractClient;
import ch.ethz.inf.stefand.protocol.PingCommand;
import ch.ethz.inf.stefand.protocol.PongResponse;
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
        ObjectOutputStream protoOutStream = null;
        ObjectInputStream protoInStream = null;
        try {
            socket = new Socket(this.middlewareHostname, this.middlewarePortNumber);
            protoOutStream = new ObjectOutputStream(socket.getOutputStream());
            PingCommand pingCommand = new PingCommand();
            pingCommand.payload = String.format("%d", System.currentTimeMillis());
            protoOutStream.writeObject(pingCommand);
            protoOutStream.flush();
            // socket.getOutputStream().flush();
            try {
                protoInStream = new ObjectInputStream(socket.getInputStream());
                final Object respObject = protoInStream.readObject();
                if(respObject instanceof RuntimeException) {
                    ((RuntimeException) respObject).printStackTrace();
                } else {
                    final PongResponse pongResponse = (PongResponse) respObject;
                    final long delta = System.currentTimeMillis() - Long.parseLong(pongResponse.payload);
                    System.out.println(String.format("Successful ping, round trip time: %d ms", delta));
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
