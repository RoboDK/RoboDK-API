using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RoboDk.API
{
    public enum DisplayRefType
    {
        DEFAULT = -1,
        NONE = 0,
        TX = 0b001,
        TY = 0b010,
        TZ = 0b100,
        RX = 0b001000,
        RY = 0b010000,
        RZ = 0b100000,
        PXY = 0b001000000,
        PXZ = 0b010000000,
        PYZ = 0b100000000
    }
}
