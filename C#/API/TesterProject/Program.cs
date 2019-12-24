namespace TesterProject
{
    using RoboDk.API;
    using System;

    class Program
    {
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
