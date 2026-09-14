package com.robodk.api;

/**
 * Result of {@link RoboDK#getCursorXYZ(int, int)}.
 */
public final class CursorXyzResult {

    private final Item item;
    private final double[] xyz;

    public CursorXyzResult(Item item, double[] xyz) {
        this.item = item;
        this.xyz = xyz;
    }

    /** Item under the cursor, if any (an invalid item otherwise). */
    public Item getItem() {
        return item;
    }

    /** Station-relative XYZ coordinates (mm) of the point under the cursor. */
    public double[] getXyz() {
        return xyz;
    }
}
