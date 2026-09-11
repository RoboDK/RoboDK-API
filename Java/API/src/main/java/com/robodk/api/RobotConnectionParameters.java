package com.robodk.api;

/**
 * Connection parameters for a robot driver, as returned by {@link Item#connectionParams()} and
 * accepted by {@link Item#setConnectionParams}.
 */
public final class RobotConnectionParameters {

    private final String robotIp;
    private final int port;
    private final String remotePath;
    private final String ftpUser;
    private final String ftpPass;

    public RobotConnectionParameters(String robotIp, int port, String remotePath, String ftpUser, String ftpPass) {
        this.robotIp = robotIp;
        this.port = port;
        this.remotePath = remotePath;
        this.ftpUser = ftpUser;
        this.ftpPass = ftpPass;
    }

    public String getRobotIp() {
        return robotIp;
    }

    public int getPort() {
        return port;
    }

    public String getRemotePath() {
        return remotePath;
    }

    public String getFtpUser() {
        return ftpUser;
    }

    public String getFtpPass() {
        return ftpPass;
    }
}
