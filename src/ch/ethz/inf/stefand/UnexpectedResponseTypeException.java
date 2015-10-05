package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.protocol.Command;

/**
 * Created by dsd on 10/5/15.
 */
public class UnexpectedResponseTypeException extends Exception {
    protected Command command;
    protected Object response;

    public UnexpectedResponseTypeException(Command command, Object response) {
        super("Got type " + (response != null ? response.getClass().getName() : "<null>") +
                " as response from command" + (command != null ? command.getClass().getName() : "<null>") +
                " (expected " + (command != null && command.responseType() != null ?
                command.responseType().getClass().getName() : "<null>") + ")");
        this.command = command;
        this.response = response;
    }
}
