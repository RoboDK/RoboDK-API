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
    /// Modes to use with SetInteractiveMode to change the behavior of the 3D navigation or screen selection.
    /// The following groups of flags can be managed independently:
    /// 3D View: [None, Rectangle, Rotate, Zoom, Pan]. 
    /// Move References: [MoveNone, MoveReferences, MoveTools]
    /// </summary>
    public enum InteractiveType
    {
        /// <summary>
        /// Default 3D mouse behavior. Same as if we selected Escape and the user is ready to select his own choice.
        /// </summary>
        None = 0,

        /// <summary>
        /// Select one or more items (3D view)
        /// </summary>
        Rectangle = 1,

        /// <summary>
        /// Set to rotate the view on click (3D view)
        /// </summary>
        Rotate = 2,

        /// <summary>
        /// Set Zoom mode (3D view)
        /// </summary>
        Zoom = 3,

        /// <summary>
        /// Set Pan mode (3D view)
        /// </summary>
        Pan = 4,

        /// <summary>
        /// Set to move objects (same behavior as holding Alt)
        /// </summary>
        MoveReferences = 5,

        /// <summary>
        /// Set to move objects or tools changing the TCP definition or withoug changing the absolute position of nested references (same behavior as holding Alt+Shift)
        /// </summary>
        MoveTools = 6,

        /// <summary>
        /// Do not move any objects
        /// </summary>
        MoveNone = 7

    }
}
