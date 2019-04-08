#region Namespaces

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
            #region Properties

            /// <summary>
            /// Identifies the Target (Frame) to which the position belongs too.
            /// </summary>
            public int MoveId { get; set; }

            /// <summary>
            /// Joint positions (array length = number of axis)
            /// </summary>
            public double[] Joints { get; set; }

            /// <summary>
            /// Joint Speeds (for each joint), empty if ListJointsType flag less than 2
            /// </summary>
            public double[] Speeds { get; set; }

            /// <summary>
            /// Joint Accelerations (for each joint), empty if ListJointsType flag less than 3
            /// </summary>
            public double[] Accelerations { get; set; }

            /// <summary>
            /// Various error flags for the calculated joint position.
            /// </summary>
            public ErrorPathType Error { get; set; }

            /// <summary>
            /// True if joint position is causing a collision.
            /// </summary>
            public bool HasCollision => Error.HasFlag(ErrorPathType.Collision);

            /// <summary>
            /// Time between joint positions
            /// </summary>
            public double TimeStep { get; set; }

            /// <summary>
            /// Maximum step in millimeters for linear movements (millimeters)
            /// </summary>
            public double LinearStep { get; set; }

            /// <summary>
            /// Maximum step for joint movements (degrees)
            /// </summary>
            public double JointStep { get; set; }

            #endregion
        }

        #endregion
    }
}