using System;
using RoboDk.API;


namespace TesterProject
{
    class Program
    {
        // ReSharper disable once UnusedParameter.Local
        static void Main(string[] args)
        {
			
			var rdk = new RoboDK();
			var status = false;
			//The first connect opens roboDK
			status = rdk.Connect();
			Console.WriteLine($"Connect status: {status}");
            //rdk.CloseStation();
        }
    }
}
