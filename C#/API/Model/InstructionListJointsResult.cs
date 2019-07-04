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

            public JointsResult(int moveId, double[] joints, double[] speeds, double[] accelerations, ErrorPathType error, double linearStep, double jointStep, double timeStep)
            {
                MoveId = moveId;
                Joints = CopyArray(joints);
                Speeds = CopyArray(speeds);
                Accelerations = CopyArray(accelerations);
                Error = error;
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

                Error = other.Error;
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
            /// Various error flags for the calculated joint position.
            /// </summary>
            public ErrorPathType Error { get; }

            /// <summary>
            /// True if joint position is causing a collision.
            /// </summary>
            public bool HasCollision => Error.HasFlag(ErrorPathType.Collision);

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