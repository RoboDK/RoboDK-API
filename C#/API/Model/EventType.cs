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



namespace RoboDk.API.Model
{
    /// <summary>
    /// Script execution Mode 
    /// </summary>
    public enum EventType
    {
        NoEvent = 0,

        /// <summary>
        /// One object (Item) has been selected or deselected from the tree
        /// </summary>
        SelectionTreeChanged = 1,

        /// <summary>
        /// Obsolete after RoboDK v4.2.0: Use ItemMovedPose instead. The location of an object, robot or reference frame was moved
        /// </summary>
        ItemMoved = 2,

        /// <summary>
        /// A reference frame has been picked, or left clicked (any tool, reference frame or object)
        /// </summary>
        ReferencePicked = 3,

        /// <summary>
        /// A reference frame has been released (any tool or reference frame or object)
        /// </summary>
        ReferenceReleased = 4,

        /// <summary>
        /// A tool has changed (the TCP has been modified)
        /// </summary>
        ToolModified = 5,

        /// <summary>
        /// A new program to follow the ISO 9283 cube has been created
        /// </summary>
        IsoCubeCreated = 6,

        /// <summary>
        /// One object (Item) has been selected or deselected from 3D view
        /// </summary>
        Selection3DChanged = 7,

        /// <summary>
        /// The user moved the position of the camera in the 3D view (ViewPose)
        /// </summary>
        Moved3DView = 8,

        /// <summary>
        /// The Robot has changed it's position
        /// </summary>
        RobotMoved = 9,

        /// <summary>
        /// Key pressed event.
        /// More information about the event parameter can be found here: <see cref="KeyPressedEventResult"/>
        /// </summary>
        KeyPressed = 10,

        /// <summary>
        /// The location of an object, robot or reference frame was moved, including the relative pose.
        /// </summary>
        ItemMovedPose = 11,

        /// <summary>
        /// The collision map changed: collision checking has changed for one or more pairs of objects.
        /// </summary>
        CollisionMapChanged = 12,

        /// <summary>
        /// The collision map is too large (there are too many objects) and it won't be remembered.
        /// </summary>
        CollisionMapTooLarge = 13,

        /// <summary>
        /// A new measurement was obtained using a measurement system when calibrating a robot (3D or 6D measurement system)
        /// </summary>
        NewMeasurement = 14,

        /// <summary>
        /// An object in the 3D view was clicked on (right click, left click or double click), this is not triggered when we deselect an item (use Selection3DChanged instead to have more complete information)
        /// </summary>
        Selection3DClick = 15,
		
		/// <summary>
        /// The state of one or more items changed in the tree (parent/child relationship, added/removed items or instructions, changed the active station). Use this event to know if the tree changed and had to be re-rendered (Requires RoboDK v5.6.3 or later).
        /// </summary>
        ItemChanged = 16,
		
		/// <summary>
        /// The name of an item changed (Requires RoboDK v5.6.3 or later).
        /// </summary>
        ItemRenamed = 17,
		
		/// <summary>
        /// The visibility state of an item changed (Requires RoboDK v5.6.3 or later).
        /// </summary>
        ItemVisibility = 18,
		
		/// <summary>
        /// The active station changed, a new RDK file was loaded (Requires RoboDK v5.6.3 or later).
        /// </summary>
        StationChanged = 19,
		
		/// <summary>
        /// The program slider was opened, changed or closed (Requires RoboDK v5.6.4 or later).
        /// </summary>
        ProgsliderChanged = 20,
		
		/// <summary>
        /// The index of a program slider changed (Requires RoboDK v5.6.4 or later).
        /// </summary>
		ProgsliderSet = 21
    }
}


