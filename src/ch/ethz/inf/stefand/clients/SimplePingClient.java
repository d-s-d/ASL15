package ch.ethz.inf.stefand.clients;

import java.io.Closeable;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import ch.ethz.inf.stefand.AbstractClient;
import ch.ethz.inf.stefand.protocol.PingCommand;
import ch.ethz.inf.stefand.protocol.PongResponse;

/**
 * Created by dsd on 9/30/15.
 */
public class SimplePingClient extends AbstractClient {
    protected int iterations = 1;

    @Override
    public void initialize(String name, String middlewareHostname, int middlewarePortNumber, String[] args) {
        super.initialize(name, middlewareHostname, middlewarePortNumber, args);
    }

    @Override
    public void start() {
        if(this.args.length > 0) {
            this.iterations = Integer.parseInt(this.args[0]);
        }
        try {
            for(int i = 0; i < iterations; i++ ) {
                final Object response = this.sendCommand(new PingCommand(String.format("%d", System.currentTimeMillis())));
                if (response instanceof Exception) {
                    // TODO: Log
                    System.out.println("Received exception from middleware.");
                    ((Exception) response).printStackTrace();
                } else if (response instanceof PongResponse) {
                    final PongResponse pongResponse = (PongResponse) response;
                    final long delta = System.currentTimeMillis() - Long.parseLong(pongResponse.payload);
                    System.out.println(String.format("Successful ping, round trip time: %d ms", delta));
                }
            }
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
