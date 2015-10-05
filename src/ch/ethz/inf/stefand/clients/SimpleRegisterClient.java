package ch.ethz.inf.stefand.clients;

import ch.ethz.inf.stefand.AbstractClient;
import ch.ethz.inf.stefand.RemoteException;
import ch.ethz.inf.stefand.UnexpectedResponseTypeException;
import ch.ethz.inf.stefand.protocol.RegisterClientDBCommand;
import ch.ethz.inf.stefand.protocol.RemoveClientDBCommand;

import java.io.IOException;

/**
 * Created by dsd on 10/5/15.
 */
public class SimpleRegisterClient extends AbstractClient {
    @Override
    public void start() {
        try {
            Integer response = (Integer) this.sendCommand(new RegisterClientDBCommand(this.name));
            System.out.println(String.format("Registered Client with id: %d.", ((Integer) response)));
            response = (Integer) this.sendCommand(new RemoveClientDBCommand(response));
            System.out.println(String.format("Removed Client with id: %d.", ((Integer) response)));
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (UnexpectedResponseTypeException e) {
            e.printStackTrace();
        } catch (RemoteException e) {
            e.getException().printStackTrace();
        }
    }
}
