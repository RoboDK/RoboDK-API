package com.robodk.api;

/**
 * How a curve or a set of points is projected onto a surface, used by
 * {@link RoboDK#addCurve(Mat, Item, boolean, ProjectionType)}, {@link RoboDK#addPoints(Mat, Item, boolean, ProjectionType)},
 * and {@link RoboDK#projectPoints(Mat, Item, ProjectionType)}.
 * <p>
 * The numeric values match the RoboDK API wire protocol and the reference RoboDK C# and Python
 * APIs, so they must not be changed.
 */
public enum ProjectionType {

    /** No projection: the points/curve are added as provided. */
    NONE(0),
    /** The projection is the closest point on the surface. */
    CLOSEST(1),
    /** The projection is done along the normal. */
    ALONG_NORMAL(2),
    /** Projection along the normal; the normal is recalculated from the surface. */
    ALONG_NORMAL_RECALC(3),
    /** Closest point on the surface; the normal is recalculated. */
    CLOSEST_RECALC(4),
    /** The normal is recalculated according to the closest projection; the points are unchanged. */
    RECALC(5);

    private final int value;

    ProjectionType(int value) {
        this.value = value;
    }

    /** Returns the integer value used by the RoboDK API wire protocol for this projection type. */
    public int getValue() {
        return value;
    }
}
