// ----------------------------------------------------------------------------------------------------------
// Copyright 2020 - RoboDK Inc. - https://robodk.com/
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

#endregion

namespace RoboDk.API.Model
{
    [Flags]
    public enum SimulationErrorFlags
    {
        None = 0,

        /// <summary>
        /// A movement can't involve an exact rotation of 180 deg around a unique axis.
        /// The rotation is ambiguous and has infinite solutions.
        /// </summary>
        AmbiguousAxisRotation = 1,

        /// <summary>
        /// This is specific to instructionListJoints and it is displayed when the target is not reachable.
        /// </summary>
        TargetNotReachable = 2,

        /// <summary>
        /// This specific error can appear if a circular movement is not properly defined.
        /// For example, 2 of the 3 points are too close to each other.
        /// Make sure to select 2 different targets defining an arc from the last robot movement.
        /// </summary>
        InvalidCircularMove = 4,

        /// <summary>
        /// A collision detected during the move.
        /// </summary>
        CollisionDetected = 8,

        /// <summary>
        /// Wrist singularity (unable to flip joint 5 from positive/negative).
        /// Joint 5 crosses 0 degrees. This is a singularity and it is not allowed for a linear move;
        /// </summary>
        WristSingularity = 16,

        /// <summary>
        /// The robot is too close to the front/back singularity (wrist close to axis 1). 
        /// </summary>
        FrontBackSingularity = 32,

        /// <summary>
        /// Joint 3 is too close the elbow singularity.
        /// </summary>
        ElbowSingularity = 64,

        /// <summary>
        /// Joint 5 is too close to a singularity (0 degrees)
        /// </summary>
        NearWristSingularity = 128,

        /// <summary>
        /// There is no solution available to complete a linear move.
        /// Consider using a joint move.
        /// </summary>
        GenericLinearSimulationError = 256,

        /// <summary>
        /// Linear Move not possible. One of the Axis reached its joint limit.
        /// </summary>
        JointLimitReached = 512,

        /// <summary>
        /// You can avoid this warning by changing motion tolerances in Tools-Options-Motion.
        /// roboDk.Command("ToleranceSingularityWrist ", 2.0); //Threshold angle to avoid singularity for joint 5 (deg)
        /// roboDk.Command("ToleranceSingularityElbow ", 3.0); //Threshold angle to avoid singularity for joint 3 (deg)
        /// roboDk.Command("ToleranceSingularityBack", 20.0); //Threshold for back/front tolerance, in mm
        /// roboDk.Command("ToleranceTurn180", 0.5);
        /// </summary>
        MotionToleranceExceeded = 1024,

        /// <summary>
        /// The robot can't make a linear move. Consider a joint move instead. 
        /// </summary>
        FrameMoveNotPossible = 2048,

        /// <summary>
        /// The path is feasible (no error found), however, the calculation is inaccurate or invalid due to a large axis move. 
        /// Reduce the time step or the robot speed to properly get accurate flags.
        /// This error flag is never combined with other error flags. 
        /// This flag will appear with time based simulations and it means the path is feasible but RoboDK is unable to calculate it with the current time step.
        /// </summary>
        InaccurateDueToLargeAxisMove = 4096
    }
}