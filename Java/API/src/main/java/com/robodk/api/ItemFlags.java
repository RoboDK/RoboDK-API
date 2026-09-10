package com.robodk.api;

/**
 * Bitmask constants controlling how much access the user has to a specific item's features, used
 * by {@link Item#setFlags(int)}/{@link Item#getFlags()}. Combine with bitwise OR.
 * <p>
 * Values verified against the Python reference API ({@code FLAG_ITEM_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public final class ItemFlags {

    public static final int NONE = 0;
    public static final int SELECTABLE = 1;
    public static final int EDITABLE = 2;
    public static final int DRAGALLOWED = 4;
    public static final int DROPALLOWED = 8;
    public static final int ENABLED = 32;
    public static final int AUTOTRISTATE = 64;
    public static final int NOCHILDREN = 128;
    public static final int USERTRISTATE = 256;
    public static final int ALL = 64 + 32 + 8 + 4 + 2 + 1;

    private ItemFlags() {
    }
}
