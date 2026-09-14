package com.robodk.api;

/**
 * Bitmask/option constants for {@link Item#showSequence(java.util.List, java.util.List, int, int)},
 * controlling how a simulated path/sequence is displayed. Combine with bitwise OR.
 * <p>
 * Values verified against the Python reference API ({@code SEQUENCE_DISPLAY_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public final class SequenceDisplayFlags {

    public static final int DEFAULT = -1;
    public static final int TOOL_POSES = 0;
    public static final int ROBOT_POSES = 256;
    public static final int ROBOT_JOINTS = 2048;
    public static final int COLOR_SELECTED = 1;
    public static final int COLOR_TRANSPARENT = 2;
    public static final int COLOR_GOOD = 3;
    public static final int COLOR_BAD = 4;
    public static final int OPTION_RESET = 1024;

    private SequenceDisplayFlags() {
    }
}
