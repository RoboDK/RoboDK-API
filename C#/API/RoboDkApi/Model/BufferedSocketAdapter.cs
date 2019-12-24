#region Namespaces

using System;
using System.Diagnostics;
using System.Net;
using System.Net.Sockets;

#endregion

namespace RoboDk.API
{
    /// <summary>
    /// Utility class for socket communication.
    /// General RoboDK Protocol:
    ///    - Send command string
    ///    - Send 0 .. n command parameter
    ///    - Receive Result.
    /// The class buffers all the send parameters in a buffer.
    /// When the receive function is called, then all the buffered data is sent in one block.
    /// Unnecessary copying of the data is avoided. The code is faster but less pretty.
    /// Do NOT use multi-threaded.
    /// </summary>
    internal sealed class BufferedSocketAdapter : IDisposable
    {
        #region Constants

        private const int BufferCapacity = 1500; // TCP MTU

        #endregion

        #region Fields

        private readonly Socket _socket;
        private readonly byte[] _bufferArray = new byte[BufferCapacity];
        private int _numberOfBytesInBuffer;
        private bool _disposed;

        #endregion

        #region Constructors

        public BufferedSocketAdapter(Socket s)
        {
            _socket = s;

            // Disable the Nagle Algorithm for this tcp socket.
            _socket.NoDelay = true;
        }

        #endregion

        #region Properties

        public int LocalPort => ((IPEndPoint)_socket.LocalEndPoint).Port;

        public int ReceiveTimeout
        {
            get => _socket.ReceiveTimeout;
            set => _socket.ReceiveTimeout = value;
        }

        public int Available => _socket.Available;

        public bool Connected => _socket.Connected;

        #endregion

        #region Public Methods

        public bool Poll(int microSeconds, SelectMode mode)
        {
            return _socket.Poll(microSeconds, mode);
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _socket?.Dispose();

                _disposed = true;
            }
        }

        public void Disconnect(bool reuseSocket)
        {
            _socket.Disconnect(reuseSocket);
        }

        public void SendData(byte[] data)
        {
            if (IsTooBigForBuffer(data))
            {
                SendLargeDataUnbuffered(data);
            }
            else
            {
                BufferData(data);
            }
        }

        public int ReceiveData(byte[] data, int offset, int len)
        {
            Flush();
            Debug.Assert(offset + len <= data.Length);
            var receivedBytes = 0;
            while (receivedBytes < len)
            {
                var n = _socket.Receive(data, offset + receivedBytes, len - receivedBytes, SocketFlags.None);
                if (n <= 0)
                {
                    // socket closed.
                    return 0;
                }

                receivedBytes += n;
            }

            return receivedBytes;
        }

        public int ReceiveData(byte[] data, int len)
        {
            return ReceiveData(data, 0, len);
        }

        public void Close()
        {
            _socket.Close();
        }

        #endregion

        #region Private Methods

        private bool IsTooBigForBuffer(byte[] data)
        {
            return data.Length > BufferCapacity;
        }

        private bool HasSufficientBuffer(byte[] data)
        {
            var freeBuffer = BufferCapacity - _numberOfBytesInBuffer;
            return data.Length <= freeBuffer;
        }

        private void SendLargeDataUnbuffered(byte[] data)
        {
            Flush(); // This maintains the correct order.
            SendToSocket(data, data.Length);
        }

        private void BufferData(byte[] data)
        {
            Debug.Assert(data.Length <= BufferCapacity); // Too large data must be handled by caller.

            if (HasSufficientBuffer(data))
            {
                Array.Copy(data, 0, _bufferArray, _numberOfBytesInBuffer, data.Length);
                _numberOfBytesInBuffer += data.Length;
            }
            else
            {
                Flush(); // This maintains the correct order and provides enough buffer.
                BufferData(data);
            }
        }

        private void Flush()
        {
            if (_numberOfBytesInBuffer > 0)
            {
                SendToSocket(_bufferArray, _numberOfBytesInBuffer);
                _numberOfBytesInBuffer = 0;
            }
        }

        private void SendToSocket(byte[] data, int count)
        {
            var n = _socket.Send(data, count, SocketFlags.None);
            Debug.Assert(n == count);
        }

        #endregion
    }
}