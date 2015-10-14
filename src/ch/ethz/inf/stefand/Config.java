package ch.ethz.inf.stefand;

/**
 * Created by dsd on 9/26/15.
 */
public final class Config {
    public static final String DBNAME = "asl15";
    public static final String DBURL = "jdbc:postgresql://localhost/" + DBNAME;
    public static final String DBUSERNAME = "asl15_mw";
    public static final String DBPASSWORD = "asl15_mw";
    public static final int  DEFAULT_POOL_SIZE = 5;
}
