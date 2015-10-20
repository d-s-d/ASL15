package ch.ethz.inf.stefand;

import ch.ethz.inf.stefand.protocol.PingCommand;
import ch.ethz.inf.stefand.protocol.PopDBCommand;
import ch.ethz.inf.stefand.protocol.SendMessageDBCommand;

import java.util.HashSet;
import java.util.Set;

/**
 * Created by dsd on 9/26/15.
 */
public final class Config {
    public static final String DBNAME = "asl15";
    public static final String DBURL = "jdbc:postgresql://localhost/" + DBNAME;
    public static final String DBUSERNAME = "asl15_mw";
    public static final String DBPASSWORD = "asl15_mw";
    public static final int DEFAULT_POOL_SIZE = 5;

    public static final Set<Class> LOGGED_COMMANDS = new HashSet<Class>();

    static {
        LOGGED_COMMANDS.add(PopDBCommand.class);
        LOGGED_COMMANDS.add(SendMessageDBCommand.class);
        LOGGED_COMMANDS.add(PingCommand.class);
    }
}
