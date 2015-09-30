package ch.ethz.inf.stefand;

/**
 * Created by dsd on 9/30/15.
 */
public abstract class AbstractClient {
    protected String name;
    protected String middlewareHostname;
    protected int middlewarePortNumber;

    public void initialize(String name, String middlewareHostname, int middlewarePortNumber) {
        this.name = name;
        this.middlewareHostname = middlewareHostname;
        this.middlewarePortNumber = middlewarePortNumber;
    }

    public abstract void start();
}
