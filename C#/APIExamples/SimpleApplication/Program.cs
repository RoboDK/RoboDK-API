using System;
using RoboDk.API;

namespace TesterProject
{
    internal class Program
    {
        // ReSharper disable once UnusedParameter.Local
        private static void Main(string[] args)
        {
            var rdk = new RoboDK();

            // Connect to existing RoboDK or start a new one if RoboDK is not running
            var status = rdk.Connect();
            Console.WriteLine($"Connect status: {status}");

            // close RoboDK
            rdk.CloseRoboDK();
        }
    }
}