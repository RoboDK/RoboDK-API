package com.robodk.api;

/**
 * State of the RoboDK main window, as used by {@link RoboDK#setWindowState(WindowState)}.
 * <p>
 * Values verified against the Python reference API ({@code WINDOWSTATE_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public enum WindowState {
    HIDDEN(-1),
    SHOW(0),
    MINIMIZED(1),
    NORMAL(2),
    MAXIMIZED(3),
    FULLSCREEN(4),
    CINEMA(5),
    FULLSCREEN_CINEMA(6),
    VIDEO(7);

    private final int value;

    WindowState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
