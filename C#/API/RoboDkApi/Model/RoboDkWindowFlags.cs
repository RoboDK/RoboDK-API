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
    /// RoboDK Window Flags
    /// </summary>
    [Flags]
    public enum WindowFlags
    {
        TreeActive = 1,
        View3Dactive = 2,
        LeftClick = 4,
        RightClick = 8,
        DoubleClick = 16,
        MenuActive = 32,
        MenuFileActive = 64,
        MenuEditActive = 128,
        MenuProgramActive = 256,
        MenuToolsActive = 512,
        MenuUtilitiesActive = 1024,
        MenuConnectActive = 2048,
        WindowKeysActive = 4096,
        TreeVisible = 8192,
        ReferencesVisible = 16384,
        None = 0,
        All = 0xFFFF,
        MenuActiveAll = MenuActive | MenuFileActive | MenuEditActive | MenuProgramActive |
                        MenuToolsActive | MenuUtilitiesActive | MenuConnectActive
    }
}

