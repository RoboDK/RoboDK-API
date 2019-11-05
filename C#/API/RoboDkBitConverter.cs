using System;

namespace RoboDk.API
{
    /// <summary>
    /// Delegates to BitConverter and handles the conversion of the byte order for RoboDk.
    /// Do NOT use multi-threaded.
    /// </summary>
    internal class RoboDkBitConverter
    {
        // We do not want to reverse the byte order in the received array.
        // It may cause surprising side effects, e.g. not idempotent.
        // But we do not want to allocate a new array neither.
        // Solution: Allocate a buffer only once, copy the relevant data into it and reverse there.
        private readonly byte[] _buffer = new byte[sizeof(double)];

        public byte[] GetBytes(double value)
        {
            var bytes = BitConverter.GetBytes(value);
            Reverse(bytes);
            return bytes;
        }

        public byte[] GetBytes(int value)
        {
            var bytes = BitConverter.GetBytes(value);
            Reverse(bytes);
            return bytes;
        }

        public byte[] GetBytes(long value)
        {
            var bytes = BitConverter.GetBytes(value);
            Reverse(bytes);
            return bytes;
        }

        public byte[] GetBytes(ulong value)
        {
            var bytes = BitConverter.GetBytes(value);
            Reverse(bytes);
            return bytes;
        }

        public double ToDouble(byte[] value, int startIndex)
        {
            Array.Copy(value, startIndex, _buffer, 0, sizeof(double));
            Reverse(_buffer, 0, sizeof(double));
            return BitConverter.ToDouble(_buffer, 0);
        }

        public int ToInt32(byte[] value, int startIndex)
        {
            Array.Copy(value, startIndex, _buffer, 0, sizeof(int));
            Reverse(_buffer, 0, sizeof(int));
            return BitConverter.ToInt32(_buffer, 0);
        }

        public long ToInt64(byte[] value, int startIndex)
        {
            Array.Copy(value, startIndex, _buffer, 0, sizeof(long));
            Reverse(_buffer, 0, sizeof(long));
            return BitConverter.ToInt64(_buffer, 0);
        }

        private void Reverse(byte[] bytes)
        {
            Reverse(bytes, 0, bytes.Length);
        }

        private void Reverse(byte[] bytes, int startIndex, int length)
        {
            // Same as Array.Reverse but with better performance

            var bottomUpIndex = startIndex;
            var topDownIndex = startIndex + length - 1;
            while (bottomUpIndex < topDownIndex)
            {
                var temp = bytes[bottomUpIndex];
                bytes[bottomUpIndex] = bytes[topDownIndex];
                bytes[topDownIndex] = temp;
                --topDownIndex;
                ++bottomUpIndex;
            }
        }
    }
}
