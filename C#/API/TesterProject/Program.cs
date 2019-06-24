using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using RoboDk.API;


namespace TesterProject
{
    class Program
    {
        static void Main(string[] args)
        {

            RoboDK RDK = new RoboDK
            {
                RoboDKServerStartPort = 20500,
                RoboDKServerEndPort = 20500
            };
            bool status = RDK.Connect();
            Console.WriteLine("Connect status: " + status.ToString());
            Console.WriteLine("Last status message: " + RDK.LastStatusMessage);

            var robot = RDK.GetItemByName("", RoboDk.API.Model.ItemType.Robot);
            robot.Connect();
            //robot.;

            int b = 1;

        }
    }
}
