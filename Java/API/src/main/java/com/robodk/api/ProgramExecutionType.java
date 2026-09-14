package com.robodk.api;

/**
 * Whether a program runs in the simulator only, or on the physical robot, used by
 * {@link Item#setRunType(ProgramExecutionType)}/{@link Item#getRunType()}.
 * <p>
 * Values verified against the Python reference API ({@code PROGRAM_RUN_ON_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public enum ProgramExecutionType {
    RUN_ON_SIMULATOR(1),
    RUN_ON_ROBOT(2);

    private final int value;

    ProgramExecutionType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static ProgramExecutionType fromValue(int value) {
        for (ProgramExecutionType type : values()) {
            if (type.value == value) {
                return type;
            }
        }
        return RUN_ON_SIMULATOR;
    }
}
