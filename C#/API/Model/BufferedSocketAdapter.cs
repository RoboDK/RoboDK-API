#region Namespaces

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
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
    /// When the receive function is called, then all the buffered send data is sent in one block.
    /// </summary>
    internal sealed class BufferedSocketAdapter : IDisposable
    {
        #region Fields

        private readonly Socket _socket;
        private bool _disposed;
        private readonly List<byte> _buffer = new List<byte>(2048);

        #endregion

        #region Constructors

        internal BufferedSocketAdapter(Socket s)
        {
            _socket = s;

            // Disable the Nagle Algorithm for this tcp socket.
            _socket.NoDelay = true;
        }

        #endregion

        #region Properties

        public int LocalPort => ((IPEndPoint)_socket.LocalEndPoint).Port;

        internal int ReceiveTimeout
        {
            get => _socket.ReceiveTimeout;
            set => _socket.ReceiveTimeout = value;
        }

        internal int Available => _socket.Available;

        internal bool Connected => _socket.Connected;

        #endregion

        #region Public Methods

        public bool Poll(int microSeconds, SelectMode mode)
        {
            return _socket.Poll(microSeconds, mode);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        #endregion

        #region Internal Methods

        internal void Disconnect(bool reuseSocket)
        {
            _socket.Disconnect(reuseSocket);
        }

        internal int SendData(byte[] data, int len)
        {
            _buffer.AddRange(data.Length == len ? data.ToList() : data.Take(len).ToList());
            if (_buffer.Count > 1024)
            {
                Flush();
            }

            return len;
        }

        internal int SendData(byte[] data)
        {
            return SendData(data, data.Length);
        }

        internal int ReceiveData(byte[] data, int offset, int len)
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

        internal int ReceiveData(byte[] data, int len)
        {
            return ReceiveData(data, 0, len);
        }

        internal void Close()
        {
            _socket.Close();
        }

        #endregion

        #region Private Methods

        private void Flush()
        {
            if (_buffer.Count > 0)
            {
                var n = _socket.Send(_buffer.ToArray(), _buffer.Count, SocketFlags.None);
                Debug.Assert(n == _buffer.Count);
                _buffer.Clear();
            }
        }

        private void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    _socket?.Dispose();
                }

                _disposed = true;
            }
        }

        #endregion
    }
}