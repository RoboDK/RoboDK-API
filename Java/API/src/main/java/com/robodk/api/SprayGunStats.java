package com.robodk.api;

/**
 * Result of {@link RoboDK#sprayGetStats(int)}.
 */
public final class SprayGunStats {

    private final String info;
    private final Mat data;

    public SprayGunStats(String info, Mat data) {
        this.info = info;
        this.data = data;
    }

    /** Human-readable statistics (tab-separated). */
    public String getInfo() {
        return info;
    }

    /** Raw statistics data. */
    public Mat getData() {
        return data;
    }
}
