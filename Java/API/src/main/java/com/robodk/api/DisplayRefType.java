package com.robodk.api;

/**
 * Bitmask constants selecting which reference frame axes/planes are shown for interactive
 * (3D mouse) manipulation, used by {@link RoboDK#setInteractiveMode}. Combine with bitwise OR.
 * <p>
 * Values verified against the Python reference API ({@code DISPLAY_REF_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public final class DisplayRefType {

    public static final int DEFAULT = -1;
    public static final int NONE = 0;
    public static final int TX = 0b001;
    public static final int TY = 0b010;
    public static final int TZ = 0b100;
    public static final int RX = 0b001000;
    public static final int RY = 0b010000;
    public static final int RZ = 0b100000;
    public static final int PXY = 0b001000000;
    public static final int PXZ = 0b010000000;
    public static final int PYZ = 0b100000000;

    private DisplayRefType() {
    }
}
