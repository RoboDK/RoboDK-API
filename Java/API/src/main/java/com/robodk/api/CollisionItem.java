package com.robodk.api;

/**
 * An item (optionally restricted to a specific robot link) currently in a collision state; see
 * {@link RoboDK#getCollisionItems()}.
 */
public final class CollisionItem {

    private final Item item;
    private final int robotLinkId;

    public CollisionItem(Item item, int robotLinkId) {
        this.item = item;
        this.robotLinkId = robotLinkId;
    }

    public Item getItem() {
        return item;
    }

    public int getRobotLinkId() {
        return robotLinkId;
    }
}
