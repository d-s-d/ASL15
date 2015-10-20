package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.AbstractRegisteredClient;
import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import ch.ethz.inf.stefand.protocol.RegisterClientDBCommand;
import ch.ethz.inf.stefand.protocol.RemoveClientDBCommand;
import ch.ethz.inf.stefand.protocol.SendMessageDBCommand;

import java.io.IOException;

/**
 * Created by dsd on 10/5/15.
 */
public class SimpleRegisterClient extends AbstractRegisteredClient {
    @Override
    public void start() throws ClassNotFoundException, UnexpectedResponseTypeException, IOException {
        try {
            shutdown();
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }
}
