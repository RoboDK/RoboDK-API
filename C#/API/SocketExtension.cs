using System.Diagnostics;
using System.Net.Sockets;

namespace RoboDk.API
{
    /// <summary>
    /// Utility class for socket communication. All Sending/receiving should be done with this utility.
    /// </summary>
    internal static class SocketExtension
    {
        internal static int SendData(this Socket s, byte[] data, int len, SocketFlags flags)
        {
            var n = s.Send(data, len, flags);
            Debug.Assert(n == len);
            return n;
        }

        internal static int SendData(this Socket s, byte[] data)
        {
            return s.SendData(data, data.Length, SocketFlags.None);
        }

        internal static int ReceiveData(this Socket s, byte[] data, int offset, int len, SocketFlags flags)
        {
            Debug.Assert((offset + len) <= data.Length);
            var receivedBytes = 0;
            while (receivedBytes < len)
            {
                var n = s.Receive(data, offset + receivedBytes, len - receivedBytes, flags);
                if (n <= 0)
                {
                    // socket closed.
                    return 0;
                }
                receivedBytes += n;
            }

            return receivedBytes;
        }

        internal static int ReceiveData(this Socket s, byte[] data, int len, SocketFlags flags)
        {
            return s.ReceiveData(data, 0, len, flags);
        }
    }
}