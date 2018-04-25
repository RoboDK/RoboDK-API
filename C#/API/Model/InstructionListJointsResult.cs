#region Namespaces

using System.Collections.Generic;

#endregion

namespace RoboDk.API.Model
{
    public class InstructionListJointsResult
    {
        #region Properties

        /// <summary>
        /// Return value of the InstructionListJoints() method.
        /// 0 if success, negative values in case of an error
        /// </summary>
        public int ErrorCode { get; set; }

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
            /// Joint positions (array length = number of axis)
            /// </summary>
            public double[] Joints { get; set; }

            /// <summary>
            /// Various error flags for the calculated joint position.
            /// </summary>
            public ErrorPathType Error { get; set; }

            /// <summary>
            /// True if joint position is causing a collition.
            /// </summary>
            public bool HasCollision => Error.HasFlag(ErrorPathType.Collision);

            /// <summary>
            /// Maximum step in millimeters for linear movements (millimeters)
            /// </summary>
            public double MaxLinearStep { get; set; }

            /// <summary>
            /// Maximum step for joint movements (degrees)
            /// </summary>
            public double MaxJointStep { get; set; }

            public int MoveId { get; set; }

            #endregion
        }

        #endregion
    }
}