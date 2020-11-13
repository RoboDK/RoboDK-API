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

namespace RoboDk.API.Model
{
    public static class SimulationErrorHandler
    {
        #region Internal Methods

        /// <summary>
        /// Get SimulationErrorFlags from raw RoboDK Path Simulation Error.
        /// TODO mth: This code should be moved to the RoboDK API after Release 1.2
        /// </summary>
        /// <param name="simulationErrorCode"></param>
        /// <returns></returns>
        public static SimulationErrorFlags GetSimulationErrorFlags(int simulationErrorCode)
        {
            var simulationErrorFlags = SimulationErrorFlags.None;

            var isMotionError = false;
            var isLinearMoveError = false;

            if (simulationErrorCode % 10_000_000 >= 1_000_000)
            {
                // Set Threshold angle to prevent 180deg turns (deg): roboDk.Command("ToleranceTurn180", 0.5);
                // message += "The robot can't make a rotation so close to 180 deg. (the rotation axis is not properly defined). ";
                simulationErrorFlags |= SimulationErrorFlags.AmbiguousAxisRotation;
                isMotionError = true;
            }

            if (simulationErrorCode % 100_000_000 >= 10_000_000 || simulationErrorCode == 2)
            {
                // This is specific to instructionListJoints and it is displayed when the target is not reachable
                //message += "Target not reachable. ";
                simulationErrorFlags |= SimulationErrorFlags.TargetNotReachable;
            }

            if (simulationErrorCode % 1_000_000_000 >= 100_000_000)
            {
                // This specific error can appear if a circular movement is not properly defined (for example, 2 of the 3 points are too close to each other)
                // message += "Invalid circular move, make sure to select 2 different targets defining an arc from the last robot movement. ";
                simulationErrorFlags |= SimulationErrorFlags.InvalidCircularMove;
            }

            if (simulationErrorCode % 1_000_000 >= 100_000)
            {
                // A collision is detected!
                // message += "Collision detected. ";
                simulationErrorFlags |= SimulationErrorFlags.CollisionDetected;
            }

            if (simulationErrorCode % 1_000 >= 100)
            {
                // Wrist singularity (unable to flip joint 5 from positive/negative)
                // message += "Joint 5 crosses 0 degrees. This is a singularity and it is not allowed for a linear move. ";
                // tip_motion = true;
                simulationErrorFlags |= SimulationErrorFlags.WristSingularity;
                isLinearMoveError = true;
            }
            else if (simulationErrorCode % 10_000 >= 1_000)
            {
                // Any flag here may disappear by reducing singularity tolerances:
                // roboDk.Command("ToleranceSingularityWrist ", 2.0); //Threshold angle to avoid singularity for joint 5 (deg)
                // roboDk.Command("ToleranceSingularityElbow ", 3.0); //Threshold angle to avoid singularity for joint 3 (deg)
                // roboDk.Command("ToleranceSingularityBack", 20.0); //Threshold for back/front tolerance, in mm
                if (simulationErrorCode % 10_000 >= 4000)
                {
                    // Front/back singularity
                    //message += "The robot is too close to the front/back singularity (wrist close to axis 1). ";
                    simulationErrorFlags |= SimulationErrorFlags.FrontBackSingularity;
                }
                else if (simulationErrorCode % 10_000 >= 2000)
                {
                    // Elbow singularity
                    //message += "Joint 3 is too close the elbow singularity. ";
                    simulationErrorFlags |= SimulationErrorFlags.ElbowSingularity;
                }
                else
                {
                    // Too close to wrist singularity
                    //message += "Joint 5 is too close to a singularity (0 degrees). ";
                    simulationErrorFlags |= SimulationErrorFlags.NearWristSingularity;
                }

                isMotionError = true;
                isLinearMoveError = true;
            }

            if (simulationErrorCode % 10 > 0)
            {
                // Unable to reach the target using a linear move
                if (simulationErrorCode == 2)
                {
                    //InvalidPosition
                    // a joint move would not be possible
                    //message += "One or more targets are not reachable. ";
                    simulationErrorFlags |= SimulationErrorFlags.TargetNotReachable;
                }
                else
                {
                    //InaccurateDueToLargeAxisMovement -> GenericLinearSimulationError
                    // a joint move would be possible
                    //message += "There is no solution available to complete the path. ";
                    simulationErrorFlags |= SimulationErrorFlags.GenericLinearSimulationError;
                    isLinearMoveError = true;
                }
            }

            if (simulationErrorCode % 100 >= 10)
            {
                //AxisLimit
                //bool has_other_errors = message.Length > 0;
                //message += "The robot can't make a linear movement.";
                //if (!has_other_errors){
                //	message += "The robot can't make a linear movement.";
                //message += "The robot reached its joint limits.";
                //}
                simulationErrorFlags |= SimulationErrorFlags.JointLimitReached;
            }

            if (isMotionError)
            {
                //"You can avoid this warning by changing motion tolerances in Tools-Options-Motion. ";
                simulationErrorFlags |= SimulationErrorFlags.MotionToleranceExceeded;
            }

            if (isLinearMoveError)
            {
                // The robot can't make a linear move. Consider a joint move instead.
                simulationErrorFlags |= SimulationErrorFlags.FrameMoveNotPossible;
            }

            return simulationErrorFlags;
        }

        #endregion
    }
}