package ch.ethz.inf.stefand;

import java.io.Closeable;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import ch.ethz.inf.stefand.protocol.*;

/**
 * Created by dsd on 9/30/15.
 */
public class ClientDispatcher {
    protected int portNumber;

    public ClientDispatcher(int portNumber) {
        this.portNumber = portNumber;
    }

    public void run() {
        ServerSocket serverSocket = null;
        Socket client = null;
        ObjectInputStream protoInStream = null;
        ObjectOutputStream protoOutStream = null;
        try {
            serverSocket = new ServerSocket(this.portNumber);
            client = serverSocket.accept();
            protoInStream = new ObjectInputStream(client.getInputStream());
            try {
                RequestHeader reqHeader = (RequestHeader) protoInStream.readObject();
                if(reqHeader.requestType == RequestHeader.REQUEST_TYPE_PING) {
                    protoOutStream = new ObjectOutputStream(client.getOutputStream());
                    ResponseHeader responseHeader = new ResponseHeader(ResponseHeader.ERROR_STATE_SUCCESS);
                    protoOutStream.writeObject(responseHeader);
                    protoOutStream.writeObject(protoInStream.readObject());
                    protoOutStream.flush();
                }
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            Closeable[] closeables = new Closeable[] {serverSocket, client, protoInStream, protoOutStream};
            for( Closeable closeable: closeables ) {
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
