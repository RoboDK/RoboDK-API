using RoboDk.API;
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;

namespace RoboDKApiWPFApplication
{


    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        RoboDK RDK = null;

        private IntPtr _hWnd;

        [DllImport("user32.dll")]
        public static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);


        public MainWindow()
        {
            InitializeComponent();
        }

        private void EmbedProcessWindow(int processId)
        {
            Process process = Process.GetProcessById(processId);
            if (process != null && !process.HasExited)
            {
                _hWnd = process.MainWindowHandle;
                if (_hWnd != IntPtr.Zero)
                {
                    IntPtr hostHandle = new WindowInteropHelper(this).Handle;

                    SetParent(_hWnd, hostHandle);

                    MoveWindow(_hWnd, (int)border1.Margin.Left, (int)border1.Margin.Top, (int)border1.ActualWidth, (int)border1.ActualHeight, true);
                }
            }
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            RDK = new RoboDK();
            RDK.SetWindowState(RoboDk.API.Model.WindowState.Cinema);

            string processIdStr = RDK.Command("MainProcess_ID");
            int processId = Convert.ToInt32(processIdStr);

            EmbedProcessWindow(processId);

        }

        private void Window_Closing(object sender, CancelEventArgs e)
        {
            if (_hWnd != IntPtr.Zero)
            {
                SetParent(_hWnd, IntPtr.Zero);
                RDK.CloseRoboDK();
                RDK = null;
                _hWnd = IntPtr.Zero;
            }
        }

        private void border1_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            if (_hWnd != IntPtr.Zero)
            {
                MoveWindow(_hWnd, (int)border1.Margin.Left, (int)border1.Margin.Top, (int)border1.ActualWidth, (int)border1.ActualHeight, true);
            }
        }
    }
}
