package ch.ethz.inf.stefand.protocol;

import javax.naming.event.ObjectChangeListener;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by dsd on 10/2/15.
 */
public class CommandDispatcher {
    public static Map<String, CommandExecutor> COMMANDS = new HashMap<>();

    public CommandDispatcher() {
        new PingExecutor().registerExecutor(this);
    }

    public CommandExecutor dispatchCommand(RequestContext requestContext)
            throws IOException {
        final ObjectInputStream objectInputStream = new ObjectInputStream(
                requestContext.getSocket().getInputStream());
        try {
            final Object command = objectInputStream.readObject();
            requestContext.setCommand(command);
            final CommandExecutor cmdExecutor = COMMANDS.get(command.getClass().getName());
            if(cmdExecutor != null) {
                return cmdExecutor;
            }
            throw new RuntimeException(
                    String.format("No command executor for '%s.'", command.getClass().getName()));
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }
    }

    public void registerExecutor(Class clazz, CommandExecutor commandExecutor) {
        COMMANDS.put(clazz.getName(), commandExecutor);
    }
}
