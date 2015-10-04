package ch.ethz.inf.stefand.protocol;

/**
 * Created by dsd on 10/2/15.
 */
public interface CommandExecutor {
    Object execute(RequestContext requestContext);
}
