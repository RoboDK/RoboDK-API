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
    /// Type of information returned by InstructionListJoints and GetInstructionListJoints
    /// </summary>
    public enum ListJointsType
    {
        /// <summary>
        /// Same result as Position (fastest)
        /// </summary>
        Any = 0,

        /// <summary>
        /// Return the joints position. The returned columns are organized in the following way:
        /// [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID]
        /// </summary>
        Position = 1,

        /// <summary>
        /// Include the speed information (also includes the time). The returned columns are organized in the following way:
        /// [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn] 
        /// </summary>
        Speed = 2,

        /// <summary>
        /// Return the speed and acceleration information (also includes the time). The returned columns are organized in the following way:
        /// [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn,   Accel_J1, Accel_J2, ..., Accel_Jn]
        /// </summary>
        SpeedAndAcceleration = 3,

        /// <summary>
        /// Make the result time-based so that the interval between joint values is provided at constant time steps
        /// </summary>
        TimeBased = 4,

        /// <summary>
        /// Make the result time-based so that the interval between joint values is provided at constant time steps. Speed and acceleration data is ignored.
        /// </summary>
        TimeBasedPosition = 5
    }
}


