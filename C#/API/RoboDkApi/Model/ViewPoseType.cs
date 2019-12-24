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
    /// Type of the view pose: Isometric, Top, Front, Back, ...
    /// </summary>
    public enum ViewPoseType
    {
        /// <summary>
        /// Currently active view pose (do not calculate)
        /// </summary>
        ActiveView = 0,

        /// <summary>
        /// Isometric View pose
        /// </summary>
        Isometric = 1,

        /// <summary>
        /// Front view pose
        /// </summary>
        Front = 2,

        /// <summary>
        /// Top view pose
        /// </summary>
        Top = 3,

        /// <summary>
        /// Right view pose
        /// </summary>
        Right = 4,

        /// <summary>
        /// Left view pose
        /// </summary>
        Left = 5,

        /// <summary>
        /// Back view pose
        /// </summary>
        Back = 6,

        /// <summary>
        /// Fit all pose (do not change rotation)
        /// </summary>
        FitAll = 7
    }
}

