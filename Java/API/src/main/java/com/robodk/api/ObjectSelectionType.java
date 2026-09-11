package com.robodk.api;

/**
 * Object-selection feature types, used by {@link RoboDK#getPoints(ObjectSelectionType)} and
 * reported by {@link GetPointsResult}.
 * <p>
 * Values verified against the Python reference API ({@code FEATURE_*} constants in
 * {@code robolink.py}), since the C# {@code Model} enum definitions were not available.
 */
public enum ObjectSelectionType {
    NONE(0),
    SURFACE(1),
    CURVE(2),
    POINT(3),
    OBJECT_MESH(7),
    SURFACE_PREVIEW(8),
    MESH(9),
    HOVER_OBJECT_MESH(10),
    HOVER_OBJECT(11);

    private final int value;

    ObjectSelectionType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static ObjectSelectionType fromValue(int value) {
        for (ObjectSelectionType type : values()) {
            if (type.value == value) {
                return type;
            }
        }
        return NONE;
    }
}
