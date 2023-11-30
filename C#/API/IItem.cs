// ----------------------------------------------------------------------------------------------------------
// Copyright 2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ----------------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------------
// This file (RoboDK.cs) implements the RoboDK API for C#
// This file defines the following classes:
//     Mat: Matrix class, useful pose operations
//     RoboDK: API to interact with RoboDK
//     RoboDK.Item: Any item in the RoboDK station tree
//
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the RoboDK() object (such as RoboDK.GetItem() method) 
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API for Python here:
//     https://robodk.com/doc/en/CsAPI/index.html
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
// This library includes the mathematics to operate with homogeneous matrices for robotics.
// ----------------------------------------------------------------------------------------------------------

#region Namespaces

using System;
using System.Collections.Generic;
#if NET45
using System.Windows.Media;
#else
using System.Drawing;
#endif
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IItem
    {
        #region Properties

        long ItemId { get; }

        #endregion

        #region Public Methods

        /// <summary>
        /// Make a copy of the item with a new roboDK link.
        /// </summary>
        /// <param name="connectionLink">RoboDK link</param>
        /// <returns>new item</returns>
        IItem Clone(IRoboDK connectionLink);

        /// <summary>
        /// Update item flags. 
        /// Item flags allow defining how much access the user has to item-specific features. 
        /// </summary>
        /// <param name="itemFlags">Item Flags to be set</param>
        void SetItemFlags(ItemFlags itemFlags = ItemFlags.All);

        /// <summary>
        /// Retrieve current item flags. 
        /// Item flags allow defining how much access the user has to item-specific features. 
        /// </summary>
        /// <returns>Current Item Flags</returns>
        ItemFlags GetItemFlags();

        /// <summary>
        /// Compare this item with other item.
        /// Return true if they are the same; False otherwise.
        /// </summary>
        /// <param name="otherItem"></param>
        /// <returns>True if this item and other item is the same RoboDK item.</returns>
        bool Equals(IItem otherItem);

        /// <summary>
        ///     Use RDK() instead. Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        RoboDK RL();

        /// <summary>
        ///     Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        RoboDK RDK();

        /// <summary>
        /// Get RoboDK low level link interface.
        /// </summary>
        /// <returns></returns>
        RoboDK.IRoboDKLink GetRoboDkLink();

        /// <summary>
        ///     Create a new communication link. Use this for robots if you use a multithread application running multiple robots
        ///     at the same time.
        /// </summary>
        void NewLink();

        /// <summary>
        /// Returns the type of an item (robot, object, target, reference frame, ...)
        /// </summary>
        /// <returns></returns>
        ItemType GetItemType();

        /// <summary>
        ///     Save a station or object to a file
        /// </summary>
        /// <param name="filename"></param>
        void Save(string filename);

        /// <summary>
        ///     Deletes an item and its childs from the station.
        /// </summary>
        void Delete();

        /// <summary>
        ///     Checks if the item is valid. An invalid item will be returned by an unsuccessful function call.
        /// </summary>
        /// <returns>true if valid, false if invalid</returns>
        bool Valid();

        /// <summary>
        /// Attaches the item to a new parent while maintaining the relative position with its parent. The absolute position is changed.
        /// </summary>
        /// <param name="parent"></param>
        void SetParent(IItem parent);


        /// <summary>
        /// Attaches the item to another parent while maintaining the current absolute position in the station.
        /// The relationship between this item and its parent is changed to maintain the abosolute position.
        /// </summary>
        /// <param name="parent">parent item to attach this item</param>
        void SetParentStatic(IItem parent);

        /// <summary>
        /// Attach the closest object to the tool.
        /// Returns the item that was attached.
        /// Use item.Valid() to check if an object was attached to the tool.
        /// </summary>
        IItem AttachClosest();

        /// <summary>
        /// Detach the closest object attached to the tool (see also: setParentStatic).
        /// </summary>
        /// <param name="parent">New parent item to attach, such as a reference frame(optional). If not provided, the items held by the tool will be placed at the station root.</param>
        IItem DetachClosest(IItem parent = null);

        /// <summary>
        /// Detaches any object attached to a tool.
        /// </summary>
        /// <param name="parent">New parent item to attach, such as a reference frame(optional). If not provided, the items held by the tool will be placed at the station root.</param>
        void DetachAll(IItem parent = null);


        /// <summary>
        ///     Returns a list of the item childs that are attached to the provided item.
        /// </summary>
        /// <returns>item x n -> list of child items</returns>
        List<IItem> Childs();

        /// <summary>
        ///     Returns the parent item of this item.
        /// </summary>
        IItem Parent();

        /// <summary>
        ///     Returns 1 if the item is visible, otherwise, returns 0.
        /// </summary>
        /// <returns>true if visible, false if not visible</returns>
        bool Visible();

        /// <summary>
        ///     Sets the item visiblity status
        /// </summary>
        /// <param name="visible"></param>
        /// <param name="visibleFrame">srt the visible reference frame (1) or not visible (0)</param>
        void SetVisible(bool visible, VisibleRefType visibleFrame = VisibleRefType.Default);

        /// <summary>
        ///     Show an object or a robot link as collided (red)
        /// </summary>
        /// <param name="collided"></param>
        /// <param name="robotLinkId"></param>
        void ShowAsCollided(bool collided, int robotLinkId = 0);

        /// <summary>
        ///     Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
        /// </summary>
        /// <returns>name of the item</returns>
        string Name();

        /// <summary>
        ///     Set the name of a RoboDK item.
        /// </summary>
        /// <param name="name"></param>
        void SetName(string name);

		/// <summary>
		/// Sets the tool mass and center of gravity. This is only used with accurate robots to improve accuracy.
		/// </summary>
		/// <param name="toolMass">Tool weigth in Kg.</param>
		/// <param name="toolCOG">Tool center of gravity as [x,y,z] with respect to the robot flange.</param>
		void setParamRobotTool(double toolMass, double[] toolCOG);

        /// <summary>
        /// Send a specific parameter for an item.
        /// </summary>
        /// <param name="param">Command name</param>
        /// <param name="value">Command value (optional, not all commands require a value)</param>
        /// <returns>Command response</returns>
        string SetParam(string param, string value = "");

        /// <summary>
        /// Set a custom data parameter. Some items can hold custom data parameters.
        /// </summary>
        /// <param name="param"></param>
        /// <param name="value"></param>
        void SetParam(string param, byte[] value);

        /// <summary>
        /// Get a custom data parameter. Some items can hold custom data parameters.
        /// </summary>
        /// <param name="param"></param>
        /// <returns></returns>
        byte[] GetParam(string param);

        /// <summary>
        ///     Sets the local position (pose) of an object, target or reference frame. For example, the position of an
        ///     object/frame/target with respect to its parent.
        ///     If a robot is provided, it will set the pose of the end effector.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        void SetPose(Mat pose);

        /// <summary>
        ///     Returns the local position (pose) of an object, target or reference frame. For example, the position of an
        ///     object/frame/target with respect to its parent.
        ///     If a robot is provided, it will get the pose of the end effector
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat Pose();

        /// <summary>
        ///     Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for
        ///     tools and objects.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        void SetGeometryPose(Mat pose);

        /// <summary>
        ///     Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for
        ///     tools and objects.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat GeometryPose();

        /// <summary>
        ///     Obsolete: Use setPoseTool(pose) instead. Sets the tool pose of a tool item. If a robot is provided it will set the
        ///     tool pose of the active tool held by the robot.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        void SetHtool(Mat pose);

        /// <summary>
        ///     Obsolete: Use PoseTool() instead.
        ///     Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the
        ///     robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat Htool();

        /// <summary>
        ///     Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the
        ///     robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat PoseTool();

        /// <summary>
        ///     Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active
        ///     reference frame used by the robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat PoseFrame();

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP) to a frame position.
        ///     To set a new frame position <seealso cref="SetPoseFrame(IItem)"/>
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="framePose"></param>
        void SetPoseFrame(Mat framePose);

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP) to a frame position.
        ///     To set a new pose position <seealso cref="SetPoseFrame(Mat)"/>
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="frameItem"></param>
        void SetPoseFrame(IItem frameItem);

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4
        ///     Matrix.
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="toolPose"></param>
        void SetPoseTool(Mat toolPose);

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4
        ///     Matrix.
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="toolItem"></param>
        void SetPoseTool(IItem toolItem);

        /// <summary>
        ///     Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the
        ///     station origin.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        void SetPoseAbs(Mat pose);

        /// <summary>
        ///     Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to
        ///     the station origin.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        Mat PoseAbs();

        /// <summary>
        ///     Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values
        ///     range from 0 to 1.
        ///     Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        /// </summary>
        /// <param name="tocolor">color to change to</param>
        /// <param name="fromcolor">filter by this color</param>
        /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        void Recolor(double[] tocolor, double[] fromcolor = null, double tolerance = 0.1);

        /// <summary>
        ///     Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values
        ///     range from 0 to 1.
        ///     Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        /// </summary>
        /// <param name="tocolor">color to change to</param>
        /// <param name="fromcolor">filter by this color</param>
        /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        void Recolor(Color tocolor, Color? fromcolor = null, double tolerance = 0.1);

        /// <summary>
        /// Set the color of an object, tool or robot. 
        /// A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <param name="tocolor">color to set</param>
        /// <seealso cref="Item.GetColor"/>
        /// <seealso cref="Item.Recolor(System.Windows.Media.Color,System.Nullable{System.Windows.Media.Color},double)"/>
        void SetColor(Color tocolor);

        /// <summary>
        /// Set the color of an object shape. It can also be used for tools. A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <param name="shapeId">ID of the shape: the ID is the order in which the shape was added using AddShape()</param>
        /// <param name="tocolor">color to set</param>
        void SetColor(int shapeId, Color tocolor);

        /// <summary>
        /// Set the color of a curve object. It can also be used for tools. A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <param name="tocolor">color to set</param>        
        /// <param name="curveId">ID of the curve: the ID is the order in which the shape was added using AddCurve()</param>
        void SetColorCurve(Color tocolor, int curveId = -1);

        /// <summary>
        /// Set the alpha channel of an object, tool or robot. 
        /// The alpha channel must remain between 0 and 1.
        /// </summary>
        /// <param name="alpha">transparency level</param>
        /// <seealso cref="Item.GetColor"/>
        /// <seealso cref="Item.SetColor"/>
        /// <seealso cref="Item.Recolor(System.Windows.Media.Color,System.Nullable{System.Windows.Media.Color},double)"/>
        void SetTransparency(double alpha);

        /// <summary>
        /// Return the color of an Item (object, tool or robot). If the item has multiple colors it returns the first color available). 
        /// A color is in the format COLOR = [R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <returns>Color [R, G, B, A]</returns>
        /// <seealso cref="Item.SetColor"/>
        /// <seealso cref="Item.Recolor(System.Windows.Media.Color,System.Nullable{System.Windows.Media.Color},double)"/>
        Color GetColor();

        /// <summary>
        /// Apply a scale to an object to make it bigger or smaller.
        /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
        /// </summary>
        /// <param name="scale">scale to apply as [scale_x, scale_y, scale_z]</param>
        void Scale(double[] scale);

        /// <summary>
        ///     Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be
        ///     provided optionally.
        /// </summary>
        /// <param name="curvePoints">matrix 3xN or 6xN -> N must be multiple of 3</param>
        /// <param name="addToRef">add_to_ref -> If True, the curve will be added as part of the object in the RoboDK item tree</param>
        /// <param name="projectionType">
        ///     Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the
        ///     point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>returns the object where the curve was added or null if failed</returns>
        IItem AddCurve(Mat curvePoints, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        ///     Projects a point to the object given its coordinates. The provided points must be a list of [XYZ] coordinates.
        ///     Optionally, a vertex normal can be provided [XYZijk].
        /// </summary>
        /// <param name="points">matrix 3xN or 6xN -> list of points to project</param>
        /// <param name="projectionType">
        ///     projection_type -> Type of projection. For example: ProjectionType.AlongNormalRecalc will
        ///     project along the point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>projected points (empty matrix if failed)</returns>
        Mat ProjectPoints(Mat points, ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        /// Retrieve the currently selected feature for this object (surface, point, line, ...)
        /// </summary>
        /// <param name="featureType">The type of geometry, FEATURE_SURFACE, FEATURE_POINT, ... </param>
        /// <param name="featureId">The internal ID to retrieve the raw geometry (use GetPoints)</param>
        /// <returns>True if the object is selected</returns>
        bool SelectedFeature(out ObjectSelectionType featureType, out int featureId);

        /// <summary>
        /// Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format in relative coordinates. The XYZ are the local point coordinate and ijk is the normal of the surface.
        /// </summary>
        /// <param name="featureType">The type of geometry (FEATURE_SURFACE, FEATURE_POINT, ...). Set to FEATURE_SURFACE and if not point or curve was selected, the name of the geometry will be 'point on surface'</param>
        /// <param name="featureId">The internal ID to retrieve the right geometry from the object (use SelectedFeature)</param>
        /// <param name="pointList">The point or a list of points as XYZijk, coordinates are relative to the object (ijk is the normal to the surface)</param>
        /// <returns>The name of the selected geometry (if applicable)</returns>
        string GetPoints(ObjectSelectionType featureType, int featureId, out Mat pointList);

        /// <summary>
        /// Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
        /// Tip: Use getLink() and setLink() to get/set the robot tool, reference frame, robot and program linked to the project.
        /// Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.
        /// </summary>
        /// <param name="ncfile">path to the NC (G-code/APT/Point cloud) file to load (optional)</param>
        /// <param name="partObj"></param>
        /// <param name="options">Additional options (optional)</param>
        /// <returns>Program (null). Use Update() to retrieve the result</returns>
        IItem SetMachiningParameters(string ncfile = "", IItem partObj = null, string options = "");

        /// <summary>
        ///     Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
        /// </summary>
        void SetAsCartesianTarget();

        /// <summary>
        ///     Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian
        ///     coordinates.
        /// </summary>
        void SetAsJointTarget();

        /// <summary>
        ///     Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the
        ///     preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <returns>double x n -> joints matrix</returns>
        double[] Joints();

        /// <summary>
        /// Return the current joint position of a robot (only from the simulator, never from the real robot). This should be used only when RoboDK is connected to the real robot and only the simulated robot needs to be retrieved(for example, if we want to move the robot using a spacemouse).
        /// Note: Use robot.Joints() instead to retrieve the simulated and real robot position when connected.
        /// </summary>
        /// <returns>double x n -> joints array</returns>
        double[] SimulatorJoints();

        /// <summary>
        /// Returns the home joints of a robot.
        /// These joints can be manually set in the robot "Parameters" menu, then select "Set home position"
        /// <seealso cref="SetJointsHome"/>
        /// </summary>
        /// <returns>double x n -> joints array</returns>
        double[] JointsHome();

        /// <summary>
        /// Set the home position of the robot in the joint space.
        /// param joints: robot joints
        /// <seealso cref="JointsHome"/>
        /// </summary>
        /// <param name="joints">Home Position of all robot joints</param>
        void SetJointsHome(double[] joints);

        /// <summary>
        /// Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.
        /// </summary>
        /// <param name="linkId">link index(0 for the robot base, 1 for the first link, ...)</param>
        /// <returns></returns>
        IItem ObjectLink(int linkId = 0);

        /// <summary>
        /// Returns an item pointer (Item class) to a robot, object, tool or program. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
        /// </summary>
        /// <param name="typeLinked">type of linked object to retrieve</param>
        /// <returns></returns>
        IItem GetLink(ItemType typeLinked = ItemType.Robot);

        /// <summary>
        ///     Sets the current joints of a robot or the joints of a target. It the item is a cartesian target, it returns the
        ///     preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <param name="joints">array of joint values, in degrees or mm for linear axes</param>
        /// <param name="saturate_action">Behavior to saturate or ignore invalid joints (only applicable to robot items)</param>
        /// <returns>Returns True if the joints are valid (not saturated), False if they are outside the joint limitations.</returns>
        bool SetJoints(double[] joints, SetJointsType saturate_action=SetJointsType.Default);

        /// <summary>
        ///     Returns the joint limits of a robot
        /// </summary>
        /// <param name="lowerLlimits"></param>
        /// <param name="upperLimits"></param>
        void JointLimits(out double[] lowerLlimits, out double[] upperLimits);

        /// <summary>
        /// Sets the joint limits of a robot
        /// </summary>
        /// <param name="lower_limits"></param>
        /// <param name="upper_limits"></param>
        void SetJointLimits(double[] lowerLlimits, double[] upperLimits);

        /// <summary>
        ///     Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy
        ///     paste these objects.
        ///     If the robot is not provided, the first available robot will be chosen automatically.
        /// </summary>
        /// <param name="robot">Robot item</param>
        void SetRobot(IItem robot = null);

        /// <summary>
        ///     Obsolete: Use setPoseFrame instead.
        ///     Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ///     If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose
        ///     of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        void SetFrame(IItem frame);

        /// <summary>
        ///     Obsolete: Use setPoseFrame instead.
        ///     Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ///     If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose
        ///     of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        void SetFrame(Mat frame);

        /// <summary>
        ///     Obsolete: Use setPoseTool instead.
        ///     Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ///     If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of
        ///     the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        void SetTool(IItem tool);

        /// <summary>
        ///     Obsolete: Use setPoseTool instead.
        ///     Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ///     If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of
        ///     the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        void SetTool(Mat tool);

        /// <summary>
        ///     Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
        /// </summary>
        /// <param name="toolPose"></param>
        /// <param name="toolName"></param>
        /// <returns>new item created</returns>
        IItem AddTool(Mat toolPose, string toolName = "New TCP");

        /// <summary>
        ///     Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not
        ///     taken into account.
        /// </summary>
        /// <param name="joints"></param>
        /// <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
        Mat SolveFK(double[] joints);

        /// <summary>
        ///     Returns the robot configuration state for a set of robot joints.
        /// </summary>
        /// <param name="joints">array of joints</param>
        /// <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
        double[] JointsConfig(double[] joints);

        /// <summary>
        ///     Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the
        ///     current robot configuration (see SolveIK_All())
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
        /// <param name="jointsApprox">Aproximate solution. Leave empty to return the closest match to the current robot position.</param>
        /// <param name="tool">4x4 matrix -> Optionally provide a tool, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
        /// <param name="reference">4x4 matrix -> Optionally provide a reference, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
        /// <returns>array of joints</returns>
        double[] SolveIK(Mat pose, double[] jointsApprox = null, Mat tool = null, Mat reference = null);

        /// <summary>
        ///     Computes the inverse kinematics for the specified robot and pose. The function returns all available joint
        ///     solutions as a 2D matrix.
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
        /// <param name="tool">4x4 matrix -> Optionally provide a tool, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
        /// <param name="reference">4x4 matrix -> Optionally provide a reference, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
        /// <returns>double x n x m -> joint list (2D matrix)</returns>
        Mat SolveIK_All(Mat pose, Mat tool = null, Mat reference = null);

        /// <summary>
        ///     Connect to a real robot using the robot driver.
        /// </summary>
        /// <param name="robotIp">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
        /// <returns>status -> true if connected successfully, false if connection failed</returns>
        bool Connect(string robotIp = "");

		/// <summary>
		/// Connect to a real robot and wait for a connection to succeed.
		/// </summary>
		/// <param name="robotIp">Robot IP. Leave blank to use the robot's connection params.</param>
		/// <param name="maxAttempts">Maximum connection attemps before reporting an unsuccessful connection.</param>
		/// <param name="waitConnection">Time to wait in seconds between connection attempts.</param>
		/// <returns>True if connected successfully, else false.</returns>
		bool ConnectSafe(string robotIp = "", int maxAttempts = 5, int waitConnection = 4);

		/// <summary>
		/// Returns the robot connection parameters.
		/// </summary>
		/// <returns>Robot IP, Robot Port, FTP Path, FTP Username, FTP Password</returns>
		RobotConnectionParameter ConnectionParams();

		/// <summary>
		/// Set the robot connection parameters.
		/// </summary>
		/// <param name="robotIP">IP address of robot.</param>
		/// <param name="port">Port of robot.</param>
		/// <param name="remotePath">FTP path to connect to.</param>
		/// <param name="ftpUser">FTP username</param>
		/// <param name="ftpPass">FTP password</param>
		void setConnectionParams(string robotIP, int port, string remotePath, string ftpUser, string ftpPass);

		/// <summary>
		/// Check connection status with a real robot.
		/// </summary>
		/// <returns>Status contains connection status code enum, Message contains error info if status is not "Ready".</returns>
		RobotConnectionType ConnectedState();

		/// <summary>
		///     Disconnect from a real robot (when the robot driver is used)
		/// </summary>
		/// <returns>
		///     status -> true if disconnected successfully, false if it failed. It can fail if it was previously disconnected
		///     manually for example.
		/// </returns>
		bool Disconnect();

        /// <summary>
        /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveJ can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        void MoveJ(IItem itemtarget, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="joints">joints -> joint target to move to.</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveJ(double[] joints, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveJ(Mat target, bool blocking = true);

        /// <summary>
        /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveL can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        void MoveL(IItem itemtarget, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="joints">joints -> joint target to move to.</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveL(double[] joints, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveL(Mat target, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot
        ///     finishes its movements.
        /// </summary>
        /// <param name="itemtarget1">target -> intermediate target to move to as a target item (RoboDK target item)</param>
        /// <param name="itemtarget2">target -> final target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveC(IItem itemtarget1, IItem itemtarget2, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot
        ///     finishes its movements.
        /// </summary>
        /// <param name="joints1">joints -> intermediate joint target to move to.</param>
        /// <param name="joints2">joints -> final joint target to move to.</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveC(double[] joints1, double[] joints2, bool blocking = true);

        /// <summary>
        ///     Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot
        ///     finishes its movements.
        /// </summary>
        /// <param name="target1">pose -> intermediate pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="target2">pose -> final pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        void MoveC(Mat target1, Mat target2, bool blocking = true);

        /// <summary>
        ///     Checks if a joint movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> destination joints</param>
        /// <param name="minstepDeg">(optional): maximum joint step in degrees</param>
        /// <returns>
        ///     collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of
        ///     objects that collided if there was a collision.
        /// </returns>
        int MoveJ_Test(double[] j1, double[] j2, double minstepDeg = -1);

        /// <summary>
        /// Checks if a joint movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> joints via</param>
        /// <param name="j3">joints -> joints final destination</param>
        /// <param name="blendDeg">Blend in degrees</param>
        /// <param name="minstepDeg">(optional): maximum joint step in degrees</param>
        /// <returns>collision : returns false if the movement is possible and free of collision. Otherwise it returns true.</returns>
        bool MoveJ_Test_Blend(double[] j1, double[] j2, double[] j3, double blendDeg = 5, double minstepDeg = -1);

        /// <summary>
        ///     Checks if a linear movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="t2">Pose -> destination pose with respect to the active tool and coordinate system</param>
        /// <param name="minstepDeg">(optional): maximum joint step in degrees</param>
        /// <returns>
        ///     collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of
        ///     objects that collided if there was a collision.
        /// </returns>
        int MoveL_Test(double[] j1, Mat t2, double minstepDeg = -1);

        /// <summary>
        /// Sets the speed and/or the acceleration of a robot.
        /// </summary>
        /// <param name="speedLinear">linear speed in mm/s (-1 = no change)</param>
        /// <param name="speedJoints">joint speed in deg/s (-1 = no change)</param>
        /// <param name="accelLinear">linear acceleration in mm/s2 (-1 = no change)</param>
        /// <param name="accelJoints">joint acceleration in deg/s2 (-1 = no change)</param>
        void SetSpeed(double speedLinear, double accelLinear = -1, double speedJoints = -1,
            double accelJoints = -1);


        /// <summary>
        ///     Sets the robot movement smoothing accuracy (also known as zone data value).
        /// Obsolete, use SetRounding instead.
        /// </summary>
        /// <param name="zonedata">zonedata value (int) (robot dependent, set to -1 for fine movements)</param>
        [Obsolete]
        void SetZoneData(double zonedata);

        /// <summary>
        /// Sets the rounding accuracy to smooth the edges of corners.
        /// In general, it is recommended to allow a small approximation near the corners to maintain a constant speed.
        /// Setting a rounding values greater than 0 helps avoiding jerky movements caused by constant acceleration and decelerations.
        /// </summary>
        /// <param name="rounding"></param>
        void SetRounding(double rounding);

        /// <summary>
        ///     Displays a sequence of joints
        /// </summary>
        /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
        void ShowSequence(Mat sequence);

        /// <summary>
        ///     Displays a sequence of joints or poses
        /// </summary>
        /// <param name="joints">List of joint arrays</param>
        /// <param name="poses">List of poses</param>
        /// <param name="flags">Display options</param>
        /// <param name="timeout">Display timeout, in milliseconds (default: -1)</param>
        void ShowSequence(List<double[]> joints = null, List<Mat> poses = null, SequenceDisplayFlags flags = SequenceDisplayFlags.Default, int timeout = -1);

        /// <summary>
        ///     Checks if a robot or program is currently running (busy or moving)
        /// </summary>
        /// <returns>busy status (true=moving, false=stopped)</returns>
        bool Busy();

        /// <summary>
        ///     Stops a program or a robot
        /// </summary>
        /// <returns></returns>
        void Stop();

        /// <summary>
        ///     Waits (blocks) until the robot finishes its movement.
        /// </summary>
        /// <param name="timeoutSec">timeout -> Max time to wait for robot to finish its movement (in seconds)</param>
        void WaitMove(double timeoutSec = 300);

        /// <summary>
        ///     Saves a program to a file.
        /// </summary>
        /// <param name="filename">File path of the program</param>
        /// <param name="runMode">RUNMODE_MAKE_ROBOTPROG to generate the program file.Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.</param>
        /// <returns>Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)</returns>
        bool MakeProgram(string filename = "", RunMode runMode = RunMode.MakeRobotProgram);

        /// <summary>
        ///     Sets if the program will be run in simulation mode or on the real robot.
        ///     Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force
        ///     the program to run on the robot.
        /// </summary>
        /// <returns>number of instructions that can be executed</returns>
        void SetRunType(ProgramExecutionType programExecutionType);

        /// <summary>
        ///     Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is
        ///     performed before the program starts)
        ///     This is a non-blocking call. Use IsBusy() to check if the program execution finished.
        ///     Notes:
        ///     if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        ///     if setRunMode(RUNMODE_RUN_ROBOT) is used -> the program will run on the robot (default when RUNMODE_RUN_ROBOT is
        ///     used)
        ///     if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will
        ///     run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the
        ///     RoboDK GUI
        /// </summary>
        /// <returns>number of instructions that can be executed</returns>
        int RunProgram();

        /// <summary>
        ///     Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is
        ///     performed before the program starts)
        ///     Program parameters can be provided for Python calls.
        ///     This is a non-blocking call.Use IsBusy() to check if the program execution finished.
        ///     Notes: if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        ///     if setRunMode(RUNMODE_RUN_ROBOT) is used ->the program will run on the robot(default when RUNMODE_RUN_ROBOT is
        ///     used)
        ///     if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will
        ///     run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the
        ///     RoboDK GUI
        /// </summary>
        /// <param name="parameters">Number of instructions that can be executed</param>
        int RunCode(string parameters = null);

        /// <summary>
        /// Adds a program call, code, message or comment to the program. Returns True if succeeded.
        /// </summary>
        /// <param name="code">string of the code or program to run </param>
        /// <param name="runType">specify if the code is a program</param>
        /// <returns>True if success; False othwersise</returns>
        bool RunInstruction(string code, ProgramRunType runType = ProgramRunType.CallProgram);
		
		/// <summary>
        /// Adds a program call, code, message or comment to the program. Returns True if succeeded.
        /// </summary>
        /// <param name="code">string of the code or program to run </param>
        /// <param name="runType">specify if the code is a program</param>
        /// <returns>True if success; False othwersise</returns>
        bool RunCodeCustom(string code, ProgramRunType runType = ProgramRunType.CallProgram);
		
        /// <summary>
        ///     Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the
        ///     robot to stop and let the user resume the program anytime.
        /// </summary>
        /// <param name="timeMs">Time in milliseconds</param>
        void Pause(double timeMs = -1);

        /// <summary>
        ///     Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
        /// </summary>
        /// <param name="ioVar">io_var -> digital output (string or number)</param>
        /// <param name="ioValue">io_value -> value (string or number)</param>
        void setDO(string ioVar, string ioValue);

        /// <summary>
        ///     Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
        /// </summary>
        /// <param name="ioVar">io_var -> digital output (string or number)</param>
        /// <param name="ioValue">io_value -> value (string or number)</param>
        /// <param name="timeoutMs">int (optional) -> timeout in miliseconds</param>
        void waitDI(string ioVar, string ioValue, double timeoutMs = -1);

        /// <summary>
        ///     Add a custom instruction. This instruction will execute a Python file or an executable file.
        /// </summary>
        /// <param name="name"></param>
        /// <param name="pathRun">path to run(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="pathIcon">icon path(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="blocking">True if blocking, 0 if it is a non blocking executable trigger</param>
        /// <param name="cmdRunOnRobot">Command to run through the driver when connected to the robot</param>
        /// :param name: digital input (string or number)
        void AddCustomInstruction(string name, string pathRun, string pathIcon = "", bool blocking = true,
            string cmdRunOnRobot = "");

        /// <summary>
        ///     Adds a new robot move joint instruction to a program. Obsolete. Use MoveJ instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        void AddMoveJ(IItem itemtarget);

        /// <summary>
        ///     Adds a new robot move linear instruction to a program. Obsolete. Use MoveL instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        void AddMoveL(IItem itemtarget);

        /// <summary>
        /// Show or hide instruction items of a program in the RoboDK tree
        /// </summary>
        /// <param name="show"></param>
        void ShowInstructions(bool show = true);

        /// <summary>
        /// Show or hide targets of a program in the RoboDK tree
        /// </summary>
        /// <param name="show"></param>
        void ShowTargets(bool show = true);

        /// <summary>
        ///     Returns the number of instructions of a program.
        /// </summary>
        /// <returns></returns>
        int InstructionCount();

        /// <summary>
        ///     Returns the program instruction at position id
        /// </summary>
        /// <param name="instructionId"></param>
        /// <returns>program instruction at position instructionId</returns>
        ProgramInstruction GetInstruction(int instructionId);

        /// <summary>
        ///     Sets the program instruction at position id
        /// </summary>
        /// <param name="instructionId"></param>
        /// <param name="instruction"></param>
        void SetInstruction(int instructionId, ProgramInstruction instruction);

        UpdateResult Update();

        /// <summary>
        /// Updates a program and returns the estimated time and the number of valid instructions.
        /// An update can also be applied to a robot machining project. The update is performed on the generated program.
        /// </summary>
        /// <param name="collisionCheck">check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)</param>
        /// <param name="timeoutSec">Maximum time to wait for the update to complete (in seconds)</param>
        /// <param name="linStepMm">Maximum step in millimeters for linear movements (millimeters). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <param name="jointStepDeg">Maximum step for joint movements (degrees). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <returns>1.0 if there are no problems with the path or less than 1.0 if there is a problem in the path (ratio of problem)</returns>
        UpdateResult Update(
            CollisionCheckOptions collisionCheck, /* = CollisionCheckOptions.CollisionCheckOff, */
            int timeoutSec = 3600,
            double linStepMm = -1,
            double jointStepDeg = -1);

        /// <summary>
        ///     Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1
        ///     plus the number of robot axes.
        /// </summary>
        /// <param name="instructions">the matrix of instructions</param>
        /// <returns>Returns 0 if success</returns>
        int InstructionList(out Mat instructions);

        /// <summary>
        /// Returns a list of joints. 
        /// Linear moves are rounded according to the smoothing parameter set inside the program.
        /// </summary>
        /// <param name="mmStep">Maximum step in millimeters for linear movements (millimeters)</param>
        /// <param name="degStep">Maximum step for joint movements (degrees)</param>
        /// <param name="saveToFile">Provide a file name to directly save the output to a file. If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.</param>
        /// <param name="collisionCheck">Check for collisions: will set to 1 or 0</param>
        /// <param name="flags">Reserved for future compatibility</param>
        /// <param name="timeoutSec">Maximum time to wait for the result (in seconds)</param>
        /// <param name="time_step">Time step in seconds for time-based calculation (ListJointsType must be set to TimeBased)</param>
        /// <returns>List of InstructionListJointsResult.</returns>
        InstructionListJointsResult GetInstructionListJoints(
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            ListJointsType flags = 0,
            int timeoutSec = 3600,
            double time_step = 0.2);

        /// <summary>
        /// Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.
        /// </summary>
        /// <param name="errorMsg">Returns a human readable error message (if any)</param>
        /// <param name="jointList">Returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] if a file name is not specified</param>
        /// <param name="mmStep">Maximum step in millimeters for linear movements (millimeters)</param>
        /// <param name="degStep">Maximum step for joint movements (degrees)</param>
        /// <param name="saveToFile">Provide a file name to directly save the output to a file. If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.</param>
        /// <param name="collisionCheck">Check for collisions: will set to 1 or 0</param>
        /// <param name="flags">Reserved for future compatibility</param>
        /// <param name="timeoutSec">Maximum time to wait for the result (in seconds)</param>
        /// <param name="time_step">Time step for time-based calculation (ListJointsType must be set to TimeBased)</param>
        /// <returns>Returns 0 if success, otherwise, it will return negative values</returns>
        int InstructionListJoints(out string errorMsg,
            out Mat jointList,
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            ListJointsType flags = 0,
            int timeoutSec = 3600,
            double time_step = 0.2);

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        void Finish();

        /// <summary>
        ///     Sets the accuracy of the robot active or inactive.
        ///     A robot must have been calibrated to properly use this option.
        /// </summary>
        /// <param name="accurate">Set true to use the accurate model or false to use the nominal model</param>
        void SetAccuracyActive(bool accurate = true);

        /// <summary>
        /// Request accurate kinematics status
        /// </summary>
        /// <returns>Returns true if the accurate kinematics are being used</returns>
        bool AccuracyActive();

        /// <summary>
        /// Adds an object attached to this object
        /// </summary>
        /// <param name="filename">
        ///     Any file to load, supported by RoboDK. 
        ///     Supported formats include STL, STEP, IGES, ROBOT, TOOL, RDK,... 
        ///     It is also possible to load supported robot programs, such as SRC (KUKA), 
        ///     SCRIPT (Universal Robots), LS (Fanuc), JBI (Motoman), MOD (ABB), PRG (ABB), ...
        /// </param>
        /// <returns>Returns loaded object</returns>
        IItem AddFile(string filename);

        /// <summary>
        /// Makes a copy of the source item geometry adding it at a given position (pose), relative to this item
        /// </summary>
        /// <param name="source">Source item</param>
        /// <param name="pose">Relative position</param>
        void AddGeometry(IItem source, Mat pose);

        /// <summary>
        /// Adds a list of points to the object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="points">list of points as a matrix (3xN matrix, or 6xN to provide point normals as ijk vectors)</param>
        /// <param name="addToRef">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
        /// <param name="projectionType">Type of projection.Use the PROJECTION_* flags.</param>
        /// <returns>added object/shape (0 if failed)</returns>
        IItem AddPoints(Mat points, bool addToRef = false, ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        /// Check if if this item is in a collision state with another item
        /// </summary>
        /// <param name="item">Item to check for collisions</param>
        /// <returns>Returns true if this item collides with another item; false otherwise.</returns>
        bool Collision(IItem item);

        /// <summary>
        ///     Copy the item to the clipboard (same as Ctrl+C).
        ///     Use together with Paste() to duplicate items.
        /// </summary>        
        /// <param name="copy_children">Set to false to prevent copying all items attached to this item</param>
        void Copy(bool copy_children = true);

        /// <summary>
        ///     Filter a program file to improve accuracy for a specific robot.
        ///     The robot must have been previously calibrated.
        /// </summary>
        /// <param name="filename">File path of the program. Formats supported include: JBI (Motoman), SRC (KUKA), MOD (ABB), PRG (ABB), LS (FANUC)</param>
        /// <param name="filterMessage">The summary of the filtering</param>
        /// <returns>Returns true if the filter succeeded, or false if there are filtering problems.</returns>
        bool FilterProgram(string filename, out string filterMessage);

        /// <summary>
        ///     Get an Analog Input (AI).
        ///     This function is only useful when connected to a real robot using the robot driver.
        /// </summary>
        /// <param name="input">Analog Input (string or number)</param>
        /// <returns>
        ///     Returns a string related to the state of the Analog Input (0-1 or other range depending on the robot driver).
        ///     This function returns an empty string if the script is not executed on the robot.
        /// </returns>
        string GetAnalogInput(string input);

        /// <summary>
        ///     Get a Digital Input (DI).
        ///     This function is only useful when connected to a real robot using the robot driver.
        /// </summary>
        /// <param name="input">Digital Input (string or number)</param>
        /// <returns>
        ///     Returns a string related to the state of the Digital Input (0/1 or other value depending on the robot driver).
        ///     This function returns an empty string if the script is not executed on the robot.
        /// </returns>
        string GetDigitalInput(string input);

        /// <summary>
        /// Set an Analog Output (AO).
        /// </summary>
        /// <param name="output">Analog Output (string or number)</param>
        /// <param name="value">Desired value</param>
        void SetAnalogOutput(string output, string value);

        /// <summary>
        ///     Set a Digital Output (DO).
        ///     This command can also be used to set any generic variables to a desired value.
        /// </summary>
        /// <param name="output">Digital Output (string or number)</param>
        /// <param name="value">Desired value</param>
        void SetDigitalOutput(string output, string value);

        /// <summary>
        ///     Waits for an input to attain a given value.
        ///     Optionally, a timeout can be provided.
        /// </summary>
        /// <param name="input">Digital Input (string or number)</param>
        /// <param name="value">Expected value</param>
        /// <param name="timeout">Timeout in miliseconds</param>
        void WaitDigitalInput(string input, string value, double timeout = -1);

        /// <summary>
        /// Delete an instruction of a program
        /// </summary>
        /// <param name="instructionId">Instruction ID</param>
        /// <returns>Returns true if success.</returns>
        bool InstructionDelete(int instructionId = 0);

        /// <summary>
        ///     Select an instruction in the program as a reference to add new instructions.
        ///     New instructions will be added after the selected instruction.
        /// </summary>
        /// <param name="instructionId">Instruction ID</param>
        /// <returns>
        ///     If no Instruction ID is specified, the active instruction will be selected and returned (if the program is running), otherwise it returns -1.
        /// </returns>
        int InstructionSelect(int instructionId = -1);

        /// <summary>
        /// Check if the object is inside the provided object.
        /// </summary>
        /// <param name="objectParent"></param>
        /// <returns>Returns true if the object is inside the objectParent.</returns>
        bool IsInside(IItem objectParent);

        /// <summary>
        ///     Check if the target is a joint target.
        ///     A joint target moves to the joint position without taking into account the cartesian coordinates.
        /// </summary>
        /// <returns>Returns true if the target is a joint target.</returns>        
        bool IsJointTarget();

        /// <summary>
        /// Get the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).
        /// </summary>
        /// <returns>Returns ProgramExecutionType (Simulator or Robot).</returns>
        ProgramExecutionType GetRunType();

        /// <summary>
        /// Sets the linear acceleration of a robot in mm/s2
        /// </summary>
        /// <param name="value">Acceleration in mm/s2</param>
        void SetAcceleration(double value);

        /// <summary>
        /// Sets the joint acceleration of a robot
        /// </summary>
        /// <param name="value">Acceleration in deg/s2 for rotary joints and mm/s2 for linear joints</param>
        void SetAccelerationJoints(double value);

        /// <summary>
        /// Sets the joint speed of a robot
        /// </summary>
        /// <param name="value">Speed in deg/s for rotary joints and mm/s for linear joints</param>
        void SetSpeedJoints(double value);

        /// <summary>
        ///     Sets a link between this item and the specified item.
        ///     This is useful to set the relationship between programs, robots, tools and other specific projects.
        /// </summary>
        /// <param name="item">Item to link</param>
        void SetLink(IItem item);

        #endregion
    }
}