package ch.ethz.inf.stefand.protocol;

/**
 * Created by dsd on 10/4/15.
 */
public interface Command {
    Object execute(RequestContext requestContext) throws Exception;
    Class responseType();
}
