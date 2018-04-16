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
    public class UpdateResult
    {
        public UpdateResult(double instructions, double time, double distance, double ratio, string message="")
        {
            ValidInstructions = instructions;
            ProgramTime = time;
            ProgramDistance = distance;
            ValidRatio = ratio;
            Message = message;
        }

        /// <summary>
        /// The number of valid instructions
        /// </summary>
        public double ValidInstructions { get; private set; }
        /// <summary>
        /// Estimated cycle time (in seconds)
        /// </summary>
        public double ProgramTime { get; private set; }
        /// <summary>
        /// Estimated distance that the robot TCP will travel (in mm)
        /// </summary>
        public double ProgramDistance { get; private set; }
        /// <summary>
        /// This is a ratio from [0.00 to 1.00] showing if the path can be fully completed without 
        /// any problems (1.0 means the path 100% feasible).
        /// ValidRatio is less then 1.0 if there were problems along the path.
        /// </summary>
        public double ValidRatio { get; private set; }
        /// <summary>
        /// A readable message as a string
        /// </summary>
        public string Message { get; private set; }
    }
}
