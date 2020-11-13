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
using System.Collections.Generic;

#endregion

namespace RoboDk.API.Model
{
    /// <summary>
    /// Encapsulates the InstructionListJoints() result.
    /// </summary>
    public class InstructionListJointsResult
    {
        #region Properties

        /// <summary>
        /// Status is 0 if no problems are found. Otherwise it returns the number of instructions that can be successfully executed. 
        /// If status is negative it means that one or more targets are not properly defined (missing target item in an instruction).
        /// </summary>
        public int ErrorCode { get; set; }

        /// <summary>
        /// Human readable error message (if any)
        /// </summary>
        public string ErrorMessage { get; set; }

        /// <summary>
        /// List of joint(axis) positions. 
        /// </summary>
        public List<JointsResult> JointList { get; set; }

        #endregion

        #region Embedded Classes

        public class JointsResult
        {
            #region Constructors

            private static double[] CopyArray(double[] source)
            {
                var destination = new double[source.Length];
                Array.Copy(source, destination, source.Length);
                return destination;
            }

            public JointsResult(
                int moveId,
                double[] joints,
                double[] speeds,
                double[] accelerations,
                int pathSimulationErrorCode,
                SimulationErrorFlags simulationErrorFlags,
                double linearStep,
                double jointStep,
                double timeStep)
            {
                MoveId = moveId;
                Joints = CopyArray(joints);
                Speeds = CopyArray(speeds);
                Accelerations = CopyArray(accelerations);
                SimulationErrorFlags = simulationErrorFlags;
                PathSimulationErrorCode = pathSimulationErrorCode;
                LinearStep = linearStep;
                JointStep = jointStep;
                TimeStep = timeStep;
            }

            public JointsResult(JointsResult other)
            {
                MoveId = other.MoveId;

                Joints = new double[other.Joints.Length];
                Array.Copy(other.Joints, Joints, other.Joints.Length);

                Speeds = new double[other.Speeds.Length];
                Array.Copy(other.Speeds, Speeds, other.Speeds.Length);

                Accelerations = new double[other.Accelerations.Length];
                Array.Copy(other.Accelerations, Accelerations, other.Accelerations.Length);

                SimulationErrorFlags = other.SimulationErrorFlags;
                PathSimulationErrorCode = other.PathSimulationErrorCode;
                TimeStep = other.TimeStep;
                LinearStep = other.LinearStep;
                JointStep = other.JointStep;
            }

            #endregion

            #region Properties

            /// <summary>
            /// Identifies the Target (Frame) to which the position belongs too.
            /// </summary>
            public int MoveId { get; }

            /// <summary>
            /// Joint positions (array length = number of axis)
            /// </summary>
            public double[] Joints { get; }

            /// <summary>
            /// Joint Speeds (for each joint), empty if ListJointsType flag less than 2
            /// </summary>
            public double[] Speeds { get; }

            /// <summary>
            /// Joint Accelerations (for each joint), empty if ListJointsType flag less than 3
            /// </summary>
            public double[] Accelerations { get; }

            /// <summary>
            /// Raw Error Code (PathSimulationErrorCode) translated into SimulationErrorFlags.
            /// </summary>
            public SimulationErrorFlags SimulationErrorFlags { get; }

            /// <summary>
            /// Simulation Error Code (raw value returned by RoboDK)
            /// </summary>
            public int PathSimulationErrorCode { get; }

            /// <summary>
            /// True if joint position is causing a collision.
            /// </summary>
            public bool HasCollision => SimulationErrorFlags.HasFlag(SimulationErrorFlags.CollisionDetected);

            /// <summary>
            /// Time between joint positions
            /// </summary>
            public double TimeStep { get; }

            /// <summary>
            /// Maximum step in millimeters for linear movements (millimeters)
            /// </summary>
            public double LinearStep { get; }

            /// <summary>
            /// Maximum step for joint movements (degrees)
            /// </summary>
            public double JointStep { get; }

            #endregion
        }

        #endregion
    }
}