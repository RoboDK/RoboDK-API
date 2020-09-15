namespace RoboDk.API.Model
{
    public class RobotConnectionParameter
    {
        public RobotConnectionParameter(string robotIp, int port, string remotePath, string ftpUser, string ftpPass)
        {
            RobotIp = robotIp;
            Port = port;
            RemotePath = remotePath;
            FtpUser = ftpUser;
            FtpPass = ftpPass;
        }

        public string RobotIp { get; }
        public int Port { get; }
        public string RemotePath { get; }
        public string FtpUser { get; }
        public string FtpPass { get; }
    }
}