package com.robodk.api;

/**
 * A pair of items (optionally restricted to a specific robot link on each) considered together
 * for collision checking; see {@link RoboDK#setCollisionActivePair}, {@link RoboDK#getCollisionPairs()},
 * {@link RoboDK#collisionActivePairList()}.
 */
public final class CollisionPair {

    private final Item item1;
    private final int robotLinkId1;
    private final Item item2;
    private final int robotLinkId2;

    public CollisionPair(Item item1, int robotLinkId1, Item item2, int robotLinkId2) {
        this.item1 = item1;
        this.robotLinkId1 = robotLinkId1;
        this.item2 = item2;
        this.robotLinkId2 = robotLinkId2;
    }

    public CollisionPair(Item item1, Item item2) {
        this(item1, 0, item2, 0);
    }

    public Item getItem1() {
        return item1;
    }

    public int getRobotLinkId1() {
        return robotLinkId1;
    }

    public Item getItem2() {
        return item2;
    }

    public int getRobotLinkId2() {
        return robotLinkId2;
    }
}
