package ch.ethz.inf.stefand.protocol;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;

/**
 * Created by dsd on 10/2/15.
 */
public class RequestContext implements Runnable {
    protected CommandExecutor commandExecutor;
    protected Object command;
    protected Socket socket;
    protected CommandDispatcher commandDispatcher;

    public RequestContext(Socket socket, CommandDispatcher commandDispatcher /* sql connection */) {
        this.socket = socket;
        this.commandDispatcher = commandDispatcher;
    }

    @Override
    public void run() {
        ObjectOutputStream objectOutputStream = null;
        try {
            objectOutputStream = new ObjectOutputStream(this.socket.getOutputStream());
            try {
                Object response = this.commandDispatcher.dispatchCommand(this).execute(this);
                objectOutputStream.writeObject(response);
                objectOutputStream.flush();
                objectOutputStream.close();
            } catch (RuntimeException rt) {
                objectOutputStream.writeObject(rt);
            }
            // TODO: log
            this.socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (objectOutputStream != null) {
                try {
                    objectOutputStream.close();
                } catch (IOException e) {
                    // log
                    e.printStackTrace();
                }
            }
            try {
                this.socket.close();
            } catch (IOException e) {
                // log
                e.printStackTrace();
            }
        }
    }

    public CommandExecutor getCommandExecutor() {
        return commandExecutor;
    }

    public Object getCommand() {
        return command;
    }

    public void setCommandExecutor(CommandExecutor commandExecutor) {
        this.commandExecutor = commandExecutor;
    }

    public void setCommand(Object command) {
        this.command = command;
    }

    public Socket getSocket() {
        return socket;
    }

    public void setSocket(Socket socket) {
        this.socket = socket;
    }

    public CommandDispatcher getCommandDispatcher() {
        return commandDispatcher;
    }

    public void setCommandDispatcher(CommandDispatcher commandDispatcher) {
        this.commandDispatcher = commandDispatcher;
    }
}
