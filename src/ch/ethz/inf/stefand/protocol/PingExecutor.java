package ch.ethz.inf.stefand.protocol;

/**
 * Created by dsd on 10/2/15.
 */
public class PingExecutor implements CommandExecutor {
    @Override
    public Object execute(RequestContext requestContext) {
        final PingCommand pingCommand = (PingCommand) requestContext.getCommand();
        final PongResponse pongResponse = new PongResponse();
        pongResponse.payload = pingCommand.payload;
        return pongResponse;
    }

    public void registerExecutor(CommandDispatcher commandDispatcher) {
        commandDispatcher.registerExecutor(PingCommand.class, this);
    }

    /*
    Object response = CommandDispatcher.dispatchCommand(requestContext).execute(requestContext)
    writeObject(response)
    close
     */
}
