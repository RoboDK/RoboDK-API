package com.robodk.api;

/**
 * Constants for {@link Item#setVisible(boolean, int)}'s {@code visibleReference} parameter,
 * controlling the visibility of an item's reference frame indicator (or, for robots, its links -
 * see the {@code VISIBLE_ROBOT_*} constants documented in the Python reference API for the
 * per-link bitmask, not reproduced here since this library only exposes the simple on/off/default
 * cases used by {@code setVisible}).
 * <p>
 * Values verified against the Python reference API ({@code VISIBLE_REFERENCE_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public final class VisibleRefType {

    /** Use the default behavior: same as {@link #ON} if the item itself is made visible, {@link #OFF} otherwise. */
    public static final int DEFAULT = -1;
    public static final int OFF = 0;
    public static final int ON = 1;

    private VisibleRefType() {
    }
}
