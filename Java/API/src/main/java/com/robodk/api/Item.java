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
     * Shows or hides this item in the 3D station view, and controls the visibility of its
     * reference frame indicator (see {@link VisibleRefType}).
     */
    public void setVisible(boolean visible, int visibleReference) {
        int reference = visibleReference;
        if (reference == VisibleRefType.DEFAULT) {
            reference = visible ? VisibleRefType.ON : VisibleRefType.OFF;
        }
        link.checkConnection();
        link.sendLine("S_Visible");
        link.sendItem(this);
        link.sendInt(visible ? 1 : 0);
        link.sendInt(reference);
        link.checkStatus();
    }

    /**
     * Shows or hides this item in the 3D station view.
     */
    public void setVisible(boolean visible) {
        setVisible(visible, VisibleRefType.DEFAULT);
    }

    /** Marks this item as being in collision (or not), highlighting it in the 3D view. */
    public void showAsCollided(boolean collided, int robotLinkId) {
        link.checkConnection();
        link.sendLine("ShowAsCollided");
        link.sendItem(this);
        link.sendInt(robotLinkId);
        link.sendInt(collided ? 1 : 0);
        link.checkStatus();
    }

    /** @see #showAsCollided(boolean, int) */
    public void showAsCollided(boolean collided) {
        showAsCollided(collided, 0);
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

    // ------------------------------------------------------------------------------------
    // Tree manipulation
    // ------------------------------------------------------------------------------------

    /** Attaches this item to a new parent, keeping its absolute position in the station. */
    public void setParent(Item parent) {
        link.checkConnection();
        link.sendLine("S_Parent");
        link.sendItem(this);
        link.sendItem(parent);
        link.checkStatus();
    }

    /** Attaches this item to a new parent, keeping its local pose (position relative to the new parent). */
    public void setParentStatic(Item parent) {
        link.checkConnection();
        link.sendLine("S_Parent_Static");
        link.sendItem(this);
        link.sendItem(parent);
        link.checkStatus();
    }

    /** Attaches this item to the closest object/frame/robot in the station and returns it. */
    public Item attachClosest() {
        link.checkConnection();
        link.sendLine("Attach_Closest");
        link.sendItem(this);
        Item attached = link.recvItem();
        link.checkStatus();
        return attached;
    }

    /** Detaches the closest child object attached to this item (or to {@code parent}, if given). */
    public Item detachClosest(Item parent) {
        link.checkConnection();
        link.sendLine("Detach_Closest");
        link.sendItem(this);
        link.sendItem(parent);
        Item detached = link.recvItem();
        link.checkStatus();
        return detached;
    }

    /** @see #detachClosest(Item) */
    public Item detachClosest() {
        return detachClosest(null);
    }

    /** Detaches every object attached to this item, re-attaching them to {@code parent} (or the station). */
    public void detachAll(Item parent) {
        link.checkConnection();
        link.sendLine("Detach_All");
        link.sendItem(this);
        link.sendItem(parent);
        link.checkStatus();
    }

    /** @see #detachAll(Item) */
    public void detachAll() {
        detachAll(null);
    }

    /** Marks this item (and, optionally, its children) to be inserted elsewhere with {@link RoboDK#paste(Item)}. */
    public void copy(boolean copyChildren) {
        link.copy(this, copyChildren);
    }

    /** @see #copy(boolean) */
    public void copy() {
        copy(true);
    }

    /** Inserts the item previously marked with {@link #copy()}, attached to this item. */
    public Item paste() {
        return link.paste(this);
    }

    /**
     * Returns {@code true} if this item's geometry lies inside {@code objectParent}'s geometry.
     */
    public boolean isInside(Item objectParent) {
        return link.isInside(this, objectParent);
    }

    /** Returns {@code true} if this item's geometry is currently in collision with {@code other}'s. */
    public boolean collision(Item other) {
        return link.collision(this, other);
    }

    // ------------------------------------------------------------------------------------
    // Item-level parameters and values
    // ------------------------------------------------------------------------------------

    /**
     * Sends a low-level, item-specific command to RoboDK and returns its response. Available
     * commands are listed under <b>Tools &gt; Run Script &gt; Show Commands</b> in the RoboDK GUI.
     */
    public String setParam(String param, String value) {
        link.checkConnection();
        link.sendLine("ICMD");
        link.sendItem(this);
        link.sendLine(param);
        link.sendLine(value);
        String response = link.recvLine();
        link.checkStatus();
        return response;
    }

    /** @see #setParam(String, String) */
    public String setParam(String param) {
        return setParam(param, "");
    }

    /** Attaches arbitrary binary data to this item, under a named slot. */
    public void setParam(String param, byte[] value) {
        link.checkConnection();
        link.sendLine("S_ItmDataParam");
        link.sendItem(this);
        link.sendLine(param);
        link.sendBytes(value);
        link.checkStatus();
    }

    /** Reads back binary data previously attached to this item with {@link #setParam(String, byte[])}. */
    public byte[] getParam(String param) {
        link.checkConnection();
        link.sendLine("G_ItmDataParam");
        link.sendItem(this);
        link.sendLine(param);
        byte[] data = link.recvBytes();
        link.checkStatus();
        return data;
    }

    /** Sets a named matrix-valued custom variable on this item (used by some post-processors/macros). */
    public Mat setValue(String variableName, Mat value) {
        link.checkConnection();
        link.sendLine("S_ValueMat");
        link.sendItem(this);
        link.sendLine(variableName);
        link.sendMatrix(value != null ? value : new Mat(0, 0));
        Mat result = link.recvMatrix();
        link.checkStatus();
        return result;
    }

    /** Sets a named string-valued custom variable on this item (used by some post-processors/macros). */
    public void setValue(String variableName, String value) {
        link.checkConnection();
        link.sendLine("S_Gen_Str");
        link.sendItem(this);
        link.sendLine(variableName);
        link.sendLine(value);
        link.checkStatus();
    }

    // ------------------------------------------------------------------------------------
    // Appearance
    // ------------------------------------------------------------------------------------

    /**
     * Recolors every shape of this item matching {@code fromColor} (within {@code tolerance}) to
     * {@code toColor}.
     *
     * @param toColor RGBA color in the 0-1 range (4 values) to apply
     * @param fromColor RGBA color to replace, or {@code null} to recolor every shape
     * @param tolerance color-matching tolerance (ignored when {@code fromColor} is {@code null})
     */
    public void recolor(double[] toColor, double[] fromColor, double tolerance) {
        link.checkConnection();
        double[] from = fromColor;
        double effectiveTolerance = tolerance;
        if (from == null) {
            from = new double[] {0, 0, 0, 0};
            effectiveTolerance = 2;
        }
        RoboDK.checkColor(toColor);
        RoboDK.checkColor(from);
        link.sendLine("Recolor");
        link.sendItem(this);
        double[] combined = new double[9];
        combined[0] = effectiveTolerance;
        System.arraycopy(from, 0, combined, 1, 4);
        System.arraycopy(toColor, 0, combined, 5, 4);
        link.sendArray(combined);
        link.checkStatus();
    }

    /** @see #recolor(double[], double[], double) */
    public void recolor(double[] toColor) {
        recolor(toColor, null, 0.1);
    }

    /** Sets the color of every shape of this item. */
    public void setColor(double[] toColor) {
        RoboDK.checkColor(toColor);
        link.checkConnection();
        link.sendLine("S_Color");
        link.sendItem(this);
        link.sendArray(toColor);
        link.checkStatus();
    }

    /** Sets the color of a single shape (by id) of this item. */
    public void setColor(int shapeId, double[] toColor) {
        RoboDK.checkColor(toColor);
        link.checkConnection();
        link.sendLine("S_ShapeColor");
        link.sendItem(this);
        link.sendInt(shapeId);
        link.sendArray(toColor);
        link.checkStatus();
    }

    /** Sets the color of a curve (by id, or every curve if -1) of this item. */
    public void setColorCurve(double[] toColor, int curveId) {
        RoboDK.checkColor(toColor);
        link.checkConnection();
        link.sendLine("S_CurveColor");
        link.sendItem(this);
        link.sendInt(curveId);
        link.sendArray(toColor);
        link.checkStatus();
    }

    /** @see #setColorCurve(double[], int) */
    public void setColorCurve(double[] toColor) {
        setColorCurve(toColor, -1);
    }

    /** Returns the current color of this item, as an RGBA array in the 0-1 range. */
    public double[] getColor() {
        link.checkConnection();
        link.sendLine("G_Color");
        link.sendItem(this);
        double[] color = link.recvArray();
        link.checkStatus();
        return color;
    }

    /** Sets the transparency (0 = fully transparent, 1 = fully opaque) of this item. */
    public void setTransparency(double alpha) {
        double clamped = Math.min(1, Math.max(0, alpha));
        link.checkConnection();
        link.sendLine("S_Color");
        link.sendItem(this);
        link.sendArray(new double[] {-1, -1, -1, clamped});
        link.checkStatus();
    }

    /** Scales this object's geometry uniformly, or per-axis with a 3-value array. */
    public void scale(double[] scale) {
        if (scale.length != 3) {
            throw new RdkException("scale must be a 3-value array [scale_x, scale_y, scale_z]");
        }
        link.checkConnection();
        link.sendLine("Scale");
        link.sendItem(this);
        link.sendArray(scale);
        link.checkStatus();
    }

    /** @see #scale(double[]) */
    public void scale(double factor) {
        scale(new double[] {factor, factor, factor});
    }

    // ------------------------------------------------------------------------------------
    // Geometry
    // ------------------------------------------------------------------------------------

    /** Adds a shape (as triangles) to this object. @see RoboDK#addShape(Mat, Item) */
    public Item addShape(Mat trianglePoints) {
        return link.addShape(trianglePoints, this);
    }

    /** Adds a curve (as a list of points) to this object. @see RoboDK#addCurve(Mat, Item, boolean, ProjectionType) */
    public Item addCurve(Mat curvePoints, boolean addToRef, ProjectionType projectionType) {
        return link.addCurve(curvePoints, this, addToRef, projectionType);
    }

    /** @see #addCurve(Mat, boolean, ProjectionType) */
    public Item addCurve(Mat curvePoints) {
        return addCurve(curvePoints, false, ProjectionType.ALONG_NORMAL_RECALC);
    }

    /** Adds a list of points to this object. @see RoboDK#addPoints(Mat, Item, boolean, ProjectionType) */
    public Item addPoints(Mat points, boolean addToRef, ProjectionType projectionType) {
        return link.addPoints(points, this, addToRef, projectionType);
    }

    /** @see #addPoints(Mat, boolean, ProjectionType) */
    public Item addPoints(Mat points) {
        return addPoints(points, false, ProjectionType.ALONG_NORMAL_RECALC);
    }

    /** Projects a list of points onto this object's surface. */
    public Mat projectPoints(Mat points, ProjectionType projectionType) {
        return link.projectPoints(points, this, projectionType);
    }

    /** Copies the geometry (faces) of {@code source} into this item, at the given relative pose. */
    public void addGeometry(Item source, Mat pose) {
        link.checkConnection();
        link.sendLine("CopyFaces");
        link.sendItem(source);
        link.sendItem(this);
        link.sendPose(pose);
        link.checkStatus();
    }

    /** Loads a file and attaches it to this item. @see RoboDK#addFile(String, Item) */
    public Item addFile(String filename) {
        return link.addFile(filename, this);
    }

    // ------------------------------------------------------------------------------------
    // Poses
    // ------------------------------------------------------------------------------------

    /** Returns the geometry (mesh) pose of this item, relative to its own local pose. */
    public Mat getGeometryPose() {
        link.checkConnection();
        link.sendLine("G_Hgeom");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /** Sets the geometry (mesh) pose of this item, relative to its own local pose. */
    public void setGeometryPose(Mat pose) {
        link.checkConnection();
        link.sendLine("S_Hgeom");
        link.sendItem(this);
        link.sendPose(pose);
        link.checkStatus();
    }

    /** For a tool item, returns the tool center point (TCP) pose relative to the robot flange. */
    public Mat getHtool() {
        link.checkConnection();
        link.sendLine("G_Htool");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /** For a tool item, sets the tool center point (TCP) pose relative to the robot flange. */
    public void setHtool(Mat pose) {
        link.checkConnection();
        link.sendLine("S_Htool");
        link.sendItem(this);
        link.sendPose(pose);
        link.checkStatus();
    }

    /** For a robot, returns the currently active tool's TCP pose relative to the robot flange. */
    public Mat getPoseTool() {
        link.checkConnection();
        link.sendLine("G_Tool");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /** For a robot, returns the currently active reference frame's pose relative to the robot base. */
    public Mat getPoseFrame() {
        link.checkConnection();
        link.sendLine("G_Frame");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /** Sets the active reference frame of a robot (or a target/program) directly by pose. */
    public void setPoseFrame(Mat framePose) {
        link.checkConnection();
        link.sendLine("S_Frame");
        link.sendPose(framePose);
        link.sendItem(this);
        link.checkStatus();
    }

    /** Sets the active reference frame of a robot (or a target/program) to an existing frame item. */
    public void setPoseFrame(Item frameItem) {
        link.checkConnection();
        link.sendLine("S_Frame_ptr");
        link.sendItem(frameItem);
        link.sendItem(this);
        link.checkStatus();
    }

    /** Sets the active tool of a robot (or a target/program) directly by TCP pose. */
    public void setPoseTool(Mat toolPose) {
        link.checkConnection();
        link.sendLine("S_Tool");
        link.sendPose(toolPose);
        link.sendItem(this);
        link.checkStatus();
    }

    /** Sets the active tool of a robot (or a target/program) to an existing tool item. */
    public void setPoseTool(Item toolItem) {
        link.checkConnection();
        link.sendLine("S_Tool_ptr");
        link.sendItem(toolItem);
        link.sendItem(this);
        link.checkStatus();
    }

    /** @see #setPoseFrame(Item) */
    public void setFrame(Item frame) {
        setPoseFrame(frame);
    }

    /** @see #setPoseFrame(Mat) */
    public void setFrame(Mat frame) {
        setPoseFrame(frame);
    }

    /** @see #setPoseTool(Item) */
    public void setTool(Item tool) {
        setPoseTool(tool);
    }

    /** @see #setPoseTool(Mat) */
    public void setTool(Mat tool) {
        setPoseTool(tool);
    }

    /** Adds a new, empty tool with the given TCP pose to this robot. */
    public Item addTool(Mat toolPose, String toolName) {
        link.checkConnection();
        link.sendLine("AddToolEmpty");
        link.sendItem(this);
        link.sendPose(toolPose);
        link.sendLine(toolName);
        Item newTool = link.recvItem();
        link.checkStatus();
        return newTool;
    }

    /** @see #addTool(Mat, String) */
    public Item addTool(Mat toolPose) {
        return addTool(toolPose, "New TCP");
    }

    /** Sets the absolute (station-relative) pose of this item. */
    public void setPoseAbs(Mat pose) {
        link.checkConnection();
        link.sendLine("S_Hlocal_Abs");
        link.sendItem(this);
        link.sendPose(pose);
        link.checkStatus();
    }

    /** Returns the absolute (station-relative) pose of this item. */
    public Mat getPoseAbs() {
        link.checkConnection();
        link.sendLine("G_Hlocal_Abs");
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    // ------------------------------------------------------------------------------------
    // Target items
    // ------------------------------------------------------------------------------------

    /** Marks this target as a Cartesian (pose-based) target. */
    public void setAsCartesianTarget() {
        link.checkConnection();
        link.sendLine("S_Target_As_RT");
        link.sendItem(this);
        link.checkStatus();
    }

    /** Marks this target as a joint-based target. */
    public void setAsJointTarget() {
        link.checkConnection();
        link.sendLine("S_Target_As_JT");
        link.sendItem(this);
        link.checkStatus();
    }

    /** Returns {@code true} if this target is a joint-based target (as opposed to Cartesian). */
    public boolean isJointTarget() {
        link.checkConnection();
        link.sendLine("Target_Is_JT");
        link.sendItem(this);
        int result = link.recvInt();
        link.checkStatus();
        return result > 0;
    }

    // ------------------------------------------------------------------------------------
    // Robot: state, kinematics, links
    // ------------------------------------------------------------------------------------

    /** For a robot, returns the simulated (as opposed to real, connected) joint values. */
    public double[] getSimulatorJoints() {
        link.checkConnection();
        link.sendLine("G_Thetas_Sim");
        link.sendItem(this);
        double[] joints = link.recvArray();
        link.checkStatus();
        return joints;
    }

    /** Returns the home joint values of this robot. */
    public double[] getJointsHome() {
        link.checkConnection();
        link.sendLine("G_Home");
        link.sendItem(this);
        double[] joints = link.recvArray();
        link.checkStatus();
        return joints;
    }

    /** Sets the home joint values of this robot. */
    public void setJointsHome(double[] joints) {
        link.checkConnection();
        link.sendLine("S_Home");
        link.sendArray(joints);
        link.sendItem(this);
        link.checkStatus();
    }

    /** Returns the object attached to this robot at the given link id (0 = end effector). */
    public Item getObjectLink(int linkId) {
        link.checkConnection();
        link.sendLine("G_LinkObjId");
        link.sendItem(this);
        link.sendInt(linkId);
        Item linked = link.recvItem();
        link.checkStatus();
        return linked;
    }

    /** @see #getObjectLink(int) */
    public Item getObjectLink() {
        return getObjectLink(0);
    }

    /** Returns the item of the given type that this item is linked to (for example, its robot). */
    public Item getLink(ItemType typeLinked) {
        link.checkConnection();
        link.sendLine("G_LinkType");
        link.sendItem(this);
        link.sendInt(typeLinked.getValue());
        Item linked = link.recvItem();
        link.checkStatus();
        return linked;
    }

    /** @see #getLink(ItemType) */
    public Item getLinkedItem() {
        return getLink(ItemType.ROBOT);
    }

    /**
     * Returns the joint value bounds of this robot.
     *
     * @return a 2-element array: {@code [lowerLimits, upperLimits]}
     */
    public double[][] getJointLimits() {
        link.checkConnection();
        link.sendLine("G_RobLimits");
        link.sendItem(this);
        double[] lowerLimits = link.recvArray();
        double[] upperLimits = link.recvArray();
        link.recvInt(); // Joints type (unused).
        link.checkStatus();
        return new double[][] {lowerLimits, upperLimits};
    }

    /** Sets the joint value bounds of this robot. */
    public void setJointLimits(double[] lowerLimits, double[] upperLimits) {
        link.checkConnection();
        link.sendLine("S_RobLimits");
        link.sendItem(this);
        link.sendArray(lowerLimits);
        link.sendArray(upperLimits);
        link.checkStatus();
    }

    /** Attaches a target/object/program to a specific robot (or mechanism). */
    public void setRobot(Item robot) {
        link.checkConnection();
        link.sendLine("S_Robot");
        link.sendItem(this);
        link.sendItem(robot);
        link.checkStatus();
    }

    /** @see #setRobot(Item) */
    public void setRobot() {
        setRobot(null);
    }

    /** Links this item to another one (for example, a tool to the robot that uses it). */
    public void setLink(Item item) {
        link.checkConnection();
        link.sendLine("S_Link_ptr");
        link.sendItem(item);
        link.sendItem(this);
        link.checkStatus();
    }

    /** Computes the robot flange pose for the given joint values (forward kinematics). */
    public Mat solveFK(double[] joints) {
        link.checkConnection();
        link.sendLine("G_FK");
        link.sendArray(joints);
        link.sendItem(this);
        Mat pose = link.recvPose();
        link.checkStatus();
        return pose;
    }

    /** Returns the robot configuration (turn/flip flags) for the given joint values. */
    public double[] getJointsConfig(double[] joints) {
        link.checkConnection();
        link.sendLine("G_Thetas_Config");
        link.sendArray(joints);
        link.sendItem(this);
        double[] config = link.recvArray();
        link.checkStatus();
        return config;
    }

    /**
     * Computes a joint solution reaching the given pose (inverse kinematics), close to {@code
     * jointsApprox} if provided.
     *
     * @return the joint solution, or an empty array if no solution was found
     */
    public double[] solveIK(Mat pose, double[] jointsApprox, Mat tool, Mat reference) {
        Mat targetPose = pose;
        if (tool != null) {
            targetPose = targetPose.multiply(tool.invert());
        }
        if (reference != null) {
            targetPose = reference.multiply(targetPose);
        }
        link.checkConnection();
        if (jointsApprox == null) {
            link.sendLine("G_IK");
            link.sendPose(targetPose);
        } else {
            link.sendLine("G_IK_jnts");
            link.sendPose(targetPose);
            link.sendArray(jointsApprox);
        }
        link.sendItem(this);
        double[] joints = link.recvArray();
        link.checkStatus();
        return joints;
    }

    /** @see #solveIK(Mat, double[], Mat, Mat) */
    public double[] solveIK(Mat pose) {
        return solveIK(pose, null, null, null);
    }

    /** Computes every joint solution reaching the given pose (complete inverse kinematics). */
    public Mat solveIkAll(Mat pose, Mat tool, Mat reference) {
        Mat targetPose = pose;
        if (tool != null) {
            targetPose = targetPose.multiply(tool.invert());
        }
        if (reference != null) {
            targetPose = reference.multiply(targetPose);
        }
        link.checkConnection();
        link.sendLine("G_IK_cmpl");
        link.sendPose(targetPose);
        link.sendItem(this);
        Mat jointsList = link.recvMatrix();
        link.checkStatus();
        return jointsList;
    }

    /** @see #solveIkAll(Mat, Mat, Mat) */
    public Mat solveIkAll(Mat pose) {
        return solveIkAll(pose, null, null);
    }

    // ------------------------------------------------------------------------------------
    // Robot: online connection to the physical controller
    // ------------------------------------------------------------------------------------

    /** Connects to the physical robot controller through its (already configured) robot driver. */
    public boolean connectRobot(String robotIp) {
        link.checkConnection();
        link.sendLine("Connect");
        link.sendItem(this);
        link.sendLine(robotIp);
        int status = link.recvInt();
        link.checkStatus();
        return status != 0;
    }

    /** @see #connectRobot(String) */
    public boolean connectRobot() {
        return connectRobot("");
    }

    /** Disconnects from the physical robot controller. */
    public boolean disconnectRobot() {
        link.checkConnection();
        link.sendLine("Disconnect");
        link.sendItem(this);
        int status = link.recvInt();
        link.checkStatus();
        return status != 0;
    }

    // ------------------------------------------------------------------------------------
    // Robot: movement
    // ------------------------------------------------------------------------------------

    private void moveX(Item target, double[] joints, Mat pose, int moveType, boolean blocking) {
        link.checkConnection();
        waitMove(300);
        link.sendLine(blocking ? "MoveXb" : "MoveX");
        link.sendInt(moveType);
        if (target != null) {
            link.sendInt(3);
            link.sendArray(null);
            link.sendItem(target);
        } else if (joints != null) {
            link.sendInt(1);
            link.sendArray(joints);
            link.sendItem(null);
        } else if (pose != null && pose.isHomogeneous()) {
            link.sendInt(2);
            link.sendArray(pose.toDoubles());
            link.sendItem(null);
        } else {
            throw new RdkException("Invalid target: expected an item, a joint array, or a homogeneous pose");
        }
        link.sendItem(this);
        link.checkStatus();
        if (blocking) {
            int previousTimeout = link.getSocketTimeoutMilliseconds();
            link.setSocketTimeoutMilliseconds(360_000_000);
            try {
                link.checkStatus();
            } finally {
                link.setSocketTimeoutMilliseconds(previousTimeout);
            }
        }
    }

    private void moveC(Item target1, double[] joints1, Mat pose1, Item target2, double[] joints2, Mat pose2,
                        boolean blocking) {
        link.checkConnection();
        waitMove(300);
        link.sendLine(blocking ? "MoveCb" : "MoveC");
        link.sendInt(3);
        sendMoveTarget(target1, joints1, pose1, "1");
        sendMoveTarget(target2, joints2, pose2, "2");
        link.sendItem(this);
        link.checkStatus();
        if (blocking) {
            int previousTimeout = link.getSocketTimeoutMilliseconds();
            link.setSocketTimeoutMilliseconds(360_000_000);
            try {
                link.checkStatus();
            } finally {
                link.setSocketTimeoutMilliseconds(previousTimeout);
            }
        }
    }

    private void sendMoveTarget(Item target, double[] joints, Mat pose, String label) {
        if (target != null) {
            link.sendInt(3);
            link.sendArray(null);
            link.sendItem(target);
        } else if (joints != null) {
            link.sendInt(1);
            link.sendArray(joints);
            link.sendItem(null);
        } else if (pose != null && pose.isHomogeneous()) {
            link.sendInt(2);
            link.sendArray(pose.toDoubles());
            link.sendItem(null);
        } else {
            throw new RdkException("Invalid type of target " + label);
        }
    }

    /**
     * Moves a robot to a target using a joint move (a straight line in the joint space). If this
     * item is a program, this instead adds a joint move instruction to it.
     */
    public void moveJ(Item target, boolean blocking) {
        if (getItemType() == ItemType.PROGRAM) {
            addMoveJ(target);
        } else {
            moveX(target, null, null, 1, blocking);
        }
    }

    /** @see #moveJ(Item, boolean) */
    public void moveJ(Item target) {
        moveJ(target, true);
    }

    /** @see #moveJ(Item, boolean) */
    public void moveJ(double[] joints, boolean blocking) {
        moveX(null, joints, null, 1, blocking);
    }

    /** @see #moveJ(Item, boolean) */
    public void moveJ(double[] joints) {
        moveJ(joints, true);
    }

    /** @see #moveJ(Item, boolean) */
    public void moveJ(Mat target, boolean blocking) {
        moveX(null, null, target, 1, blocking);
    }

    /** @see #moveJ(Item, boolean) */
    public void moveJ(Mat target) {
        moveJ(target, true);
    }

    /**
     * Moves a robot to a target using a linear move (a straight line in Cartesian space). If
     * this item is a program, this instead adds a linear move instruction to it.
     */
    public void moveL(Item target, boolean blocking) {
        if (getItemType() == ItemType.PROGRAM) {
            addMoveL(target);
        } else {
            moveX(target, null, null, 2, blocking);
        }
    }

    /** @see #moveL(Item, boolean) */
    public void moveL(Item target) {
        moveL(target, true);
    }

    /** @see #moveL(Item, boolean) */
    public void moveL(double[] joints, boolean blocking) {
        moveX(null, joints, null, 2, blocking);
    }

    /** @see #moveL(Item, boolean) */
    public void moveL(double[] joints) {
        moveL(joints, true);
    }

    /** @see #moveL(Item, boolean) */
    public void moveL(Mat target, boolean blocking) {
        moveX(null, null, target, 2, blocking);
    }

    /** @see #moveL(Item, boolean) */
    public void moveL(Mat target) {
        moveL(target, true);
    }

    /** Moves a robot along a circular arc through two targets (start already reached, midpoint, end). */
    public void moveC(Item target1, Item target2, boolean blocking) {
        moveC(target1, null, null, target2, null, null, blocking);
    }

    /** @see #moveC(Item, Item, boolean) */
    public void moveC(Item target1, Item target2) {
        moveC(target1, target2, true);
    }

    /** @see #moveC(Item, Item, boolean) */
    public void moveC(double[] joints1, double[] joints2, boolean blocking) {
        moveC(null, joints1, null, null, joints2, null, blocking);
    }

    /** @see #moveC(Item, Item, boolean) */
    public void moveC(double[] joints1, double[] joints2) {
        moveC(joints1, joints2, true);
    }

    /** @see #moveC(Item, Item, boolean) */
    public void moveC(Mat target1, Mat target2, boolean blocking) {
        moveC(null, null, target1, null, null, target2, blocking);
    }

    /** @see #moveC(Item, Item, boolean) */
    public void moveC(Mat target1, Mat target2) {
        moveC(target1, target2, true);
    }

    /**
     * Sets the robot movement speed and acceleration; pass a negative value to leave a parameter
     * unchanged.
     *
     * @param speedLinear linear speed in mm/s
     * @param accelLinear linear acceleration in mm/s^2
     * @param speedJoints joint speed in deg/s (rotary axes) or mm/s (linear axes)
     * @param accelJoints joint acceleration in deg/s^2 or mm/s^2
     */
    public void setSpeed(double speedLinear, double accelLinear, double speedJoints, double accelJoints) {
        link.checkConnection();
        link.sendLine("S_Speed4");
        link.sendItem(this);
        link.sendArray(new double[] {speedLinear, speedJoints, accelLinear, accelJoints});
        link.checkStatus();
    }

    /** @see #setSpeed(double, double, double, double) */
    public void setSpeed(double speedLinear) {
        setSpeed(speedLinear, -1, -1, -1);
    }

    /** Sets the linear acceleration only, leaving speed and joint motion unchanged. */
    public void setAcceleration(double accelLinear) {
        setSpeed(-1, accelLinear, -1, -1);
    }

    /** Sets the joint speed only, leaving linear motion unchanged. */
    public void setSpeedJoints(double speedJoints) {
        setSpeed(-1, -1, speedJoints, -1);
    }

    /** Sets the joint acceleration only, leaving linear motion unchanged. */
    public void setAccelerationJoints(double accelJoints) {
        setSpeed(-1, -1, -1, accelJoints);
    }

    /** Sets the rounding/blending radius (zone data) used between consecutive movements. */
    public void setRounding(double roundingMm) {
        link.checkConnection();
        link.sendLine("S_ZoneData");
        link.sendInt((int) (roundingMm * 1000.0));
        link.sendItem(this);
        link.checkStatus();
    }

    /** @see #setRounding(double) */
    public void setZoneData(double roundingMm) {
        setRounding(roundingMm);
    }

    /** Returns {@code true} if the robot (or program) is currently moving/running. */
    public boolean isBusy() {
        link.checkConnection();
        link.sendLine("IsBusy");
        link.sendItem(this);
        int busy = link.recvInt();
        link.checkStatus();
        return busy > 0;
    }

    /** Stops the current robot movement (or program execution). */
    public void stop() {
        link.checkConnection();
        link.sendLine("Stop");
        link.sendItem(this);
        link.checkStatus();
    }

    /** Blocks until the robot has finished its current movement, or {@code timeoutSec} elapses. */
    public void waitMove(double timeoutSec) {
        link.checkConnection();
        link.sendLine("WaitMove");
        link.sendItem(this);
        link.checkStatus();
        int previousTimeout = link.getSocketTimeoutMilliseconds();
        link.setSocketTimeoutMilliseconds((int) (timeoutSec * 1000.0));
        try {
            link.checkStatus();
        } finally {
            link.setSocketTimeoutMilliseconds(previousTimeout);
        }
    }

    /** @see #waitMove(double) */
    public void waitMove() {
        waitMove(300);
    }

    /** Blocks until {@link #isBusy()} returns {@code false} (polling every 50 ms). */
    public void waitFinished() {
        while (isBusy()) {
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    // ------------------------------------------------------------------------------------
    // Program items
    // ------------------------------------------------------------------------------------

    /** Adds a joint-move instruction to this program, targeting {@code target}. */
    public void addMoveJ(Item target) {
        link.checkConnection();
        link.sendLine("Add_INSMOVE");
        link.sendItem(target);
        link.sendItem(this);
        link.sendInt(1);
        link.checkStatus();
    }

    /** Adds a linear-move instruction to this program, targeting {@code target}. */
    public void addMoveL(Item target) {
        link.checkConnection();
        link.sendLine("Add_INSMOVE");
        link.sendItem(target);
        link.sendItem(this);
        link.sendInt(2);
        link.checkStatus();
    }

    /** Shows or hides this program's instructions in the 3D view. */
    public void showInstructions(boolean show) {
        link.checkConnection();
        link.sendLine("Prog_ShowIns");
        link.sendItem(this);
        link.sendInt(show ? 1 : 0);
        link.checkStatus();
    }

    /** @see #showInstructions(boolean) */
    public void showInstructions() {
        showInstructions(true);
    }

    /** Shows or hides this program's targets in the 3D view. */
    public void showTargets(boolean show) {
        link.checkConnection();
        link.sendLine("Prog_ShowTargets");
        link.sendItem(this);
        link.sendInt(show ? 1 : 0);
        link.checkStatus();
    }

    /** @see #showTargets(boolean) */
    public void showTargets() {
        showTargets(true);
    }

    /** Returns the number of instructions in this program. */
    public int getInstructionCount() {
        link.checkConnection();
        link.sendLine("Prog_Nins");
        link.sendItem(this);
        int count = link.recvInt();
        link.checkStatus();
        return count;
    }

    /** Deletes an instruction (by index) from this program. */
    public boolean deleteInstruction(int instructionId) {
        link.checkConnection();
        link.sendLine("Prog_DelIns");
        link.sendItem(this);
        link.sendInt(instructionId);
        int result = link.recvInt();
        link.checkStatus();
        return result > 0;
    }

    /** Selects an instruction (by index) in the program editor; {@code -1} selects the last one. */
    public int selectInstruction(int instructionId) {
        link.checkConnection();
        link.sendLine("Prog_SelIns");
        link.sendItem(this);
        link.sendInt(instructionId);
        int result = link.recvInt();
        link.checkStatus();
        return result;
    }

    /** @see #selectInstruction(int) */
    public int selectInstruction() {
        return selectInstruction(-1);
    }

    /** Runs this program (non-blocking); see {@link #isBusy()}/{@link #waitFinished()}. */
    public int runProgram() {
        link.checkConnection();
        link.sendLine("RunProg");
        link.sendItem(this);
        int status = link.recvInt();
        link.checkStatus();
        return status;
    }

    /** Runs this program with the given parameters (non-blocking, for Python programs). */
    public int runCode(String parameters) {
        link.checkConnection();
        if (parameters == null) {
            link.sendLine("RunProg");
            link.sendItem(this);
        } else {
            link.sendLine("RunProgParam");
            link.sendItem(this);
            link.sendLine(parameters);
        }
        int status = link.recvInt();
        link.checkStatus();
        return status;
    }

    /** @see #runCode(String) */
    public int runCode() {
        return runCode(null);
    }

    /**
     * Adds a program call, raw code, a comment, or a message to this program.
     *
     * @param code text to insert (its meaning depends on {@code runType})
     * @param runType 0 = call program, 1 = insert code, 2 = start thread, 3 = comment, 4 = show message
     */
    public boolean runInstruction(String code, int runType) {
        link.checkConnection();
        link.sendLine("RunCode2");
        link.sendItem(this);
        link.sendLine(code.replace("\n\n", "<br>").replace("\n", "<br>"));
        link.sendInt(runType);
        int status = link.recvInt();
        link.checkStatus();
        return status == 0;
    }

    /** @see #runInstruction(String, int) */
    public boolean runInstruction(String code) {
        return runInstruction(code, 0);
    }

    /** Pauses program generation/simulation for {@code timeMs} milliseconds ({@code -1} pauses until resumed). */
    public void pause(double timeMs) {
        link.checkConnection();
        link.sendLine("RunPause");
        link.sendItem(this);
        link.sendInt((int) (timeMs * 1000.0));
        link.checkStatus();
    }

    /** @see #pause(double) */
    public void pause() {
        pause(-1);
    }

    /** Sets a digital output, either in the program being generated or on the connected robot. */
    public void setDigitalOutput(String ioVariable, String ioValue) {
        link.checkConnection();
        link.sendLine("setDO");
        link.sendItem(this);
        link.sendLine(ioVariable);
        link.sendLine(ioValue);
        link.checkStatus();
    }

    /** Sets an analog output, either in the program being generated or on the connected robot. */
    public void setAnalogOutput(String ioVariable, String ioValue) {
        link.checkConnection();
        link.sendLine("setAO");
        link.sendItem(this);
        link.sendLine(ioVariable);
        link.sendLine(ioValue);
        link.checkStatus();
    }

    /** Reads a digital input, either from the program being generated or from the connected robot. */
    public String getDigitalInput(String ioVariable) {
        link.checkConnection();
        link.sendLine("getDI");
        link.sendItem(this);
        link.sendLine(ioVariable);
        String result = link.recvLine();
        link.checkStatus();
        return result;
    }

    /** Reads an analog input, either from the program being generated or from the connected robot. */
    public String getAnalogInput(String ioVariable) {
        link.checkConnection();
        link.sendLine("getAI");
        link.sendItem(this);
        link.sendLine(ioVariable);
        String result = link.recvLine();
        link.checkStatus();
        return result;
    }

    /** Waits for a digital input to reach the given value, up to {@code timeoutMs} ({@code -1} = wait forever). */
    public void waitDigitalInput(String ioVariable, String ioValue, double timeoutMs) {
        link.checkConnection();
        link.sendLine("waitDI");
        link.sendItem(this);
        link.sendLine(ioVariable);
        link.sendLine(ioValue);
        link.sendInt((int) (timeoutMs * 1000.0));
        link.checkStatus();
    }

    /** @see #waitDigitalInput(String, String, double) */
    public void waitDigitalInput(String ioVariable, String ioValue) {
        waitDigitalInput(ioVariable, ioValue, -1);
    }

    /** Enables/disables sub-millimeter accuracy (inverse kinematics accuracy correction) for this robot. */
    public void setAccuracyActive(boolean accurate) {
        link.checkConnection();
        link.sendLine("S_AbsAccOn");
        link.sendItem(this);
        link.sendInt(accurate ? 1 : 0);
        link.checkStatus();
    }

    /** @see #setAccuracyActive(boolean) */
    public boolean isAccuracyActive() {
        link.checkConnection();
        link.sendLine("G_AbsAccOn");
        link.sendItem(this);
        int result = link.recvInt();
        link.checkStatus();
        return result != 0;
    }

    /** Flushes any pending program generation and disconnects; the underlying {@link RoboDK} link becomes unusable. */
    public void finish() {
        link.disconnect();
    }

    // ------------------------------------------------------------------------------------
    // Item flags
    // ------------------------------------------------------------------------------------

    /** Updates this item's flags, controlling how much access the user has to it; see {@link ItemFlags}. */
    public void setFlags(int itemFlags) {
        link.checkConnection();
        link.sendLine("S_Item_Rights");
        link.sendItem(this);
        link.sendInt(itemFlags);
        link.checkStatus();
    }

    /** @see #setFlags(int) */
    public void setFlags() {
        setFlags(ItemFlags.ALL);
    }

    /** Returns this item's current flags; see {@link ItemFlags}. */
    public int getFlags() {
        link.checkConnection();
        link.sendLine("G_Item_Rights");
        link.sendItem(this);
        int flags = link.recvInt();
        link.checkStatus();
        return flags;
    }

    // ------------------------------------------------------------------------------------
    // Program run type
    // ------------------------------------------------------------------------------------

    /** Sets whether this program (made through the GUI) runs in the simulator only, or on the physical robot. */
    public void setRunType(ProgramExecutionType programExecutionType) {
        link.checkConnection();
        link.sendLine("S_ProgRunType");
        link.sendItem(this);
        link.sendInt(programExecutionType.getValue());
        link.checkStatus();
    }

    /** @see #setRunType(ProgramExecutionType) */
    public ProgramExecutionType getRunType() {
        link.checkConnection();
        link.sendLine("G_ProgRunType");
        link.sendItem(this);
        int result = link.recvInt();
        link.checkStatus();
        return ProgramExecutionType.fromValue(result);
    }

    // ------------------------------------------------------------------------------------
    // Robot: physical connection details
    // ------------------------------------------------------------------------------------

    /** Returns the current connection status to the physical robot controller. */
    public RobotConnectionType connectedState() {
        link.checkConnection();
        link.sendLine("ConnectedState");
        link.sendItem(this);
        RobotConnectionType status = RobotConnectionType.fromValue(link.recvInt());
        link.recvLine(); // Status message (unused).
        link.checkStatus();
        return status;
    }

    /** Returns the robot driver connection parameters (IP, port, remote path, FTP credentials). */
    public RobotConnectionParameters connectionParams() {
        link.checkConnection();
        link.sendLine("ConnectParams");
        link.sendItem(this);
        String robotIp = link.recvLine();
        int port = link.recvInt();
        String remotePath = link.recvLine();
        String ftpUser = link.recvLine();
        String ftpPass = link.recvLine();
        link.checkStatus();
        return new RobotConnectionParameters(robotIp, port, remotePath, ftpUser, ftpPass);
    }

    /** Sets the robot driver connection parameters (IP, port, remote path, FTP credentials). */
    public void setConnectionParams(String robotIp, int port, String remotePath, String ftpUser, String ftpPass) {
        link.checkConnection();
        link.sendLine("setConnectParams");
        link.sendItem(this);
        link.sendLine(robotIp);
        link.sendInt(port);
        link.sendLine(remotePath);
        link.sendLine(ftpUser);
        link.sendLine(ftpPass);
        link.checkStatus();
    }

    // ------------------------------------------------------------------------------------
    // Sequence display
    // ------------------------------------------------------------------------------------

    /** Displays a sequence of poses (for example a path being planned) directly, as a matrix. */
    public void showSequence(Mat sequence) {
        link.checkConnection();
        link.sendLine("Show_Seq");
        link.sendMatrix(sequence);
        link.sendItem(this);
        link.checkStatus();
    }

    /**
     * Displays a sequence of joint values or poses, as a temporary animation over this item
     * (typically a robot or a program).
     *
     * @param joints list of joint value arrays; used when {@code flags} includes {@link SequenceDisplayFlags#ROBOT_JOINTS}
     * @param poses list of poses; used otherwise
     * @param flags a bitwise OR of {@link SequenceDisplayFlags} constants
     * @param timeoutMilliseconds how long the sequence stays displayed, or -1 for no timeout
     */
    public void showSequence(List<double[]> joints, List<Mat> poses, int flags, int timeoutMilliseconds) {
        if (joints == null && poses == null) {
            return;
        }
        link.checkConnection();
        link.sendLine("Show_SeqPoses");
        link.sendItem(this);
        link.sendArray(new double[] {flags, timeoutMilliseconds});
        boolean useJoints = flags != SequenceDisplayFlags.DEFAULT && (flags & SequenceDisplayFlags.ROBOT_JOINTS) != 0;
        if (useJoints) {
            link.sendInt(joints.size());
            for (double[] jointValues : joints) {
                link.sendArray(jointValues);
            }
        } else {
            link.sendInt(poses.size());
            for (Mat pose : poses) {
                link.sendPose(pose);
            }
        }
        link.checkStatus();
    }
}
