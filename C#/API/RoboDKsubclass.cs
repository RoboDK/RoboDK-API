using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SamplePanelRoboDK
{
    public class RoboDKsubclass : RoboDK
    {
        public RoboDKsubclass(string ip, bool hidden, int port, string args, string path="") : base(ip, hidden, port, args, path)
        {

        }

        public void AddTargetJ(Item pgm, string targetName, double[] joints, Item robotBase = null, Item robot = null)
        {
            var target = AddTarget(targetName, robotBase);
            if (target == null)
            {
                throw new Exception($"Create target '{targetName}' failed.");
            }
            target.setVisible(false);
            target.setAsJointTarget();
            target.setJoints(joints);
            if (robot != null)
            {
                target.setRobot(robot);
            }

            //target
            pgm.addMoveJ(target);
        }

        public bool Collision_Line_Check(double[] p1, double[] p2, Mat ref_abs = null)
        {
            Item collided = this.Collision_Line(p1, p2, ref_abs);
            return collided.Valid();
        }



    }
}
