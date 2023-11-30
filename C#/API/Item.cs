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
using System.Diagnostics;
#if NET45
using System.Windows.Media;
#else
using System.Drawing;
#endif
using RoboDk.API.Exceptions;
using RoboDk.API.Model;
// ReSharper disable InconsistentNaming

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
    internal class Item : IItem
    {
        #region Fields

        private readonly ItemType _type;
        private string _name;

        #endregion

        #region Constructors

        /// <summary>
        /// Constructor
        /// </summary>
        public Item(RoboDK connectionLink, long itemId = 0, ItemType itemType = ItemType.Any)
        {
            ItemId = itemId;
            Link = connectionLink;
            _type = itemType;
            _name = "";
        }

        #endregion

        #region Properties

        internal RoboDK Link { get; private set; }

        public long ItemId { get; private set; }

        #endregion

        #region Public Methods

        public IItem Clone(IRoboDK connectionLink)
        {
            var item = new Item((RoboDK)connectionLink, this.ItemId, this._type);
            var itemProxy = connectionLink.ItemInterceptFunction(item);
            return itemProxy;
        }

        public override string ToString()
        {
            if (Valid())
            {
                return $"RoboDK item(name:{_name}, id:{ItemId}, type:{_type})";
            }

            return "RoboDK item (INVALID)";
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public ItemFlags GetItemFlags()
        {
            Link.check_connection();
            string command = "G_Item_Rights";
            Link.send_line(command);
            Link.send_item(this);
            int flags = Link.rec_int();
            ItemFlags itemFlags = (ItemFlags) flags;
            Link.check_status();
            return itemFlags;
        }

        /// <inheritdoc />
        public bool Equals(IItem otherItem)
        {
            return ItemId == otherItem?.ItemId;
        }

        /// <inheritdoc />
        public RoboDK RL()
        {
            return Link;
        }

        /// <inheritdoc />
        public RoboDK RDK()
        {
            return Link;
        }

        /// <inheritdoc />
        public RoboDK.IRoboDKLink GetRoboDkLink()
        {
            return Link.GetRoboDkLink();
        }

        /// <inheritdoc />
        public void NewLink()
        {
            Link = new RoboDK();
            Link.Connect();
        }

        //////// GENERIC ITEM CALLS

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void Save(string filename)
        {
            Link.Save(filename, this);
        }

        /// <inheritdoc />
        public void Delete()
        {
            if (ItemId == 0)
            {
                throw new RdkException("Item does not exist");
            }
            Link.check_connection();
            var command = "Remove";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
            ItemId = 0;
        }

        /// <inheritdoc />
        public bool Valid()
        {
            if (ItemId == 0)
            {
                return false;
            }

            return true;
        }

        /// <inheritdoc />
        public void SetParent(IItem parent)
        {
            Link.check_connection();
            Link.send_line("S_Parent");
            Link.send_item(this);
            Link.send_item(parent);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetParentStatic(IItem parent)
        {
            Link.check_connection();
            Link.send_line("S_Parent_Static");
            Link.send_item(this);
            Link.send_item(parent);
            Link.check_status();
        }

        /// <inheritdoc />
        public IItem AttachClosest()
        {
            Link.check_connection();
            Link.send_line("Attach_Closest");
            Link.send_item(this);
            IItem item_attached = Link.rec_item();
            Link.check_status();
            return item_attached;
        }

        /// <inheritdoc />
        public IItem DetachClosest(IItem parent = null)
        {
            Link.check_connection();
            Link.send_line("Detach_Closest");
            Link.send_item(this);
            Link.send_item(parent);
            IItem item_detached = Link.rec_item();
            Link.check_status();
            return item_detached;
        }
        
        /// <inheritdoc />
        public void DetachAll(IItem parent = null)
        {
            Link.check_connection();
            Link.send_line("Detach_All");
            Link.send_item(this);
            Link.send_item(parent);
            Link.check_status();
        }

        /// <inheritdoc />
        public List<IItem> Childs()
        {
            Link.check_connection();
            var command = "G_Childs";
            Link.send_line(command);
            Link.send_item(this);
            var nitems = Link.rec_int();
            var itemlist = new List<IItem>(nitems);
            for (var i = 0; i < nitems; i++)
            {
                itemlist.Add(Link.rec_item());
            }

            Link.check_status();
            return itemlist;
        }

        /// <inheritdoc />
        public IItem Parent()
        {
            Link.check_connection();
            var command = "G_Parent";
            Link.send_line(command);
            Link.send_item(this);
            var parent = Link.rec_item();
            Link.check_status();
            return parent;
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void SetVisible(bool visible, VisibleRefType visible_reference = VisibleRefType.Default)
        {
            if (visible_reference == VisibleRefType.Default)
            {
                visible_reference = visible ? VisibleRefType.On : VisibleRefType.Off;
            }

            Link.check_connection();
            var command = "S_Visible";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int(visible ? 1 : 0);
            Link.send_int((int)visible_reference);
            Link.check_status();
        }

        /// <inheritdoc />
        public void ShowAsCollided(bool collided, int robotLinkId = 0)
        {
            Link.RequireBuild(5449);
            Link.check_connection();
            Link.send_line("ShowAsCollided");
            Link.send_item(this);
            Link.send_int(robotLinkId);
            Link.send_int(collided ? 1 : 0);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void SetName(string name)
        {
            Link.check_connection();
            var command = "S_Name";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(name);
            Link.check_status();
        }

		/// <inheritdoc />
		public void setParamRobotTool(double toolMass = 5, double[] toolCOG = null)
		{
			Link.check_connection();
			var command = "S_ParamCalibTool";
			Link.send_line(command);
			Link.send_item(this);
            Link.send_double(toolMass);
            if (toolCOG != null)
            {
                Link.send_array(toolCOG);
            }
			Link.check_status();
        }

        /// <inheritdoc />
        public string SetParam(string param, string value = "")
        {
            Link.RequireBuild(7129);
            Link.check_connection();
            Link.send_line("ICMD");
            Link.send_item(this);
            Link.send_line(param);
            Link.send_line(value);
            var response = Link.rec_line();
            Link.check_status();
            return response;
        }

        /// <inheritdoc />
        public void SetParam(string param, byte[] value)
        {
            Link.RequireBuild(7129);
            Link.check_connection();
            Link.send_line("S_ItmDataParam");
            Link.send_item(this);
            Link.send_line(param);
            Link.send_bytes(value);
            Link.check_status();
        }

        /// <inheritdoc />
        public byte[] GetParam(string param)
        {
            Link.RequireBuild(7129);
            Link.check_connection();
            Link.send_line("G_ItmDataParam");
            Link.send_item(this);
            Link.send_line(param);
            byte [] data = Link.rec_bytes();
            Link.check_status();
            return data;
        }


        /// <inheritdoc />
        public void SetPose(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hlocal";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void SetGeometryPose(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hgeom";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void SetHtool(Mat pose)
        {
            Link.check_connection();
            var command = "S_Htool";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
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

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void SetPoseFrame(Mat framePose)
        {
            Link.check_connection();
            var command = "S_Frame";
            Link.send_line(command);
            Link.send_pose(framePose);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetPoseFrame(IItem frameItem)
        {
            Link.check_connection();
            var command = "S_Frame_ptr";
            Link.send_line(command);
            Link.send_item(frameItem);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetPoseTool(Mat toolPose)
        {
            Link.check_connection();
            var command = "S_Tool";
            Link.send_line(command);
            Link.send_pose(toolPose);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetPoseTool(IItem toolItem)
        {
            Link.check_connection();
            var command = "S_Tool_ptr";
            Link.send_line(command);
            Link.send_item(toolItem);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetPoseAbs(Mat pose)
        {
            Link.check_connection();
            var command = "S_Hlocal_Abs";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(pose);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        [Obsolete("Deprecated, please use new Recolor mehod which uses the new RoboDK Color class.")]
        public void Recolor(double[] tocolor, double[] fromcolor = null, double tolerance = 0.1)
        {
            Link.check_connection();
            if (fromcolor == null)
            {
                fromcolor = new double[] {0, 0, 0, 0};
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

        /// <inheritdoc />
        public void Recolor(Color tocolor, Color? fromcolor = null, double tolerance = 0.1)
        {
            var toColorArray = tocolor.ToRoboDKColorArray();
            Link.check_connection();
            if (fromcolor.HasValue == false)
            {
                fromcolor = Color.FromArgb(0, 0, 0, 0);
                tolerance = 2;
            }

            var fromColorArray = fromcolor.Value.ToRoboDKColorArray();

            Link.check_color(toColorArray);
            Link.check_color(fromColorArray);
            var command = "Recolor";
            Link.send_line(command);
            Link.send_item(this);
            var combined = new double[9];
            combined[0] = tolerance;
            Array.Copy(fromColorArray, 0, combined, 1, 4);
            Array.Copy(toColorArray, 0, combined, 5, 4);
            Link.send_array(combined);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetColor(Color tocolor)
        {
            double[] tocolorArray = tocolor.ToRoboDKColorArray();
            Link.check_connection();            
            Link.check_color(tocolorArray);
            Link.send_line("S_Color");
            Link.send_item(this);
            Link.send_array(tocolorArray);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetColor(int shapeId, Color tocolor)
        {
            double[] tocolorArray = tocolor.ToRoboDKColorArray();
            Link.check_color(tocolorArray);
            Link.check_connection();
            Link.send_line("S_ShapeColor");
            Link.send_item(this);
            Link.send_int(shapeId);
            Link.send_array(tocolorArray);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetTransparency(double alpha)
        {
            // saturate the alpha channel so it remains between 0 and 1.
            alpha = Math.Min(1, Math.Max(0, alpha));
            Link.check_connection();
            double[] tocolorArray = {-1, -1, -1, alpha};
            Link.send_line("S_Color");
            Link.send_item(this);
            Link.send_array(tocolorArray);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
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

        /// <inheritdoc />
        public IItem AddCurve(Mat curvePoints, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            return Link.AddCurve(curvePoints, this, addToRef, projectionType);
        }

        /// <inheritdoc />
        public Mat ProjectPoints(Mat points, ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            return Link.ProjectPoints(points, this, projectionType);
        }


        /// <inheritdoc />
        public bool SelectedFeature(out ObjectSelectionType featureType, out int featureId)
        {
            Link.check_connection();
            Link.send_line("G_ObjSelection");
            Link.send_item(this);
            int isSelected = Link.rec_int();
            featureType = (ObjectSelectionType)Link.rec_int();
            featureId = Link.rec_int();
            Link.check_status();
            return isSelected > 0;
        }

        /// <inheritdoc />
        public string GetPoints(ObjectSelectionType featureType, int featureId, out Mat pointList)
        {
            Link.check_connection();
            Link.send_line("G_ObjPoint");
            Link.send_item(this);
            Link.send_int((int)featureType);
            Link.send_int(featureId);
            pointList = Link.rec_matrix();
            string name = Link.rec_line();
            Link.check_status();
            return name;
        }

        /// <inheritdoc />
        public IItem SetMachiningParameters(string ncfile = "", IItem partObj = null, string options = "")
        {
            Link.check_connection();
            Link.send_line("S_MachiningParams");
            Link.send_item(this);
            Link.send_line(ncfile);
            Link.send_item(partObj);
            Link.send_line("NO_UPDATE " + options);
            Link.ReceiveTimeout = 3600 * 1000;
            IItem program = Link.rec_item();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            double status = Link.rec_int() / 1000.0;
            Link.check_status();
            return program;
        }

        //"""Target item calls"""

        /// <inheritdoc />
        public void SetAsCartesianTarget()
        {
            Link.check_connection();
            var command = "S_Target_As_RT";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetAsJointTarget()
        {
            Link.check_connection();
            var command = "S_Target_As_JT";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        //#####Robot item calls####

        /// <inheritdoc />
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

        /// <inheritdoc />
        public double[] SimulatorJoints()
        {
            Link.check_connection();
            var command = "G_Thetas_Sim";
            Link.send_line(command);
            Link.send_item(this);
            var joints = Link.rec_array();
            Link.check_status();
            return joints;
        }

        // add more methods

        /// <inheritdoc />
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


        /// <inheritdoc />
        public void SetJointsHome(double[] joints)
        {
            Link.check_connection();
            const string command = @"S_Home";
            Link.send_line(command);
            Link.send_array(joints);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        /// <returns></returns>
        public IItem ObjectLink(int linkId = 0)
        {
            Link.check_connection();
            Link.send_line("G_LinkObjId");
            Link.send_item(this);
            Link.send_int(linkId);
            IItem item = Link.rec_item();
            Link.check_status();
            return item;
        }

        /// <inheritdoc />
        public IItem GetLink(ItemType typeLinked = ItemType.Robot)
        {
            Link.check_connection();
            Link.send_line("G_LinkType");
            Link.send_item(this);
            Link.send_int((int) typeLinked);
            IItem item = Link.rec_item();
            Link.check_status();
            return item;
        }

        /// <inheritdoc />
        public bool SetJoints(double[] joints, SetJointsType saturate_action = SetJointsType.Default)
        {
            if (saturate_action == SetJointsType.Default)
            {
                Link.check_connection();
                var command = "S_Thetas";
                Link.send_line(command);
                Link.send_array(joints);
                Link.send_item(this);
                Link.check_status();
                return true;
            }
            else
            {
                Link.RequireBuild(14129);
                Link.check_connection();
                var command = "S_Thetas2";
                Link.send_line(command);
                Link.send_array(joints);
                Link.send_item(this);
                Link.send_int((int) saturate_action);
                bool isvalid = Link.rec_int() == 1;
                Link.check_status();
                return isvalid;
            }
        }

        /// <inheritdoc />
        public void JointLimits(out double[] lowerLlimits, out double[] upperLimits)
        {
            Link.check_connection();
            var command = "G_RobLimits";
            Link.send_line(command);
            Link.send_item(this);
            lowerLlimits = Link.rec_array();
            upperLimits = Link.rec_array();
            var jointsType = Link.rec_int() / 1000.0;
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetJointLimits(double[] lower_limits, double[] upper_limits)
        {
            Link.check_connection();
            Link.send_line("S_RobLimits");
            Link.send_item(this);
            Link.send_array(lower_limits);
            Link.send_array(upper_limits);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetRobot(IItem robot = null)
        {
            Link.check_connection();
            var command = "S_Robot";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_item(robot);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetFrame(IItem frame)
        {
            SetPoseFrame(frame);
        }

        /// <inheritdoc />
        public void SetFrame(Mat frame)
        {
            SetPoseFrame(frame);
        }

        /// <inheritdoc />
        public void SetTool(IItem tool)
        {
            SetPoseTool(tool);
        }

        /// <inheritdoc />
        public void SetTool(Mat tool)
        {
            SetPoseTool(tool);
        }

        /// <inheritdoc />
        public IItem AddTool(Mat toolPose, string toolName = "New TCP")
        {
            Link.check_connection();
            var command = "AddToolEmpty";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_pose(toolPose);
            Link.send_line(toolName);
            var newtool = Link.rec_item();
            Link.check_status();
            return newtool;
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
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

        /// <inheritdoc />
        /// <returns>array of joints</returns>
        public double[] SolveIK(Mat pose, double[] jointsApprox = null, Mat tool = null, Mat reference = null)
        {
            if (tool != null)
            {
                pose = pose * tool.inv();
            }
            if (reference != null)
            {
                pose = reference * pose;
            }
            Link.check_connection();
            if (jointsApprox == null)
            {
                Link.send_line("G_IK");
                Link.send_pose(pose);
            }
            else
            {
                Link.send_line("G_IK_jnts");
                Link.send_pose(pose);
                Link.send_array(jointsApprox);
            }
            Link.send_item(this);
            var jointsok = Link.rec_array();
            Link.check_status();
            return jointsok;
        }

        /// <inheritdoc />
        public Mat SolveIK_All(Mat pose, Mat tool = null, Mat reference = null)
        {
            if (tool != null)
            {
                pose = pose * tool.inv();
            }
            if (reference != null)
            {
                pose = reference * pose;
            }
            Link.check_connection();
            var command = "G_IK_cmpl";
            Link.send_line(command);
            Link.send_pose(pose);
            Link.send_item(this);
            var jointsList = Link.rec_matrix();
            Link.check_status();
            return jointsList;
        }

        /// <inheritdoc />
        public bool Connect(string robotIp = "")
        {
            Link.check_connection();
            var command = "Connect";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(robotIp);
            var status = Link.rec_int();
            Link.check_status();
            return status != 0;
        }

		/// <inheritdoc />
		public bool ConnectSafe(string robotIp = "", int maxAttempts = 5, int waitConnection = 4)
		{
			int tryCount = 0;
			int refreshRate = 500; // [ms]
			var waitSpan = new TimeSpan(0, 0, waitConnection);
            RobotConnectionType connectionStatus;
			Connect(robotIp);
			var timer = new Stopwatch();
			timer.Start();
			var attemptStart = timer.Elapsed;
			System.Threading.Thread.Sleep(refreshRate);
			while (true)
			{
				connectionStatus = ConnectedState();
                Console.WriteLine(connectionStatus); //.Message);
				if (connectionStatus == RobotConnectionType.Ready)
				{
					break;
				}
				else if (connectionStatus == RobotConnectionType.Disconnected)
				{
					Console.WriteLine("Trying to reconnect...");
					Connect(robotIp);
				}

				if (timer.Elapsed - attemptStart > waitSpan)
				{
					attemptStart = timer.Elapsed;
					Disconnect();
					tryCount++;
					if (tryCount >= maxAttempts)
					{
						Console.WriteLine("Failed to connect: Timed out");
						break;
					}
					Console.WriteLine("Retrying connection, attempt #" + (tryCount + 1));
				}

				System.Threading.Thread.Sleep(refreshRate);
			}

			return connectionStatus == RobotConnectionType.Ready;
		}

		/// <inheritdoc />
		public RobotConnectionParameter ConnectionParams()
		{
			Link.check_connection();
			const string command = "ConnectParams";
			Link.send_line(command);
			Link.send_item(this);
			var robotIp = Link.rec_line();
			var port = Link.rec_int();
			var remotePath = Link.rec_line();
			var ftpUser = Link.rec_line();
			var ftpPass = Link.rec_line();
			Link.check_status();
			return new RobotConnectionParameter(robotIp, port, remotePath, ftpUser, ftpPass);
		}

		/// <inheritdoc />
		public void setConnectionParams(string robotIP, int port, string remotePath, string ftpUser, string ftpPass)
		{
			Link.check_connection();
			var command = "setConnectParams";
			Link.send_line(command);
			Link.send_item(this);
			Link.send_line(robotIP);
			Link.send_int(port);
			Link.send_line(remotePath);
			Link.send_line(ftpUser);
			Link.send_line(ftpPass);
			Link.check_status();
		}

		/// <inheritdoc />
		public RobotConnectionType ConnectedState()
		{
			Link.check_connection();
			var command = "ConnectedState";
			Link.send_line(command);
			Link.send_item(this);
            RobotConnectionType status = (RobotConnectionType) Link.rec_int();
			var message = Link.rec_line();
			Link.check_status();
            return status;//((RobotConnectionStatus)status, message);
		}

		/// <inheritdoc />
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

        /// <inheritdoc />
        public void MoveJ(IItem itemtarget, bool blocking = true)
        {
            if (this.GetItemType() == ItemType.Program)
            {
                AddMoveJ(itemtarget);
            }
            else
            {
                Link.MoveX(itemtarget, null, null, this, 1, blocking);
            }
        }

        /// <inheritdoc />
        public void MoveJ(double[] joints, bool blocking = true)
        {
            Link.MoveX(null, joints, null, this, 1, blocking);
        }

        /// <inheritdoc />
        public void MoveJ(Mat target, bool blocking = true)
        {
            Link.MoveX(null, null, target, this, 1, blocking);
        }

        /// <inheritdoc />
        public void MoveL(IItem itemtarget, bool blocking = true)
        {
            if (this.GetItemType() == ItemType.Program)
            {
                AddMoveL(itemtarget);
            }
            else
            {
                Link.MoveX(itemtarget, null, null, this, 2, blocking);
            }
        }

        /// <inheritdoc />
        public void MoveL(double[] joints, bool blocking = true)
        {
            Link.MoveX(null, joints, null, this, 2, blocking);
        }

        /// <inheritdoc />
        public void MoveL(Mat target, bool blocking = true)
        {
            Link.MoveX(null, null, target, this, 2, blocking);
        }

        /// <inheritdoc />
        public void MoveC(IItem itemtarget1, IItem itemtarget2, bool blocking = true)
        {
            Link.moveC_private(itemtarget1, null, null, itemtarget2, null, null, this, blocking);
        }

        /// <inheritdoc />
        public void MoveC(double[] joints1, double[] joints2, bool blocking = true)
        {
            Link.moveC_private(null, joints1, null, null, joints2, null, this, blocking);
        }

        /// <inheritdoc />
        public void MoveC(Mat target1, Mat target2, bool blocking = true)
        {
            Link.moveC_private(null, null, target1, null, null, target2, this, blocking);
        }

        /// <inheritdoc />
        public int MoveJ_Test(double[] j1, double[] j2, double minstepDeg = -1)
        {
            Link.check_connection();
            Link.send_line("CollisionMove");
            Link.send_item(this);
            Link.send_array(j1);
            Link.send_array(j2);
            Link.send_int((int) (minstepDeg * 1000.0));
            Link.ReceiveTimeout = 3600 * 1000;
            var collision = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            Link.check_status();
            return collision;
        }

        /// <inheritdoc />
        public bool MoveJ_Test_Blend(double[] j1, double[] j2, double[] j3, double blendDeg = 5, double minstepDeg = -1)
        {
            Link.RequireBuild(7206);
            Link.check_connection();
            Link.send_line("CollisionMoveBlend");
            Link.send_item(this);
            Link.send_array(j1);
            Link.send_array(j2);
            Link.send_array(j3);
            Link.send_int((int)(minstepDeg * 1000.0));
            Link.send_int((int)(blendDeg * 1000.0));
            Link.ReceiveTimeout = 3600 * 1000;
            var collision = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            Link.check_status();
            return collision != 0;
        }

        /// <inheritdoc />
        public int MoveL_Test(double[] j1, Mat t2, double minstepDeg = -1)
        {
            Link.check_connection();
            var command = "CollisionMoveL";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_array(j1);
            Link.send_pose(t2);
            Link.send_int((int) (minstepDeg * 1000.0));
            Link.ReceiveTimeout = 3600 * 1000;
            var collision = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            Link.check_status();
            return collision;
        }

        /// <inheritdoc />
        public void SetSpeed(double speedLinear, double accelLinear = -1, double speedJoints = -1,
            double accelJoints = -1)
        {
            Link.check_connection();
            var command = "S_Speed4";
            Link.send_line(command);
            Link.send_item(this);
            var speedAccel = new double[4];
            speedAccel[0] = speedLinear;
            speedAccel[1] = speedJoints;
            speedAccel[2] = accelLinear;
            speedAccel[3] = accelJoints;
            Link.send_array(speedAccel);
            Link.check_status();
        }

        /// <inheritdoc />
        public void SetZoneData(double zonedata)
        {
            Link.check_connection();
            var command = "S_ZoneData";
            Link.send_line(command);
            Link.send_int((int) (zonedata * 1000.0));
            Link.send_item(this);
            Link.check_status();
        }


        /// <inheritdoc />
        public void SetRounding(double rounding)
        {
            Link.check_connection();
            var command = "S_ZoneData";
            Link.send_line(command);
            Link.send_int((int) rounding * 1000);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void ShowSequence(Mat sequence)
        {
            Link.check_connection();
            var command = "Show_Seq";
            Link.send_line(command);
            Link.send_matrix(sequence);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void ShowSequence(List<double[]> joints = null, List<Mat> poses = null, SequenceDisplayFlags flags = SequenceDisplayFlags.Default, int timeout = -1)
        {
            if (joints == null && poses == null)
            {
                return;
            }

            Link.check_connection();
            var command = "Show_SeqPoses";
            Link.send_line(command);
            Link.send_item(this);
            double[] options = { (double)flags, (double)timeout };
            Link.send_array(options);
            if (flags != SequenceDisplayFlags.Default && flags.HasFlag(SequenceDisplayFlags.RobotJoints))
            {
                Link.send_int(joints.Count);
                for (int i = 0; i < joints.Count; i++)
                {
                    Link.send_array(joints[i]);
                }
            }
            else
            {
                Link.send_int(poses.Count);
                for (int i = 0; i < poses.Count; i++)
                {
                    Link.send_pose(poses[i]);
                }
            }
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
        public void Stop()
        {
            Link.check_connection();
            var command = "Stop";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
        }

        /// <inheritdoc />
        public void WaitMove(double timeoutSec = 300)
        {
            Link.check_connection();
            var command = "WaitMove";
            Link.send_line(command);
            Link.send_item(this);
            Link.check_status();
            Link.ReceiveTimeout = (int) (timeoutSec * 1000.0);
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

        /// <inheritdoc />
        public bool MakeProgram(string filename = "", RunMode runMode = RunMode.MakeRobotProgram)
        {
            Link.check_connection();
            Link.send_line("MakeProg2");
            Link.send_item(this);
            Link.send_line(filename);
            Link.send_int((int) runMode);
            Link.ReceiveTimeout = 3600 * 1000;
            int progStatus = Link.rec_int();
            Link.ReceiveTimeout = Link.DefaultSocketTimeoutMilliseconds;
            string progLogStr = Link.rec_line();
            int transferStatus = Link.rec_int();
            Link.check_status();
            Link.LastStatusMessage = progLogStr;
            bool success = progStatus > 0;
            bool transferOk = transferStatus > 0;
            return success && transferOk; // prog_log_str

            //return success, prog_log_str, transfer_ok
        }

        /// <inheritdoc />
        public void SetRunType(ProgramExecutionType programExecutionType)
        {
            Link.check_connection();
            var command = "S_ProgRunType";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int((int) programExecutionType);
            Link.check_status();
        }

        /// <inheritdoc />
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

        /// <inheritdoc />
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
		
		/// <inheritdoc />
		public bool RunInstruction(string code, ProgramRunType runType = ProgramRunType.CallProgram)
		{
			return RunCodeCustom(code, runType);
		}
        /// <inheritdoc />
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

        /// <inheritdoc />
        public void Pause(double timeMs = -1)
        {
            Link.check_connection();
            var command = "RunPause";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_int((int) (timeMs * 1000.0));
            Link.check_status();
        }


        /// <inheritdoc />
        public void setDO(string ioVar, string ioValue)
        {
            Link.check_connection();
            var command = "setDO";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(ioVar);
            Link.send_line(ioValue);
            Link.check_status();
        }

        /// <inheritdoc />
        public void waitDI(string ioVar, string ioValue, double timeoutMs = -1)
        {
            Link.check_connection();
            var command = "waitDI";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(ioVar);
            Link.send_line(ioValue);
            Link.send_int((int) (timeoutMs * 1000.0));
            Link.check_status();
        }

        /// <inheritdoc />
        public void AddCustomInstruction(string name, string pathRun, string pathIcon = "", bool blocking = true,
            string cmdRunOnRobot = "")
        {
            Link.check_connection();
            var command = "InsCustom2";
            Link.send_line(command);
            Link.send_item(this);
            Link.send_line(name);
            Link.send_line(pathRun);
            Link.send_line(pathIcon);
            Link.send_line(cmdRunOnRobot);
            Link.send_int(blocking ? 1 : 0);
            Link.check_status();
        }

        /// <inheritdoc />
        public void AddMoveJ(IItem itemtarget)
        {
            Link.check_connection();
            var command = "Add_INSMOVE";
            Link.send_line(command);
            Link.send_item(itemtarget);
            Link.send_item(this);
            Link.send_int(1);
            Link.check_status();
        }

        /// <inheritdoc />
        public void AddMoveL(IItem itemtarget)
        {
            Link.check_connection();
            var command = "Add_INSMOVE";
            Link.send_line(command);
            Link.send_item(itemtarget);
            Link.send_item(this);
            Link.send_int(2);
            Link.check_status();
        }

        /// <inheritdoc />
        public void ShowInstructions(bool show = true)
        {
            Link.check_connection();
            Link.send_line("Prog_ShowIns");
            Link.send_item(this);
            Link.send_int(show ? 1 : 0);
            Link.check_status();
        }

        /// <inheritdoc />
        public void ShowTargets(bool show = true)
        {
            Link.check_connection();
            Link.send_line("Prog_ShowTargets");
            Link.send_item(this);
            Link.send_int(show ? 1 : 0);
            Link.check_status();
        }

        ////////// ADD MORE METHODS

        /// <inheritdoc />
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

        /// <inheritdoc />
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
                programInstruction.IsJointTarget = Link.rec_int() > 0;
                programInstruction.Target = Link.rec_pose();
                programInstruction.Joints = Link.rec_array();
            }

            Link.check_status();
            return programInstruction;
        }

        /// <inheritdoc />
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


        /// <inheritdoc />
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

        /// <inheritdoc />
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
            string readableMsg = Link.rec_line();
            Link.check_status();
            Link.LastStatusMessage = readableMsg;
            UpdateResult updateResult = new UpdateResult(
                result[0], result[1], result[2], result[3], readableMsg);
            return updateResult;
        }


        //// <inheritdoc />
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

        /// <inheritdoc />
        public InstructionListJointsResult GetInstructionListJoints(
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            ListJointsType flags = 0,
            int timeoutSec = 3600,
            double time_step = 0.2)
        {
            var result = new InstructionListJointsResult
            {
                JointList = new List<InstructionListJointsResult.JointsResult>(),
                ErrorCode = InstructionListJoints(out var errorMessage, out var jointList, mmStep, degStep, saveToFile,
                collisionCheck,
                    flags, timeoutSec, time_step),
                ErrorMessage = errorMessage
            };


            var numberOfJoints = GetLink(ItemType.Robot).Joints().Length;
            for (var colId = 0; colId < jointList.Cols; colId++)
            {
                var joints = new double[numberOfJoints];
                for (var rowId = 0; rowId < numberOfJoints; rowId++)
                {
                    joints[rowId] = jointList[rowId, colId];
                }

                var errorCode = (int)jointList[numberOfJoints, colId];
                var simulationErrorFlags = SimulationErrorHandler.GetSimulationErrorFlags(errorCode);
                var linearStep = jointList[numberOfJoints + 1, colId];
                var jointStep = jointList[numberOfJoints + 2, colId];
                var moveId = (int)jointList[numberOfJoints + 3, colId];

                var timeStep = 0.0;

                timeStep = jointList[numberOfJoints + 4, colId];

                var accelerations = new double[numberOfJoints];
                var speeds = new double[numberOfJoints];
                var speedRowId = numberOfJoints + 8;
                var accelerationRowId = numberOfJoints + 8 + numberOfJoints;

                for (var i = 0; i < numberOfJoints; i++)
                {
                    var rowId = speedRowId + i;
                    if (rowId < jointList.Rows)
                    {
                        speeds[i] = jointList[rowId, colId];
                    }
                    rowId = accelerationRowId + i;
                    if (rowId < jointList.Rows)
                    {
                        accelerations[i] = jointList[rowId, colId];
                    }
                }

                result.JointList.Add(
                    new InstructionListJointsResult.JointsResult
                    (
                        moveId,
                        joints,
                        speeds,
                        accelerations,
                        errorCode,
                        simulationErrorFlags,
                        linearStep,
                        jointStep,
                        timeStep
                    )
                );
            }

            return result;
        }

        /// <inheritdoc />
        public int InstructionListJoints(out string errorMsg,
            out Mat jointList,
            double mmStep = 10.0,
            double degStep = 5.0,
            string saveToFile = "",
            CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOff,
            ListJointsType flags = 0,
            int timeoutSec = 3600,
            double time_step = 0.2)
        {
            Link.check_connection();
            Link.send_line("G_ProgJointList");
            Link.send_item(this);
            double[] parameter = {mmStep, degStep, (double) collisionCheck, (double)flags, time_step};
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

        /// <inheritdoc />
        public void SetAccuracyActive(bool accurate = true)
        {
            Link.check_connection();
            Link.send_line("S_AbsAccOn");
            Link.send_item(this);
            Link.send_int(accurate ? 1 : 0);
            Link.check_status();
        }

        /// <inheritdoc />
        public bool AccuracyActive()
        {
            Link.check_connection();
            Link.send_line("G_AbsAccOn");
            Link.send_item(this);
            int result = Link.rec_int();
            Link.check_status();
            return result != 0;
        }

#endregion

    }
}