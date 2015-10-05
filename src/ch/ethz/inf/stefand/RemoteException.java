package ch.ethz.inf.stefand;

/**
 * Created by dsd on 10/5/15.
 */
public class RemoteException extends Exception {
    protected Exception exception;

    public RemoteException(Exception exception) {
        this.exception = exception;
    }

    public Exception getException() {
        return exception;
    }
}
