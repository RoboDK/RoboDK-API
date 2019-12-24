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

using System;

namespace RoboDk.API.Model
{
    /// <summary>
    /// Defines which parts an objects are visible.
    /// <see cref="IItem.SetVisible(bool, VisibleRefType)"/>
    /// </summary>
    [Flags]
    public enum VisibleRefType
    {
        /// <summary>
        /// Default behavior: for objects, the reference is visible if the object is visible. For robots it does not alter the display state of the robot links.
        /// </summary>
        Default = -1,

        /// <summary>
        /// Visible.
        /// </summary>
        On = 1,

        /// <summary>
        /// Not visible.
        /// </summary>
        Off = 0,

        /// <summary>
        /// Do not show robot links or reference frames.
        /// </summary>
        RobotNone = 0,

        /// <summary>
        /// Display the robot tool flange (reference frame). The robot flange can be used to drag the robot from the tool flange.
        /// </summary>
        RobotFlange = 0x01,

        /// <summary>
        /// Display the 3D geometry attached to the robot base.
        /// </summary>
        RobotAxis_Base_3D = 0x01 << 1,

        /// <summary>
        /// Display the reference frame attached to the robot base. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_Base_Ref = 0x01 << 2,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 1.
        /// </summary>
        RobotAxis_1_3D = 0x01 << 3,

        /// <summary>
        /// Display the reference frame attached to the robot axis 1. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_1_Ref = 0x01 << 4,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 2.
        /// </summary>
        RobotAxis_2_3D = 0x01 << 5,

        /// <summary>
        /// Display the reference frame attached to the robot axis 2. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_2_Ref = 0x01 << 6,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 3.
        /// </summary>
        RobotAxis_3_3D = 0x01 << 7,

        /// <summary>
        /// Display the reference frame attached to the robot axis 3. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_3_Ref = 0x01 << 8,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 4.
        /// </summary>
        RobotAxis_4_3D = 0x01 << 9,

        /// <summary>
        /// Display the reference frame attached to the robot axis 4. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_4_Ref = 0x01 << 10,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 5.
        /// </summary>
        RobotAxis_5_3D = 0x01 << 11,

        /// <summary>
        /// Display the reference frame attached to the robot axis 5. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_5_Ref = 0x01 << 12,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 6.
        /// </summary>
        RobotAxis_6_3D = 0x01 << 13,

        /// <summary>
        /// Display the reference frame attached to the robot axis 6. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_6_Ref = 0x01 << 14,

        /// <summary>
        /// Display the 3D geometry attached to the robot axis 7.
        /// </summary>
        RobotAxis_7_3D = 0x01 << 15,

        /// <summary>
        /// Display the reference frame attached to the robot axis 7. The reference frame is only visible when the geometry is visible.
        /// </summary>
        RobotAxis_7_Ref = 0x01 << 16,

        /// <summary>
        /// Set the robot to be displayed in the default state (show the geometry, hide the internal links).
        /// </summary>
        RobotDefault = 0x2AAAAAAB,

        /// <summary>
        /// Display all robot links and references.
        /// </summary>
        RobotAll = 0x7FFFFFFF,

        /// <summary>
        /// Display all robot references. Important: The references are only displayed if the geometry is visible. Add apropriate flags to display the geometry and the reference frame.
        /// </summary>
        RobotAllRefs = 0x15555555
    }
}
