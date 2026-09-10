package com.robodk.api;

/**
 * Bitmask constants controlling which parts of the RoboDK UI are enabled, used by
 * {@link RoboDK#setWindowFlags(int)}. Combine with bitwise OR.
 * <p>
 * Values verified against the Python reference API ({@code FLAG_ROBODK_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public final class WindowFlags {

    public static final int NONE = 0x00;
    public static final int TREE_ACTIVE = 1;
    public static final int VIEW3D_ACTIVE = 2;
    public static final int LEFT_CLICK = 4;
    public static final int RIGHT_CLICK = 8;
    public static final int DOUBLE_CLICK = 16;
    public static final int MENU_ACTIVE = 32;
    public static final int MENUFILE_ACTIVE = 64;
    public static final int MENUEDIT_ACTIVE = 128;
    public static final int MENUPROGRAM_ACTIVE = 256;
    public static final int MENUTOOLS_ACTIVE = 512;
    public static final int MENUUTILITIES_ACTIVE = 1024;
    public static final int MENUCONNECT_ACTIVE = 2048;
    public static final int WINDOWKEYS_ACTIVE = 4096;
    public static final int TREE_VISIBLE = 8192;
    public static final int REFERENCES_VISIBLE = 16384;
    public static final int STATUSBAR_VISIBLE = 32768;
    public static final int ALL = 0xFFFF;
    public static final int MENU_ACTIVE_ALL = MENU_ACTIVE | MENUFILE_ACTIVE | MENUEDIT_ACTIVE
            | MENUPROGRAM_ACTIVE | MENUTOOLS_ACTIVE | MENUUTILITIES_ACTIVE | MENUCONNECT_ACTIVE;

    private WindowFlags() {
    }
}
