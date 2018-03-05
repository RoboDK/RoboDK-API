using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RoboDk.API.Model
{
    public class ProgramInstruction
    {
        public string Name { get; set; }
        public InstructionType InstructionType { get; set; }

        // The following parameter are only Valid if InstructionType is InstructionType.Move
        // TODO: Subclase ProgramMoveInstruction

        public MoveType MoveType { get; set; }
        public bool IsJointTarget { get; set; }
        public Mat Target { get; set; }
        public double[] Joints { get; set; }
    }
}
