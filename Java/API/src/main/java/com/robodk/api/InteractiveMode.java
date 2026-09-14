package com.robodk.api;

/**
 * 3D-mouse interaction mode, used by {@link RoboDK#setInteractiveMode}.
 * <p>
 * Values verified against the Python reference API ({@code SELECT_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public enum InteractiveMode {
    RESET(-1),
    NONE(0),
    RECTANGLE(1),
    ROTATE(2),
    ZOOM(3),
    PAN(4),
    MOVE(5),
    MOVE_SHIFT(6),
    MOVE_CLEAR(7);

    private final int value;

    InteractiveMode(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
