package com.robodk.api;

/**
 * Connection status to a physical robot controller, returned by {@link Item#connectedState()}.
 * <p>
 * Values verified against the Python reference API ({@code ROBOTCOM_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public enum RobotConnectionType {
    PROBLEMS(-3),
    DISCONNECTED(-2),
    NOT_CONNECTED(-1),
    READY(0),
    WORKING(1),
    WAITING(2),
    UNKNOWN(-1000);

    private final int value;

    RobotConnectionType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static RobotConnectionType fromValue(int value) {
        for (RobotConnectionType type : values()) {
            if (type.value == value) {
                return type;
            }
        }
        return UNKNOWN;
    }
}
