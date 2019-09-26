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
			
			RoboDK RDK = new RoboDK();
			bool status = false;
			//The first connect opens roboDK
			status = RDK.Connect();
			Console.WriteLine("Connect status: " + status.ToString());
            int b = 1;
            //RDK.CloseStation();
        }
    }
}
