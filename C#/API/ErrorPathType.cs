using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RoboDk.API
{
    public enum ErrorPathType
    {
        KINEMATIC = 0b001,          // One or more points is not reachable
        PATH_LIMIT = 0b010,         // The path reaches the limit of joint axes
        PATH_SINGULARITY = 0b100,   // The robot reached a singularity point
        COLLISION = 0b100000        // Collision detected
    }
}
