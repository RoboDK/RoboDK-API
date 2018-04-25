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
using System.Windows.Media;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    /// <summary>
    ///     The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target,
    ///     ... any item visible in the station tree.
    ///     An item can also be seen as a node where other items can be attached to (child items).
    ///     Every item has one parent item/node and can have one or more child items/nodes
    ///     RoboLinkItem is a "friend" class of RoboLink.
    /// </summary>
    public class Item
    {
        #region Fields

        private long _item;
        private readonly ItemType _type;
        private string _name;

        #endregion

        #region Constructors

        public Item(RoboDK connectionLink, long itemPtr = 0, ItemType itemType = ItemType.Any)
        {
            _item = itemPtr;
            Link = connectionLink;
            _type = itemType;
        }

        #endregion

        #region Properties

        public RoboDK Link { get; private set; }

        #endregion

        #region Public Methods

        public long get_item()
        {
            return _item;
        }

        public string ToString2()
        {
            if (Valid())
            {
                return $"RoboDK item {_item} of type {_type}";
            }

            return "RoboDK item (INVALID)";
        }

        /// <summary>
        /// Update item flags. 
        /// Item flags allow defining how much access the user has to item-specific features. 
        /// </summary>
        /// <param name="itemFlags">Item Flags to be set</param>
        public void SetItemFlags(ItemFlags itemFlags = ItemFlags.All)
        {
            int flags = (int) itemFlags;
            Link.check_connection();
            string command = "S_Item_Rights";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int(flags);
            Link.check_status();
        }

        /// <summary>
        /// Retrieve current item flags. 
        /// Item flags allow defining how much access the user has to item-specific features. 
        /// </summary>
        /// <returns>Current Item Flags</returns>
        public ItemFlags GetItemFlags()
        {
            Link.check_connection();
            string command = "S_Item_Rights";
            Link.send_line(command);
            Link.send_item(this);
            int flags = Link.rec_int();
            ItemFlags itemFlags = (ItemFlags) flags;
            Link.check_status();
            return itemFlags;
        }

        /// <summary>
        ///     Returns an integer that represents the type of the item (robot, object, tool, frame, ...)
        ///     Compare the returned value to ITEM_CASE_* variables
        /// </summary>
        /// <param name="item_other"></param>
        /// <returns></returns>
        public bool Equals(Item item_other)
        {
            return _item == item_other._item;
        }

        /// <summary>
        ///     Use RDK() instead. Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        public RoboDK RL()
        {
            return Link;
        }

        /// <summary>
        ///     Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        public RoboDK RDK()
        {
            return Link;
        }

        /// <summary>
        ///     Create a new communication link. Use this for robots if you use a multithread application running multiple robots
        ///     at the same time.
        /// </summary>
        public void NewLink()
        {
            Link = new RoboDK();
            Link.Connect();
        }

        //////// GENERIC ITEM CALLS

        /// <summary>
        /// Returns the type of an item (robot, object, target, reference frame, ...)
        /// </summary>
        /// <returns></returns>
        public ItemType GetItemType()
        {
            /*Link.check_connection();
            var command = "G_Item_Type";
            Link.send_line(command);
            Link.send_item(this);
            var type = Link.rec_int();
            ItemType itemType = (ItemType) type;
            Link.check_status();
            return itemType;*/
            return _type;
        }

        ////// add more methods

        /// <summary>
        ///     Save a station or object to a file
        /// </summary>
        /// <param name="filename"></param>
        public void Save(string filename)
        {
            Link.Save(filename, this);
        }

        /// <summary>
        ///     Deletes an item and its childs from the station.
        /// </summary>
        public void Delete()
        {
            Link.check_connection();
            var command = "Remove";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
            _item = 0;
        }

        /// <summary>
        ///     Checks if the item is valid. An invalid item will be returned by an unsuccessful function call.
        /// </summary>
        /// <returns>true if valid, false if invalid</returns>
        public bool Valid()
        {
            if (_item == 0)
            {
                return false;
            }

            return true;
        }

        /// <summary>
        /// Attaches the item to a new parent while maintaining the relative position with its parent. The absolute position is changed.
        /// </summary>
        /// <param name="parent"></param>
        public void SetParent(Item parent)
        {
            Link.check_connection();
            Link.send_line("S_Parent");
            Link.send_item(this);
            Link.send_item(parent);
            Link.check_status();
        }

        ////// add more methods
        /// <summary>
        ///     Returns a list of the item childs that are attached to the provided item.
        /// </summary>
        /// <returns>item x n -> list of child items</returns>
        public Item[] Childs()
        {
            Link.check_connection();
            var command = "G_Childs";
            Link.send_line(command);
            Link.send_item(this);
            var nitems = Link.rec_int();
            var itemlist = new Item[nitems];
            for (var i = 0; i < nitems; i++)
            {
                itemlist[i] = Link.rec_item();
            }

            Link.check_status();
            return itemlist;
        }

        /// <summary>
        ///     Returns the parent item of this item.
        /// </summary>
        public Item Parent()
        {
            Link.check_connection();
            var command = "G_Parent";
            Link.send_line(command);
            Link.send_item(this);
            var parent = Link.rec_item();
            Link.check_status();
            return parent;
        }

        /// <summary>
        ///     Returns 1 if the item is visible, otherwise, returns 0.
        /// </summary>
        /// <returns>true if visible, false if not visible</returns>
        public bool Visible()
        {
            Link.check_connection();
            var command = "G_Visible";
            Link.send_line(command);
            Link.send_item(this);
            var visible = Link.rec_int();
            Link.check_status();
            return visible != 0;
        }

        /// <summary>
        ///     Sets the item visiblity status
        /// </summary>
        /// <param name="visible"></param>
        /// <param name="visible_frame">srt the visible reference frame (1) or not visible (0)</param>
        public void setVisible(bool visible, int visible_frame = -1)
        {
            if (visible_frame < 0)
            {
                visible_frame = visible ? 1 : 0;
            }

            Link.check_connection();
            var command = "S_Visible";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int(visible ? 1 : 0);
            Link.send_int(visible_frame);
            Link.check_status();
        }

        /// <summary>
        ///     Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
        /// </summary>
        /// <returns>name of the item</returns>
        public string Name()
        {
            Link.check_connection();
            var command = "G_Name";
            Link.send_line(command);
            Link.send_item(this);
            _name = Link.rec_line();
            Link.check_status();
            return _name;
        }

        /// <summary>
        ///     Set the name of a RoboDK item.
        /// </summary>
        /// <param name="name"></param>
        public void SetName(string name)
        {
            Link.check_connection();
            var command = "S_Name";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(name);
            Link.check_status();
        }

        // add more methods

        /// <summary>
        ///     Sets the local position (pose) of an object, target or reference frame. For example, the position of an
        ///     object/frame/target with respect to its parent.
        ///     If a robot is provided, it will set the pose of the end efector.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        public void setPose(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hlocal";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <summary>
        ///     Returns the local position (pose) of an object, target or reference frame. For example, the position of an
        ///     object/frame/target with respect to its parent.
        ///     If a robot is provided, it will get the pose of the end efector
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat Pose()
        {
            Link.check_connection();
            var command = "G_Hlocal";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for
        ///     tools and objects.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        public void setGeometryPose(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hgeom";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <summary>
        ///     Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for
        ///     tools and objects.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat GeometryPose()
        {
            Link.check_connection();
            var command = "G_Hgeom";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Obsolete: Use setPoseTool(pose) instead. Sets the tool pose of a tool item. If a robot is provided it will set the
        ///     tool pose of the active tool held by the robot.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setHtool(Mat pose)
        {
            Link.check_connection();
            var command = "S_Htool";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <summary>
        ///     Obsolete: Use PoseTool() instead.
        ///     Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the
        ///     robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat Htool()
        {
            Link.check_connection();
            var command = "G_Htool";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the
        ///     robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseTool()
        {
            Link.check_connection();
            var command = "G_Tool";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active
        ///     reference frame used by the robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseFrame()
        {
            Link.check_connection();
            var command = "G_Frame";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Sets the reference frame of a robot(user frame). The frame can be either an item or a pose.
        ///     If "frame" is an item, it links the robot to the frame item. If frame is a pose, it updates the linked pose of the
        ///     robot frame (with respect to the robot reference frame).
        /// </summary>
        /// <param name="frame_pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseFrame(Mat frame_pose)
        {
            Link.check_connection();
            var command = "S_Frame";
            Link.send_line(command);
            Link.send_pose(frame_pose);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4
        ///     Matrix.
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseFrame(Item frame_item)
        {
            Link.check_connection();
            var command = "S_Frame_ptr";
            Link.send_line(command);
            Link.send_item(frame_item);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4
        ///     Matrix.
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="tool_pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseTool(Mat tool_pose)
        {
            Link.check_connection();
            var command = "S_Tool";
            Link.send_line(command);
            Link.send_pose(tool_pose);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4
        ///     Matrix.
        ///     If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="tool_item">Tool item</param>
        public void setPoseTool(Item tool_item)
        {
            Link.check_connection();
            var command = "S_Tool_ptr";
            Link.send_line(command);
            Link.send_item(tool_item);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the
        ///     station origin.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseAbs(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hlocal_Abs";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <summary>
        ///     Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to
        ///     the station origin.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseAbs()
        {
            Link.check_connection();
            var command = "G_Hlocal_Abs";
            Link.send_line(command);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values
        ///     range from 0 to 1.
        ///     Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        /// </summary>
        /// <param name="tocolor">color to change to</param>
        /// <param name="fromcolor">filter by this color</param>
        /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        [Obsolete("Deprecated, please use new Recolor mehod which uses the new RoboDK Color class.")]
        public void Recolor(double[] tocolor, double[] fromcolor = null, double tolerance = 0.1)
        {
            Link.check_connection();
            if (fromcolor == null)
            {
                fromcolor = new double[] { 0, 0, 0, 0 };
                tolerance = 2;
            }

            Link.check_color(tocolor);
            Link.check_color(fromcolor);
            var command = "Recolor";
            Link.send_line(command);
            Link.send_item(this);
            var combined = new double[9];
            combined[0] = tolerance;
            Array.Copy(fromcolor, 0, combined, 1, 4);
            Array.Copy(tocolor, 0, combined, 5, 4);
            Link.send_array(combined);
            Link.check_status();
        }

        /// <summary>
        ///     Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values
        ///     range from 0 to 1.
        ///     Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        /// </summary>
        /// <param name="tocolor">color to change to</param>
        /// <param name="fromcolor">filter by this color</param>
        /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        public void Recolor(Color tocolor, Color? fromcolor = null, double tolerance = 0.1)
        {
            double[] tocolorArray = tocolor.ToRoboDKColorArray();
            Link.check_connection();
            if (fromcolor.HasValue == false)
            {
                fromcolor = new Color() {A=0, R=0, G=0, B=0};
                tolerance = 2;
            }
            double[] fromcolorArray = fromcolor.Value.ToRoboDKColorArray();

            Link.check_color(tocolorArray);
            Link.check_color(fromcolorArray);
            var command = "Recolor";
            Link.send_line(command);
            Link.send_item(this);
            var combined = new double[9];
            combined[0] = tolerance;
            Array.Copy(fromcolorArray, 0, combined, 1, 4);
            Array.Copy(tocolorArray, 0, combined, 5, 4);
            Link.send_array(combined);
            Link.check_status();
        }

        /// <summary>
        /// Set the color of an object, tool or robot. 
        /// A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <param name="tocolor">color to set</param>
        /// <seealso cref="GetColor"/>
        /// <seealso cref="Recolor(Color, Color?, double)"/>
        public void SetColor(Color tocolor)
        {
            Link.check_connection();
            double[] tocolorArray = tocolor.ToRoboDKColorArray();
            Link.check_color(tocolorArray);
            Link.send_line("S_Color");
            Link.send_item(this);
            Link.send_array(tocolorArray);
            Link.check_status();
        }

        /// <summary>
        /// Return the color of an Item (object, tool or robot). If the item has multiple colors it returns the first color available). 
        /// A color is in the format COLOR = [R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <returns>Color [R, G, B, A]</returns>
        /// <seealso cref="SetColor(Color)"/>
        /// <seealso cref="Recolor(Color, Color?, double)"/>
        public Color GetColor()
        {
            Link.check_connection();
            Link.send_line("G_Color");
            Link.send_item(this);
            var colorArray = Link.rec_array();
            Link.check_status();
            Color c = colorArray.FromRoboDKColorArray();
            return c;
        }

        /// <summary>
        /// Apply a scale to an object to make it bigger or smaller.
        /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
        /// </summary>
        /// <param name="scale">scale to apply as [scale_x, scale_y, scale_z]</param>
        public void Scale(double[] scale)
        {
            Link.check_connection();
            if (scale.Length != 3)
            {
                throw new RdkException("scale must be a single value or a 3-vector value");
            }

            var command = "Scale";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_array(scale);
            Link.check_status();
        }

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
        public Item AddCurve(Mat curvePoints, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            return Link.AddCurve(curvePoints, this, addToRef, projectionType);
        }

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
        public Mat ProjectPoints(Mat points, ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            return Link.ProjectPoints(points, this, projectionType);
        }

        /// <summary>
        /// Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
        /// Tip: Use getLink() and setLink() to get/set the robot tool, reference frame, robot and program linked to the project.
        /// Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.
        /// </summary>
        /// <param name="ncfile">path to the NC (G-code/APT/Point cloud) file to load (optional)</param>
        /// <param name="part_obj">object holding curves or points to automatically set up a curve/point follow project (optional)</param>
        /// <param name="options">Additional options (optional)</param>
        /// <returns>Program (null). Use Update() to retrieve the result</returns>
        public Item setMachiningParameters(string ncfile = "", Item part_obj = null, string options = "")
        {
            Link.check_connection();
            Link.send_line("S_MachiningParams");
            Link.send_item(this);
            Link.send_line(ncfile);
            Link.send_item(part_obj);
            Link.send_line("NO_UPDATE " + options);
            Link.ReceiveTimeout = 3600 * 1000;
            Item program = Link.rec_item();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            double status = Link.rec_int() / 1000.0;
            Link.check_status();
            return program;
        }

        //"""Target item calls"""

        /// <summary>
        ///     Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
        /// </summary>
        public void setAsCartesianTarget()
        {
            Link.check_connection();
            var command = "S_Target_As_RT";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian
        ///     coordinates.
        /// </summary>
        public void setAsJointTarget()
        {
            Link.check_connection();
            var command = "S_Target_As_JT";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        //#####Robot item calls####

        /// <summary>
        ///     Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the
        ///     preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <returns>double x n -> joints matrix</returns>
        public double[] Joints()
        {
            Link.check_connection();
            var command = "G_Thetas";
            Link.send_line(command);
            Link.send_item(this);
            var joints = Link.rec_array();
            Link.check_status();
            return joints;
        }

        // add more methods

        /// <summary>
        ///     Returns the home joints of a robot. These joints can be manually set in the robot "Parameters" menu, then select
        ///     "Set home position"
        /// </summary>
        /// <returns>double x n -> joints array</returns>
        public double[] JointsHome()
        {
            Link.check_connection();
            var command = "G_Home";
            Link.send_line(command);
            Link.send_item(this);
            var joints = Link.rec_array();
            Link.check_status();
            return joints;
        }

        /// <summary>
        /// Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.
        /// </summary>
        /// <param name="linkId">link index(0 for the robot base, 1 for the first link, ...)</param>
        /// <returns></returns>
        public Item ObjectLink(int linkId = 0)
        {
            Link.check_connection();
            Link.send_line("G_LinkObjId");
            Link.send_item(this);
            Link.send_int(linkId);
            Item item = Link.rec_item();
            Link.check_status();
            return item;
        }

        /// <summary>
        /// Returns an item pointer (Item class) to a robot, object, tool or program. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
        /// </summary>
        /// <param name="typeLinked">type of linked object to retrieve</param>
        /// <returns></returns>
        public Item GetLink(ItemType typeLinked = ItemType.Robot)
        {
            Link.check_connection();
            Link.send_line("G_LinkType");
            Link.send_item(this);
            Link.send_int((int) typeLinked);
            Item item = Link.rec_item();
            Link.check_status();
            return item;
        }

        /// <summary>
        ///     Sets the current joints of a robot or the joints of a target. It the item is a cartesian target, it returns the
        ///     preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <param name="joints"></param>
        public void setJoints(double[] joints)
        {
            Link.check_connection();
            var command = "S_Thetas";
            Link.send_line(command);
            Link.send_array(joints);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Returns the joint limits of a robot
        /// </summary>
        /// <param name="lower_limits"></param>
        /// <param name="upper_limits"></param>
        public void JointLimits(double[] lower_limits, double[] upper_limits)
        {
            Link.check_connection();
            var command = "G_RobLimits";
            Link.send_line(command);
            Link.send_item(this);
            lower_limits = Link.rec_array();
            upper_limits = Link.rec_array();
            var joints_type = Link.rec_int() / 1000.0;
            Link.check_status();
        }

        /// <summary>
        ///     Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy
        ///     paste these objects.
        ///     If the robot is not provided, the first available robot will be chosen automatically.
        /// </summary>
        /// <param name="robot">Robot item</param>
        public void setRobot(Item robot = null)
        {
            Link.check_connection();
            var command = "S_Robot";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_item(robot);
            Link.check_status();
        }

        /// <summary>
        ///     Obsolete: Use setPoseFrame instead.
        ///     Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ///     If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose
        ///     of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        public void setFrame(Item frame)
        {
            setPoseFrame(frame);
        }

        /// <summary>
        ///     Obsolete: Use setPoseFrame instead.
        ///     Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ///     If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose
        ///     of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        public void setFrame(Mat frame)
        {
            setPoseFrame(frame);
        }

        /// <summary>
        ///     Obsolete: Use setPoseTool instead.
        ///     Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ///     If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of
        ///     the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        public void setTool(Item tool)
        {
            setPoseTool(tool);
        }

        /// <summary>
        ///     Obsolete: Use setPoseTool instead.
        ///     Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ///     If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of
        ///     the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        public void setTool(Mat tool)
        {
            setPoseTool(tool);
        }

        /// <summary>
        ///     Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
        /// </summary>
        /// <param name="tool_pose">pose -> TCP as a 4x4 Matrix (pose of the tool frame)</param>
        /// <param name="tool_name">New tool name</param>
        /// <returns>new item created</returns>
        public Item AddTool(Mat tool_pose, string tool_name = "New TCP")
        {
            Link.check_connection();
            var command = "AddToolEmpty";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(tool_pose);
            Link.send_line(tool_name);
            var newtool = Link.rec_item();
            Link.check_status();
            return newtool;
        }

        /// <summary>
        ///     Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not
        ///     taken into account.
        /// </summary>
        /// <param name="joints"></param>
        /// <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
        public Mat SolveFK(double[] joints)
        {
            Link.check_connection();
            var command = "G_FK";
            Link.send_line(command);
            Link.send_array(joints);
            Link.send_item(this);
            var pose = Link.rec_pose();
            Link.check_status();
            return pose;
        }

        /// <summary>
        ///     Returns the robot configuration state for a set of robot joints.
        /// </summary>
        /// <param name="joints">array of joints</param>
        /// <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
        public double[] JointsConfig(double[] joints)
        {
            Link.check_connection();
            var command = "G_Thetas_Config";
            Link.send_line(command);
            Link.send_array(joints);
            Link.send_item(this);
            var config = Link.rec_array();
            Link.check_status();
            return config;
        }

        /// <summary>
        ///     Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the
        ///     current robot configuration (see SolveIK_All())
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
        /// <returns>array of joints</returns>
        public double[] SolveIK(Mat pose)
        {
            Link.check_connection();
            var command = "G_IK";
            Link.send_line(command);
            Link.send_pose(pose);
            Link.send_item(this);
            var joints = Link.rec_array();
            Link.check_status();
            return joints;
        }

        /// <summary>
        ///     Computes the inverse kinematics for the specified robot and pose. The function returns all available joint
        ///     solutions as a 2D matrix.
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
        /// <returns>double x n x m -> joint list (2D matrix)</returns>
        public Mat SolveIK_All(Mat pose)
        {
            Link.check_connection();
            var command = "G_IK_cmpl";
            Link.send_line(command);
            Link.send_pose(pose);
            Link.send_item(this);
            var joints_list = Link.rec_matrix();
            Link.check_status();
            return joints_list;
        }

        /// <summary>
        ///     Connect to a real robot using the robot driver.
        /// </summary>
        /// <param name="robot_ip">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
        /// <returns>status -> true if connected successfully, false if connection failed</returns>
        public bool Connect(string robot_ip = "")
        {
            Link.check_connection();
            var command = "Connect";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(robot_ip);
            var status = Link.rec_int();
            Link.check_status();
            return status != 0;
        }

        /// <summary>
        ///     Disconnect from a real robot (when the robot driver is used)
        /// </summary>
        /// <returns>
        ///     status -> true if disconnected successfully, false if it failed. It can fail if it was previously disconnected
        ///     manually for example.
        /// </returns>
        public bool Disconnect()
        {
            Link.check_connection();
            var command = "Disconnect";
            Link.send_line(command);
            Link.send_item(this);
            var status = Link.rec_int();
            Link.check_status();
            return status != 0;
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveJ can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveJ(Item itemtarget, bool blocking = true)
        {
            if (itemtarget.GetItemType() == ItemType.Program)
            {
                addMoveJ(itemtarget);
            }
            else
            {
                Link.moveX(itemtarget, null, null, this, 1, blocking);
            }
        }

        /// <summary>
        ///     Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="joints">joints -> joint target to move to.</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        public void MoveJ(double[] joints, bool blocking = true)
        {
            Link.moveX(null, joints, null, this, 1, blocking);
        }

        /// <summary>
        ///     Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        public void MoveJ(Mat target, bool blocking = true)
        {
            Link.moveX(null, null, target, this, 1, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveL can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveL(Item itemtarget, bool blocking = true)
        {
            if (itemtarget.GetItemType() == ItemType.Program)
            {
                addMoveL(itemtarget);
            }
            else
            {
                Link.moveX(itemtarget, null, null, this, 2, blocking);
            }
        }

        /// <summary>
        ///     Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="joints">joints -> joint target to move to.</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        public void MoveL(double[] joints, bool blocking = true)
        {
            Link.moveX(null, joints, null, this, 2, blocking);
        }

        /// <summary>
        ///     Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes
        ///     its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">
        ///     blocking -> True if we want the instruction to block until the robot finished the movement
        ///     (default=true)
        /// </param>
        public void MoveL(Mat target, bool blocking = true)
        {
            Link.moveX(null, null, target, this, 2, blocking);
        }

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
        public void MoveC(Item itemtarget1, Item itemtarget2, bool blocking = true)
        {
            Link.moveC_private(itemtarget1, null, null, itemtarget2, null, null, this, blocking);
        }

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
        public void MoveC(double[] joints1, double[] joints2, bool blocking = true)
        {
            Link.moveC_private(null, joints1, null, null, joints2, null, this, blocking);
        }

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
        public void MoveC(Mat target1, Mat target2, bool blocking = true)
        {
            Link.moveC_private(null, null, target1, null, null, target2, this, blocking);
        }

        /// <summary>
        ///     Checks if a joint movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> destination joints</param>
        /// <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        /// <returns>
        ///     collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of
        ///     objects that collided if there was a collision.
        /// </returns>
        public int MoveJ_Test(double[] j1, double[] j2, double minstep_deg = -1)
        {
            Link.check_connection();
            var command = "CollisionMove";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_array(j1);
            Link.send_array(j2);
            Link.send_int((int) (minstep_deg * 1000.0));
            Link.ReceiveTimeout = 3600 * 1000;
            var collision = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            Link.check_status();
            return collision;
        }

        /// <summary>
        ///     Checks if a linear movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> destination joints</param>
        /// <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        /// <returns>
        ///     collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of
        ///     objects that collided if there was a collision.
        /// </returns>
        public int MoveL_Test(double[] j1, double[] j2, double minstep_deg = -1)
        {
            Link.check_connection();
            var command = "CollisionMoveL";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_array(j1);
            Link.send_array(j2);
            Link.send_int((int) (minstep_deg * 1000.0));
            Link.ReceiveTimeout = 3600 * 1000;
            var collision = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            Link.check_status();
            return collision;
        }

        /// <summary>
        ///     Sets the speed and/or the acceleration of a robot.
        /// </summary>
        /// <param name="speed">speed -> speed in mm/s (-1 = no change)</param>
        /// <param name="accel">acceleration (optional) -> acceleration in mm/s2 (-1 = no change)</param>
        /// <summary>
        ///     Sets the speed and/or the acceleration of a robot.
        /// </summary>
        /// <param name="speed_linear">linear speed in mm/s (-1 = no change)</param>
        /// <param name="accel_linear">linear acceleration in mm/s2 (-1 = no change)</param>
        /// <param name="speed_joints">joint speed in deg/s (-1 = no change)</param>
        /// <param name="accel_joints">joint acceleration in deg/s2 (-1 = no change)</param>
        public void setSpeed(double speed_linear, double accel_linear = -1, double speed_joints = -1,
            double accel_joints = -1)
        {
            Link.check_connection();
            var command = "S_Speed4";
            Link.send_line(command);
            Link.send_item(this);
            var speed_accel = new double[4];
            speed_accel[0] = speed_linear;
            speed_accel[1] = accel_linear;
            speed_accel[2] = speed_joints;
            speed_accel[3] = accel_joints;
            Link.send_array(speed_accel);
            Link.check_status();
        }

        /// <summary>
        ///     Sets the robot movement smoothing accuracy (also known as zone data value).
        /// </summary>
        /// <param name="zonedata">zonedata value (int) (robot dependent, set to -1 for fine movements)</param>
        public void setZoneData(double zonedata)
        {
            Link.check_connection();
            var command = "S_ZoneData";
            Link.send_line(command);
            Link.send_int((int) (zonedata * 1000.0));
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Displays a sequence of joints
        /// </summary>
        /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
        public void ShowSequence(Mat sequence)
        {
            Link.check_connection();
            var command = "Show_Seq";
            Link.send_line(command);
            Link.send_matrix(sequence);
            Link.send_item(this);
            Link.check_status();
        }


        /// <summary>
        ///     Checks if a robot or program is currently running (busy or moving)
        /// </summary>
        /// <returns>busy status (true=moving, false=stopped)</returns>
        public bool Busy()
        {
            Link.check_connection();
            var command = "IsBusy";
            Link.send_line(command);
            Link.send_item(this);
            var busy = Link.rec_int();
            Link.check_status();
            return busy > 0;
        }

        /// <summary>
        ///     Stops a program or a robot
        /// </summary>
        /// <returns></returns>
        public void Stop()
        {
            Link.check_connection();
            var command = "Stop";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        /// <summary>
        ///     Waits (blocks) until the robot finishes its movement.
        /// </summary>
        /// <param name="timeout_sec">timeout -> Max time to wait for robot to finish its movement (in seconds)</param>
        public void WaitMove(double timeout_sec = 300)
        {
            Link.check_connection();
            var command = "WaitMove";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
            Link.ReceiveTimeout = (int) (timeout_sec * 1000.0);
            Link.check_status(); //will wait here;
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;

            //int isbusy = link.Busy(this);
            //while (isbusy)
            //{
            //    busy = link.Busy(item);
            //}
        }

        ///////// ADD MORE METHODS


        // ---- Program item calls -----

        /// <summary>
        ///     Saves a program to a file.
        /// </summary>
        /// <param name="filename">File path of the program</param>
        /// <param name="run_mode">RUNMODE_MAKE_ROBOTPROG to generate the program file.Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.</param>
        /// <returns>Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)</returns>
        public bool MakeProgram(string filename = "", RunMode run_mode = RunMode.MakeRobotProgram)
        {
            Link.check_connection();
            Link.send_line("MakeProg2");
            Link.send_item(this);
            Link.send_line(filename);
            Link.send_int((int) run_mode);
            Link.ReceiveTimeout = 3600 * 1000;
            int prog_status = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            string prog_log_str = Link.rec_line();
            int transfer_status = Link.rec_int();
            Link.check_status();
            Link.LastStatusMessage = prog_log_str;
            bool success = prog_status > 0;
            bool transfer_ok = transfer_status > 0;
            return success && transfer_ok; // prog_log_str

            //return success, prog_log_str, transfer_ok
        }

        /// <summary>
        ///     Sets if the program will be run in simulation mode or on the real robot.
        ///     Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force
        ///     the program to run on the robot.
        /// </summary>
        /// <returns>number of instructions that can be executed</returns>
        public void SetRunType(ProgramExecutionType programExecutionType)
        {
            Link.check_connection();
            var command = "S_ProgRunType";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int((int) programExecutionType);
            Link.check_status();
        }

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
        public int RunProgram()
        {
            Link.check_connection();
            var command = "RunProg";
            Link.send_line(command);
            Link.send_item(this);
            var progStatus = Link.rec_int();
            Link.check_status();
            return progStatus;
        }


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
        public int RunCode(string parameters = null)
        {
            Link.check_connection();
            if (parameters == null)
            {
                var command = "RunProg";
                Link.send_line(command);
                Link.send_item(this);
            }
            else
            {
                var command = "RunProgParam";
                Link.send_line(command);
                Link.send_item(this);
                Link.send_line(parameters);
            }

            var progstatus = Link.rec_int();
            Link.check_status();
            return progstatus;
        }

        /// <summary>
        /// Adds a program call, code, message or comment to the program. Returns True if succeeded.
        /// </summary>
        /// <param name="code">string of the code or program to run </param>
        /// <param name="runType">specify if the code is a program</param>
        /// <returns>True if success; False othwersise</returns>
        public bool RunCodeCustom(string code, ProgramRunType runType = ProgramRunType.CallProgram)
        {
            Link.check_connection();
            var command = "RunCode2";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(code.Replace("\n\n", "<br>").Replace("\n", "<br>"));
            Link.send_int((int) runType);
            var progstatus = Link.rec_int();
            Link.check_status();
            return progstatus == 0;
        }

        /// <summary>
        ///     Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the
        ///     robot to stop and let the user resume the program anytime.
        /// </summary>
        /// <param name="time_ms">Time in milliseconds</param>
        public void Pause(double time_ms = -1)
        {
            Link.check_connection();
            var command = "RunPause";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int((int) (time_ms * 1000.0));
            Link.check_status();
        }


        /// <summary>
        ///     Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
        /// </summary>
        /// <param name="io_var">io_var -> digital output (string or number)</param>
        /// <param name="io_value">io_value -> value (string or number)</param>
        public void setDO(string io_var, string io_value)
        {
            Link.check_connection();
            var command = "setDO";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(io_var);
            Link.send_line(io_value);
            Link.check_status();
        }

        /// <summary>
        ///     Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
        /// </summary>
        /// <param name="io_var">io_var -> digital output (string or number)</param>
        /// <param name="io_value">io_value -> value (string or number)</param>
        /// <param name="timeout_ms">int (optional) -> timeout in miliseconds</param>
        public void waitDI(string io_var, string io_value, double timeout_ms = -1)
        {
            Link.check_connection();
            var command = "waitDI";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(io_var);
            Link.send_line(io_value);
            Link.send_int((int) (timeout_ms * 1000.0));
            Link.check_status();
        }

        /// <summary>
        ///     Add a custom instruction. This instruction will execute a Python file or an executable file.
        /// </summary>
        /// <param name="name"></param>
        /// <param name="path_run">path to run(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="path_icon">icon path(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="blocking">True if blocking, 0 if it is a non blocking executable trigger</param>
        /// <param name="cmd_run_on_robot">Command to run through the driver when connected to the robot</param>
        /// :param name: digital input (string or number)
        public void customInstruction(string name, string path_run, string path_icon = "", bool blocking = true,
            string cmd_run_on_robot = "")
        {
            Link.check_connection();
            var command = "InsCustom2";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(name);
            Link.send_line(path_run);
            Link.send_line(path_icon);
            Link.send_line(cmd_run_on_robot);
            Link.send_int(blocking ? 1 : 0);
            Link.check_status();
        }

        /// <summary>
        ///     Adds a new robot move joint instruction to a program. Obsolete. Use MoveJ instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        public void addMoveJ(Item itemtarget)
        {
            Link.check_connection();
            var command = "Add_INSMOVE";
            Link.send_line(command);
            Link.send_item(itemtarget);
            Link.send_item(this);
            Link.send_int(1);
            Link.check_status();
        }

        /// <summary>
        ///     Adds a new robot move linear instruction to a program. Obsolete. Use MoveL instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        public void addMoveL(Item itemtarget)
        {
            Link.check_connection();
            var command = "Add_INSMOVE";
            Link.send_line(command);
            Link.send_item(itemtarget);
            Link.send_item(this);
            Link.send_int(2);
            Link.check_status();
        }

        ////////// ADD MORE METHODS
        /// <summary>
        ///     Returns the number of instructions of a program.
        /// </summary>
        /// <returns></returns>
        public int InstructionCount()
        {
            Link.check_connection();
            var command = "Prog_Nins";
            Link.send_line(command);
            Link.send_item(this);
            var nins = Link.rec_int();
            Link.check_status();
            return nins;
        }

        /// <summary>
        ///     Returns the program instruction at position id
        /// </summary>
        /// <param name="instructionId"></param>
        /// <returns>program instruction at position instructionId</returns>
        public ProgramInstruction GetInstruction(int instructionId)
        {
            ProgramInstruction programInstruction = new ProgramInstruction();

            Link.check_connection();
            var command = "Prog_GIns";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int(instructionId);

            programInstruction.Name = Link.rec_line();
            programInstruction.InstructionType = (InstructionType) Link.rec_int();
            programInstruction.MoveType = MoveType.Invalid;
            programInstruction.IsJointTarget = false;
            programInstruction.Target = null;
            programInstruction.Joints = null;
            if (programInstruction.InstructionType == InstructionType.Move)
            {
                programInstruction.MoveType = (MoveType) Link.rec_int();
                programInstruction.IsJointTarget = Link.rec_int() > 0 ? true : false;
                programInstruction.Target = Link.rec_pose();
                programInstruction.Joints = Link.rec_array();
            }

            Link.check_status();
            return programInstruction;
        }

        /// <summary>
        ///     Sets the program instruction at position id
        /// </summary>
        /// <param name="instructionId"></param>
        /// <param name="instruction"></param>
        public void SetInstruction(int instructionId, ProgramInstruction instruction)
        {
            Link.check_connection();
            var command = "Prog_SIns";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int(instructionId);
            Link.send_line(instruction.Name);
            Link.send_int((int) instruction.InstructionType);
            if (instruction.InstructionType == InstructionType.Move)
            {
                Link.send_int((int) instruction.MoveType);
                Link.send_int(instruction.IsJointTarget ? 1 : 0);
                Link.send_pose(instruction.Target);
                Link.send_array(instruction.Joints);
            }

            Link.check_status();
        }


        public UpdateResult Update()
        {
            /*Updates a program and returns the estimated time and the number of valid instructions.
        
                :return: [valid_instructions, program_time, program_distance, valid_program]

            valid_instructions: The number of valid instructions

            program_time: Estimated cycle time(in seconds)


            program_distance: Estimated distance that the robot TCP will travel(in mm)


            valid_program: It is 1 if the program has no issues, 0 otherwise.


                ..seealso:: :func:`~robolink.Robolink.AddProgram`
            */
            Link.check_connection();
            var command = "Update";
            Link.send_line(command);
            Link.send_item(this);
            var values = Link.rec_array();
            if (values == null)
            {
                throw new Exception("Item Update failed.");
            }

            Link.check_status();

            //var validInstructions = values[0];
            //var program_time = values[1]
            //var program_distance = values[2]
            //var valid_program = values[3]
            UpdateResult updateResult = new UpdateResult(
                values[0], values[1], values[2], values[3]);
            return updateResult;
        }

        /// <summary>
        /// Updates a program and returns the estimated time and the number of valid instructions.
        /// An update can also be applied to a robot machining project. The update is performed on the generated program.
        /// </summary>
        /// <param name="collisionCheck">check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)</param>
        /// <param name="timeoutSec">Maximum time to wait for the update to complete (in seconds)</param>
        /// <param name="linStepMm">Maximum step in millimeters for linear movements (millimeters). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <param name="jointStepDeg">Maximum step for joint movements (degrees). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <returns>1.0 if there are no problems with the path or less than 1.0 if there is a problem in the path (ratio of problem)</returns>
        public UpdateResult Update(
            CollisionCheckOptions collisionCheck, /* = CollisionCheckOptions.CollisionCheckOff, */
            int timeoutSec = 3600,
            double linStepMm = -1,
            double jointStepDeg = -1)
        {
            Link.check_connection();
            Link.send_line("Update2");
            Link.send_item(this);
            double[] values = {(double) collisionCheck, linStepMm, jointStepDeg};
            Link.send_array(values);
            Link.ReceiveTimeout = timeoutSec * 1000;
            double[] result = Link.rec_array();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            string readable_msg = Link.rec_line();
            Link.check_status();
            Link.LastStatusMessage = readable_msg;
            UpdateResult updateResult = new UpdateResult(
                result[0], result[1], result[2], result[3], readable_msg);
            return updateResult;
        }


        /// <summary>
        ///     Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1
        ///     plus the number of robot axes.
        /// </summary>
        /// <param name="instructions">the matrix of instructions</param>
        /// <returns>Returns 0 if success</returns>
        public int InstructionList(out Mat instructions)
        {
            Link.check_connection();
            var command = "G_ProgInsList";
            Link.send_line(command);
            Link.send_item(this);
            instructions = Link.rec_matrix();
            var errors = Link.rec_int();
            Link.check_status();
            return errors;
        }


        // CHU: Old Version
        ///// <summary>
        /////     Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are
        /////     rounded according to the smoothing parameter set inside the program.
        ///// </summary>
        ///// <param name="error_msg">Returns a human readable error message (if any)</param>
        ///// <param name="joint_list">
        /////     Returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] if a file
        /////     name is not specified
        ///// </param>
        ///// <param name="mm_step">Maximum step in millimeters for linear movements (millimeters)</param>
        ///// <param name="deg_step">Maximum step for joint movements (degrees)</param>
        ///// <param name="save_to_file">
        /////     Provide a file name to directly save the output to a file. If the file name is not provided
        /////     it will return the matrix. If step values are very small, the returned matrix can be very large.
        ///// </param>
        ///// <returns>Returns 0 if success, otherwise, it will return negative values</returns>
        //public int InstructionListJoints(out string error_msg, out Mat joint_list, double mm_step = 10.0,
        //    double deg_step = 5.0, string save_to_file = "")
        //{
        //    Link.check_connection();
        //    var command = "G_ProgJointList";
        //    Link.send_line(command);
        //    Link.send_item(this);
        //    double[] ste_mm_deg = {mm_step, deg_step};
        //    Link.send_array(ste_mm_deg);
        //    //joint_list = save_to_file;
        //    if (save_to_file.Length <= 0)
        //    {
        //        Link.send_line("");
        //        joint_list = Link.rec_matrix();
        //    }
        //    else
        //    {
        //        Link.send_line(save_to_file);
        //        joint_list = null;
        //    }
        //    var error_code = Link.rec_int();
        //    error_msg = Link.rec_line();
        //    Link.check_status();
        //    return error_code;
        //}

        /// <summary>
        /// Returns a list of joints. 
        /// Linear moves are rounded according to the smoothing parameter set inside the program.
        /// </summary>
        /// <param name="mmStep">Maximum step in millimeters for linear movements (millimeters)</param>
        /// <param name="degStep">Maximum step for joint movements (degrees)</param>
        /// <param name="saveToFile">Provide a file name to directly save the output to a file. If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.</param>
        /// <param name="collisionCheck">Check for collisions: will set to 1 or 0</param>
        /// <param name="flags">Reserved for future compatibility</param>
        /// <param name="timeoutSec"></param>
        /// <returns>List of InstructionListJointsResult.</returns>
        public InstructionListJointsResult GetInstructionListJoints(
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            int flags = 0,
            int timeoutSec = 3600)
        {
            InstructionListJointsResult result =
                new InstructionListJointsResult {JointList = new List<InstructionListJointsResult.JointsResult>()};

            string errorMessage;
            Mat jointList;
            result.ErrorCode = InstructionListJoints(out errorMessage, out jointList, mmStep, degStep, saveToFile, collisionCheck,
                flags, timeoutSec);
            result.ErrorMessage = errorMessage;

            int numberOfJoints = jointList.Rows - 4;
            for (var colId = 0; colId < jointList.Cols; colId++)
            {
                var joints = new double[numberOfJoints]; 
                for (var rowId = 0; rowId < numberOfJoints; rowId++)
                {
                    joints[rowId] = jointList[rowId, colId];
                }

                var hasCollision = (int)jointList[numberOfJoints, colId] > 0;
                if (hasCollision)
                {
                    hasCollision = true;
                }
                int jointError = (int)jointList[numberOfJoints, colId];
                ErrorPathType errorType = (ErrorPathType)Convert.ToUInt32(jointError.ToString(), 2);
                var maxLinearStep = jointList[numberOfJoints + 1, colId];
                var maxJointStep = jointList[numberOfJoints + 2, colId];
                var moveId = (int)jointList[numberOfJoints + 3, colId];
                result.JointList.Add(
                    new InstructionListJointsResult.JointsResult()
                    {
                        Joints = joints,
                        Error = errorType,
                        MaxLinearStep = maxLinearStep,
                        MaxJointStep = maxJointStep,
                        MoveId = moveId
                    }
                );
            }
            return result;
        }

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
        /// <param name="timeoutSec"></param>
        /// <returns>Returns 0 if success, otherwise, it will return negative values</returns>
        public int InstructionListJoints(out string errorMsg,
            out Mat jointList,
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            int flags = 0,
            int timeoutSec = 3600)
        {
            Link.check_connection();
            Link.send_line("G_ProgJointList");
            Link.send_item(this);
            double[] parameter = {mmStep, degStep, (double) collisionCheck, flags};
            Link.send_array(parameter);

            //joint_list = save_to_file;
            Link.ReceiveTimeout = timeoutSec * 1000;
            if (string.IsNullOrEmpty(saveToFile))
            {
                Link.send_line("");
                jointList = Link.rec_matrix();
            }
            else
            {
                Link.send_line(saveToFile);
                jointList = null;
            }

            int errorCode = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            errorMsg = Link.rec_line();
            Link.check_status();
            return errorCode;
        }

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        public void Finish()
        {
            Link.Finish();
        }

        #endregion
    }
}