package com.robodk.api;

import com.robodk.api.exception.RdkException;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents an item in the RoboDK station tree: a robot, a reference frame, a tool, an
 * object, a target, a program, ... An item can also be seen as a node in the tree, with
 * exactly one parent and zero or more children.
 * <p>
 * Items are never created directly; they are obtained from a {@link RoboDK} link, for example
 * through {@link RoboDK#getItemByName(String, ItemType)} or {@link RoboDK#getItemList()}.
 */
public class Item {

    private final RoboDK link;
    private final ItemType itemType;
    private long itemId;
    private String cachedName;

    /**
     * Package-private constructor: items are created by {@link RoboDK} while decoding API
     * responses, never directly by API consumers.
     */
    Item(RoboDK link, long itemId, ItemType itemType) {
        this.link = link;
        this.itemId = itemId;
        this.itemType = itemType;
    }

    /** The RoboDK link this item was retrieved from. */
    public RoboDK getLink() {
        return link;
    }

    /** The internal RoboDK item identifier. Mostly useful for equality checks and debugging. */
    long getItemId() {
        return itemId;
    }

    /** The type of this item, as reported by RoboDK when the item was retrieved. */
    public ItemType getItemType() {
        return itemType;
    }

    /**
     * Returns {@code true} if this item still refers to a valid RoboDK item (that is, it has
     * not been deleted locally). This is a lightweight, local-only check; it does not query
     * RoboDK to verify the item still exists in the station.
     */
    public boolean isValid() {
        return itemId != 0;
    }

    @Override
    public String toString() {
        if (isValid()) {
            return String.format("Item(name=%s, id=%d, type=%s)", cachedName, itemId, itemType);
        }
        return "Item(INVALID)";
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (!(other instanceof Item)) {
            return false;
        }
        return itemId == ((Item) other).itemId;
    }

    @Override
    public int hashCode() {
        return Long.hashCode(itemId);
    }

    // ------------------------------------------------------------------------------------
    // API calls
    // ------------------------------------------------------------------------------------

    /**
     * Removes this item and its children from the RoboDK station. After calling this method
     * the item becomes invalid (see {@link #isValid()}).
     */
    public void delete() {
        if (!isValid()) {
            throw new RdkException("Item does not exist");
        }
        link.checkConnection();
        link.sendLine("Remove");
        link.sendItem(this);
        link.checkStatus();
        itemId = 0;
    }

    /**
     * Returns the name of this item, as displayed in the RoboDK station tree.
     */
    public String getName() {
        link.checkConnection();
        link.sendLine("G_Name");
        link.sendItem(this);
        cachedName = link.recvLine();
        link.checkStatus();
        return cachedName;
    }

    /**
     * Renames this item in the RoboDK station tree.
     */
    public void setName(String name) {
        link.checkConnection();
        link.sendLine("S_Name");
        link.sendItem(this);
        link.sendLine(name);
        link.checkStatus();
        cachedName = name;
    }

    /**
     * Returns the local pose of this item (relative to its parent), as a 4x4 homogeneous
     * transformation matrix.
     */
    public Mat getPose() {
        link.checkConnection();
        link.sendLine("G_Hlocal");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /**
     * Sets the local pose of this item (relative to its parent).
     */
    public void setPose(Mat pose) {
        link.checkConnection();
        link.sendLine("S_Hlocal");
        link.sendItem(this);
        link.sendPose(pose);
        link.checkStatus();
    }

    /**
     * For a robot item, returns the current joint values (in degrees for rotary axes, mm for
     * linear axes).
     */
    public double[] getJoints() {
        link.checkConnection();
        link.sendLine("G_Thetas");
        link.sendItem(this);
        double[] joints = link.recvArray();
        link.checkStatus();
        return joints;
    }

    /**
     * For a robot item, moves the robot immediately to the given joint values (no motion
     * planning, no collision checking: this only affects the simulation).
     */
    public void setJoints(double[] joints) {
        link.checkConnection();
        link.sendLine("S_Thetas");
        link.sendArray(joints);
        link.sendItem(this);
        link.checkStatus();
    }

    /**
     * Returns {@code true} if this item is currently visible in the 3D station view.
     */
    public boolean isVisible() {
        link.checkConnection();
        link.sendLine("G_Visible");
        link.sendItem(this);
        int visible = link.recvInt();
        link.checkStatus();
        return visible != 0;
    }

    /**
     * Shows or hides this item in the 3D station view.
     */
    public void setVisible(boolean visible) {
        link.checkConnection();
        link.sendLine("S_Visible");
        link.sendItem(this);
        link.sendInt(visible ? 1 : 0);
        link.sendInt(visible ? 1 : 0);
        link.checkStatus();
    }

    /**
     * Returns the parent of this item in the station tree, or an invalid item if this item has
     * no parent (for example, a station item).
     */
    public Item getParent() {
        link.checkConnection();
        link.sendLine("G_Parent");
        link.sendItem(this);
        Item parent = link.recvItem();
        link.checkStatus();
        return parent;
    }

    /**
     * Returns the direct children of this item in the station tree.
     */
    public List<Item> getChildren() {
        link.checkConnection();
        link.sendLine("G_Childs");
        link.sendItem(this);
        int childCount = link.recvInt();
        List<Item> children = new ArrayList<>(childCount);
        for (int i = 0; i < childCount; i++) {
            children.add(link.recvItem());
        }
        link.checkStatus();
        return children;
    }
}
