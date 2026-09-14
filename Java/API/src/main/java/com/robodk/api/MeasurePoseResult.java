package com.robodk.api;

/**
 * Result of {@link RoboDK#measurePose(int, int, double[])}.
 */
public final class MeasurePoseResult {

    private final Mat pose;
    private final double averageError;
    private final double maxError;

    public MeasurePoseResult(Mat pose, double averageError, double maxError) {
        this.pose = pose;
        this.averageError = averageError;
        this.maxError = maxError;
    }

    /** Measured pose. */
    public Mat getPose() {
        return pose;
    }

    /** Average error of the measurement, in mm. */
    public double getAverageError() {
        return averageError;
    }

    /** Maximum error of the measurement, in mm. */
    public double getMaxError() {
        return maxError;
    }
}
