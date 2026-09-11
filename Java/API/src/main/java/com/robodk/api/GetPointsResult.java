package com.robodk.api;

/**
 * Result of {@link RoboDK#getPoints(ObjectSelectionType)}.
 */
public final class GetPointsResult {

    private final Item item;
    private final ObjectSelectionType featureType;
    private final int featureId;
    private final String name;
    private final Mat points;

    public GetPointsResult(Item item, ObjectSelectionType featureType, int featureId, String name, Mat points) {
        this.item = item;
        this.featureType = featureType;
        this.featureId = featureId;
        this.name = name;
        this.points = points;
    }

    /** The item under the mouse cursor (or matching the requested feature). */
    public Item getItem() {
        return item;
    }

    /** The type of feature actually returned. */
    public ObjectSelectionType getFeatureType() {
        return featureType;
    }

    /** Id of the feature (surface, curve, or point) within the item. */
    public int getFeatureId() {
        return featureId;
    }

    /** Name of the feature, if any. */
    public String getName() {
        return name;
    }

    /**
     * The mesh points, only populated when the requested {@link ObjectSelectionType} was
     * {@link ObjectSelectionType#HOVER_OBJECT_MESH}; {@code null} otherwise.
     */
    public Mat getPoints() {
        return points;
    }
}
