package com.robodk.api;

/**
 * Run mode (behavior) of a RoboDK station: simulate movements, validate them quickly, generate a
 * robot program (offline programming), or run on the physical robot (online programming). See
 * {@link RoboDK#setRunMode(RunMode)} and {@link RoboDK#getRunMode()}.
 * <p>
 * The numeric values match the RoboDK API wire protocol and the reference RoboDK C# and Python
 * APIs, so they must not be changed.
 */
public enum RunMode {

    /** Simulates the robot movements (default). */
    SIMULATE(1),
    /** Performs a quick check to validate the robot movements. */
    QUICK_VALIDATE(2),
    /** Generates the robot program (offline programming). */
    MAKE_ROBOT_PROGRAM(3),
    /** Generates the robot program and uploads it to the robot controller. */
    MAKE_ROBOT_PROGRAM_AND_UPLOAD(4),
    /** Generates the robot program and starts it on the robot controller. */
    MAKE_ROBOT_PROGRAM_AND_START(5),
    /** Moves the physical robot from the PC (online programming). */
    RUN_ROBOT(6);

    private final int value;

    RunMode(int value) {
        this.value = value;
    }

    /** Returns the integer value used by the RoboDK API wire protocol for this run mode. */
    public int getValue() {
        return value;
    }

    /**
     * Resolves a {@link RunMode} from its RoboDK API wire protocol integer value.
     *
     * @param value the wire protocol value, as returned by RoboDK
     * @return the matching run mode, or {@link #SIMULATE} if the value is unknown
     */
    public static RunMode fromValue(int value) {
        for (RunMode runMode : values()) {
            if (runMode.value == value) {
                return runMode;
            }
        }
        return SIMULATE;
    }
}
