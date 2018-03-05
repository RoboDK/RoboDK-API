using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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
        /// This is a ratio from [0.00 to 1.00] showing if the path can be fully completed without any problems (1.0 means the path 100% feasible) or valid_ratio is <1.0 if there were problems along the path.
        /// </summary>
        public double ValidRatio { get; private set; }
        /// <summary>
        /// A readable message as a string
        /// </summary>
        public string Message { get; private set; }
    }
}
