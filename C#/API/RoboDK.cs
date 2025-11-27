// ----------------------------------------------------------------------------------------------------------
// Copyright 2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ----------------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------------
// This file (RoboDK.cs) implements the RoboDK API for C#
// This file defines the following classes:
//     Mat: Matrix class, useful pose operations
//     RoboDK: API to interact with RoboDK
//     RoboDK.IItem: Any item in the RoboDK station tree
//
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the RoboDK() object (such as RoboDK.GetItem() method) 
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API for Python here:
//     https://robodk.com/doc/en/CsAPI/index.html
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
// This library includes the mathematics to operate with homogeneous matrices for robotics.
// ----------------------------------------------------------------------------------------------------------

#region Namespaces

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
#if NET45
using System.Windows.Media;
#else
using System.Drawing;
#endif
using Microsoft.Win32;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;
// ReSharper disable UnusedMember.Global

#endregion

/// <summary>
///     The RoboDK API namespace contains classes and interfaces to interact with RoboDK.
/// </summary>
namespace RoboDk.API
{
    /// <summary>
    ///     The RoboDK API class is the link that allows you to communicate with RoboDK.
    ///     Any interaction is made through \"items\" (IItem() objects). An item is an object in the
    ///     RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
    /// </summary>
    public class RoboDK : IRoboDK, IDisposable
    {
        public enum ConnectionType
        {
            None,

            // API connection
            Api = 1,

            // Event connection
            Event = 2
        }

        #region Constants

        // Station parameters request
        public const string PATH_OPENSTATION = "PATH_OPENSTATION";
        public const string FILE_OPENSTATION = "FILE_OPENSTATION";
        public const string PATH_DESKTOP = "PATH_DESKTOP";

        #endregion

        #region Fields

        private bool _disposed;

        private readonly RoboDkBitConverter _bitConverter = new RoboDkBitConverter();
        private BufferedSocketAdapter _bufferedSocket;
        private readonly RoboDkCommandLineParameter _commandLineParameter;
        private ConnectionType _connectionType;
		private List<int> _eventFilter;
        private int _roboDKServerStartPort;


        #endregion

        #region Constructors

        /// <summary>
        /// Creates a link with RoboDK
        /// </summary>
        public RoboDK()
        {
            _commandLineParameter = new RoboDkCommandLineParameter();

            _connectionType = ConnectionType.Api;

            _eventFilter = new List<int>();

            Name = "RoboDk API Client";
            CustomCommandLineArgumentString = "";
            ApplicationDir = "";

            DefaultSocketTimeoutMilliseconds = 10 * 1000;

            SafeMode = true;
            AutoUpdate = false;

            RoboDKServerIpAddress = "localhost";

            // Default RoboDK Port Range: 20500 .. 20502
            RoboDKServerStartPort = RoboDkCommandLineParameter.DefaultApiServerPort;
            RoboDKServerEndPort = RoboDKServerStartPort + 2;

            RoboDKBuild = 0;
        }

        #endregion

        #region Properties

        public int DefaultApiServerPort => RoboDkCommandLineParameter.DefaultApiServerPort;

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.HideWindowsWhileLoadingNcFile"/>
        /// </summary>
        public bool HideWindowsWhileLoadingNcFile
        {
            set => _commandLineParameter.HideWindowsWhileLoadingNcFile = value;
            get => _commandLineParameter.HideWindowsWhileLoadingNcFile;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.LoadSettingsFromFile"/>
        /// </summary>
        public string LoadSettingsFromFile
        {
            set => _commandLineParameter.LoadSettingsFromFile = value;
            get => _commandLineParameter.LoadSettingsFromFile;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.HideReferenceFrames"/>
        /// </summary>
        public bool HideReferenceFrames
        {
            set => _commandLineParameter.HideReferenceFrames = value;
            get => _commandLineParameter.HideReferenceFrames;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.TreeState"/>
        /// </summary>
        public int TreeState
        {
            set => _commandLineParameter.TreeState = value;
            get => _commandLineParameter.TreeState;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.NoUserInterface"/>
        /// </summary>
        public bool NoUserInterface
        {
            set => _commandLineParameter.NoUserInterface = value;
            get => _commandLineParameter.NoUserInterface;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.ExitRoboDkAfterClosingLastApiConnection"/>
        /// </summary>
        public bool ExitRoboDkAfterClosingLastApiConnection
        {
            set => _commandLineParameter.ExitRoboDkAfterClosingLastApiConnection = value;
            get => _commandLineParameter.ExitRoboDkAfterClosingLastApiConnection;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.DoNotUseSettingsFile"/>
        /// </summary>
        public bool DoNotUseSettingsFile
        {
            set => _commandLineParameter.DoNotUseSettingsFile = value;
            get => _commandLineParameter.DoNotUseSettingsFile;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.DoNotUseRecentlyUsedFileList"/>
        /// </summary>
        public bool DoNotUseRecentlyUsedFileList
        {
            set => _commandLineParameter.DoNotUseRecentlyUsedFileList = value;
            get => _commandLineParameter.DoNotUseRecentlyUsedFileList;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.StartNewInstance"/>
        /// </summary>
        public bool StartNewInstance
        {
            set => _commandLineParameter.StartNewInstance = value;
            get => _commandLineParameter.StartNewInstance;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.NoCommunicationToRoboDkServer"/>
        /// </summary>
        public bool NoCommunicationToRoboDkServer
        {
            set => _commandLineParameter.NoCommunicationToRoboDkServer = value;
            get => _commandLineParameter.NoCommunicationToRoboDkServer;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.NoDebugOutput"/>
        /// </summary>
        public bool NoDebugOutput
        {
            set => _commandLineParameter.NoDebugOutput = value;
            get => _commandLineParameter.NoDebugOutput;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.StartHidden"/>
        /// </summary>
        public bool StartHidden
        {
            set => _commandLineParameter.StartHidden = value;
            get => _commandLineParameter.StartHidden;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.NoSplash"/>
        /// </summary>
        public bool NoSplash
        {
            set => _commandLineParameter.NoSplash = value;
            get => _commandLineParameter.NoSplash;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.NoShow"/>
        /// </summary>
        public bool HideWindowWhileLoadingFiles
        {
            set => _commandLineParameter.NoShow = value;
            get => _commandLineParameter.NoShow;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.Hidden"/>
        /// </summary>
        public bool Hidden
        {
            set => _commandLineParameter.Hidden = value;
            get => _commandLineParameter.Hidden;
        }

        /// <summary>
        /// <see cref="RoboDkCommandLineParameter.Logfile"/>
        /// </summary>
        public string Logfile
        {
            set => _commandLineParameter.Logfile = value;
            get => _commandLineParameter.Logfile;
        }

        /// <summary>
        /// Name of the RoboDK instance.
        /// In case of multiple instances the name can help to identify the instance.
        /// </summary>
        public string Name { get; set; }

        public Func<IItem, IItem> ItemInterceptFunction { set; get; } = item => item;

        /// <summary>
        /// Default Socket send / receive timeout in milliseconds: 10 seconds
        /// </summary>
        public int DefaultSocketTimeoutMilliseconds { get; set; }

        /// <summary>
        /// If True checks that provided items exist in memory and poses are homogeneous
        /// </summary>
        public bool SafeMode { get; set; }

        /// <summary>
        /// If AUTO_UPDATE is 1, updating and rendering objects the 3D the scene will be delayed until 100 ms
        /// after the last call.
        /// This value can be changed in Tools-Options-Other-API Render delay,
        /// or using the RoboDK.Command('AutoRenderDelay', value) and RoboDK.Command('AutoRenderDelayMax', value)
        /// </summary>
        public bool AutoUpdate { get; set; }

        /// <summary>
        /// The custom command line options will be appended to the standard command line argument string
        /// returned by RoboDkCommandLineParameter.CommandLineArgumentString.
        /// See https://robodk.com/doc/en/RoboDK-API.html#CommandLine
        /// </summary>
        public string CustomCommandLineArgumentString { get; set; }

        /// <summary>
        /// Defines the RoboDK Simulator IP Address.
        /// Default: localhost (Client and RoboDK Server runs on same computer)
        /// </summary>
        public string RoboDKServerIpAddress { get; set; }

        /// <summary>
        /// Port to start looking for a RoboDK connection.
        /// </summary>
        public int RoboDKServerStartPort
        {
            get => _roboDKServerStartPort;
            set
            {
                _roboDKServerStartPort = value;
                RoboDKServerEndPort = value;
            }
        }

        /// <summary>
        /// Port to stop looking for a RoboDK connection.
        /// </summary>
        public int RoboDKServerEndPort { get; set; }

        /// <summary>
        /// The RoboDK build id and is used for version checking. This value always increases with new versions
        /// </summary>
        public int RoboDKBuild { get; set; }

        /// <summary>
        /// RoboDK API protocol version.
        /// </summary>
        public int ApiVersion { get; private set; }

        /// <summary>
        /// RoboDK Event protocol version.
        /// </summary>
        public int EventChannelVersion { get; set; }


        /// <summary>
        /// TCP Server Port to which this instance is connected to.
        /// </summary>
        public int RoboDKServerPort { get; private set; }

        /// <summary>
        /// TCP Client Port
        /// </summary>
        public int RoboDKClientPort => _bufferedSocket.LocalPort;

        internal int ReceiveTimeout
        {
            get => _bufferedSocket.ReceiveTimeout;
            set => _bufferedSocket.ReceiveTimeout = value;
        }

        /// <summary>
        /// RoboDK.exe process.
        /// </summary>
        public Process Process { get; private set; }

        public string LastStatusMessage { get; set; } // Last status message

        /// <summary>
        /// Filepath to the RoboDK.exe.
        /// Typically C:/RoboDK/bin/RoboDK.exe. 
        /// Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
        /// </summary>
        public string ApplicationDir { get; set; }

        #endregion

        #region Static Methods
        /// <summary>
        /// Return the list of recently opened files
        /// </summary>
        /// <param name="extensionFilter"></param>
        /// <returns></returns>
        public static List<string> RecentFiles(string extensionFilter = "")
        {
            var iniFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), @"RoboDK\RecentFiles.ini");
            var str = "";
            if (File.Exists(iniFile))
            {
                foreach (var line in File.ReadLines(iniFile))
                {
                    if (line.Contains("RecentFileList="))
                    {
                        str = line.Remove(0, "RecentFileList=".Length);
                        break;
                    }
                }
            }
            var rdkList = new List<string>();
            var readList = str.Split(',');
            foreach (var st in readList)
            {
                var st2 = st.Trim();
                if (st2.Length < 5) // file name should be name.abc
                {
                    continue;
                }
                if (extensionFilter.Length == 0 || st2.ToLower().EndsWith(extensionFilter.ToLower()))
                {
                    rdkList.Add(st2);
                }

            }
            return rdkList;
        }

        /// <summary>
        /// Check if RoboDK was installed from RoboDK's official installer
        /// </summary>
        /// <returns></returns>
        public static bool RoboDKInstallFound()
        {
            return RoboDKInstallPath() != null;
        }

        /// <summary>
        /// Return the RoboDK install path according to the registry (saved by RoboDK installer)
        /// </summary>
        /// <returns></returns>
        public static string RoboDKInstallPath()
        {
            using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
            using (var regKey = baseKey.OpenSubKey(@"SOFTWARE\RoboDK"))
            {
                // key now points to the 64-bit key
                var installPath = regKey?.GetValue("INSTDIR").ToString();
                if (!string.IsNullOrEmpty(installPath))
                {
                    var s = Path.Combine(installPath, "bin\\RoboDK.exe");
                    return s;
                }
            }

            const string defaultPath = @"C:\RoboDK\bin\RoboDK.exe";
            return File.Exists(defaultPath) ? defaultPath : null;
        }
        #endregion

        #region Public Methods

        /// <summary>
        /// Open a new additional RoboDK Link to the same already existing RoboDK instance.
        /// NOTE: Use IItem.Clone() to use an already existing item on the new RoboDk connection.
        /// </summary>
        /// <returns>New RoboDK Link</returns>
        public IRoboDK CloneRoboDkConnection(ConnectionType connectionType = ConnectionType.Api)
        {
            var rdk = new RoboDK
            {
                RoboDKServerStartPort = this.RoboDKServerStartPort,
                RoboDKServerEndPort = this.RoboDKServerEndPort,
                Name = this.Name,
                Process = this.Process,
                ItemInterceptFunction = this.ItemInterceptFunction,
                _connectionType = connectionType,
				_eventFilter = this._eventFilter
            };
            rdk.Connect();
            return rdk;
        }

        // Implement IDisposable.
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <inheritdoc />
        public bool Connected()
        {
            if (_disposed)
            {
                throw new ObjectDisposedException(this.GetType().FullName);
            }

            //return _socket.Connected;//does not work well
            // See:
            // https://stackoverflow.com/questions/2661764/how-to-check-if-a-socket-is-connected-disconnected-in-c
            if (_bufferedSocket == null)
            {
                return false;
            }

            var part1 = _bufferedSocket.Poll(10000, SelectMode.SelectRead);
            var part2 = _bufferedSocket.Available == 0;

            // s.Poll returns true if:
            //  - connection is closed, reset, terminated or pending(meaning no active connection)
            //  - connection is active and there is data available for reading
            // s.Available returns number of bytes available for reading
            // if both are true:
            //  - there is no data available to read so connection is not active

            var rtc = !(part1 && part2);

            return rtc;
        }

        /// <inheritdoc />
        public void Disconnect()
        {
            _bufferedSocket?.Dispose();
            _bufferedSocket = null;
        }

        /// <inheritdoc />
        public bool Connect()
        {
            if (RoboDKServerEndPort < RoboDKServerStartPort)
            {
                throw new RdkException($"RoboDKServerEndPort:{RoboDKServerEndPort} < RoboDKServerStartPort:{RoboDKServerStartPort}");
            }

            var connected = StartNewInstance ? StartNewRoboDkInstance() : TryConnectToExistingRoboDkInstance();

            if (connected)
            {
                connected = VerifyConnection();
                _bufferedSocket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;

            }

            if (!connected)
            {
                _bufferedSocket.Dispose();
                _bufferedSocket = null;
                if (Process != null)
                {
                    Process.Kill();
                    Process.WaitForExit(2000);
                }
            }

            return connected;
        }


        public static bool IsTcpPortFree(int tcpPort)
        {
            var ipGlobalProperties = IPGlobalProperties.GetIPGlobalProperties();

            var activeTcpConnections = ipGlobalProperties.GetActiveTcpConnections();
            var listeningTcpPorts = ipGlobalProperties.GetActiveTcpListeners();
            var isTcpPortInUse = activeTcpConnections.Any(p => p.LocalEndPoint.Port == tcpPort) || 
                                 listeningTcpPorts.Any(tcpEndPoint => tcpEndPoint.Port == tcpPort);
            return !isTcpPortInUse;
        }

        /// <inheritdoc />
        public IntPtr GetWindowHandle()
        {
            // Retrieve the wain window handle
            if (Process != null)
            {
                return Process.MainWindowHandle;
            }

            RequireBuild(7750);
            // RoboDK was not started from this application.
            // In that case, we can retrieve the window pointer by using a specific RoboDK command
            var mainWindowId = Command("MainWindow_ID");
            return new IntPtr(Convert.ToInt32(mainWindowId));
        }

        /// <inheritdoc />
        public IRoboDKEventSource OpenRoboDkEventChannel()
        {
            return new RoboDKEventSource(this);
        }

        /// <inheritdoc />
        public void CloseRoboDK()
        {
            check_connection();
            const string command = "QUIT";
            send_line(command);
            check_status();
            _bufferedSocket.Dispose();
            _bufferedSocket = null;
            Process = null;
        }

        /// <inheritdoc />
        public string Version()
        {
            check_connection();
            send_line("Version");
            string appName = rec_line();
            int bitArch = rec_int();
            string ver4 = rec_line();
            string dateBuild = rec_line();
            check_status();
            return ver4;
        }

        /// <inheritdoc />
        public void SetWindowState(WindowState windowState = WindowState.Normal)
        {
            check_connection();
            var command = "S_WindowState";
            send_line(command);
            send_int((int)windowState);
            check_status();
        }

        /// <inheritdoc />
        public void Copy(IItem tocopy, bool copy_children = true)
        {
            if (RoboDKBuild < 18705)
            {
                check_connection();
                send_line("Copy");
                send_item(tocopy);
                check_status();
            }
            else
            {
                RequireBuild(18705);
                check_connection();
                send_line("Copy2");
                send_item(tocopy);
                send_int(copy_children ? 1 : 0);
                check_status();
            }
        }

        /// <inheritdoc />
        public IItem Paste(IItem paste_to = null)
        {
            check_connection();
            send_line("Paste");
            send_item(paste_to);
            IItem newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public List<IItem> Paste(IItem paste_to, int paste_times)
        {
            check_connection();
            send_line("PastN");
            send_item(paste_to);
            send_int(paste_times);
            ReceiveTimeout = paste_times * 1000;
            int ntimes = rec_int();

            List<IItem> list_items = new List<IItem>();
            for (int i = 0; i < ntimes; i++)
            {
                IItem newitem = rec_item();
                list_items.Add(newitem);
            }

            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return list_items;
        }

        /// <inheritdoc />
        public IItem AddFile(string filename, IItem parent = null)
        {
            if (!File.Exists(filename))
            {
                throw new FileNotFoundException(filename);
            }

            return AddItem(filename, parent);
        }

        /// <inheritdoc />
        public IItem AddText(string text, IItem parent = null)
        {
            var textItem = AddItem("", parent);
            textItem.SetName(text);
            return textItem;
        }


        private IItem AddItem(string filename, IItem parent = null)
        {
            check_connection();
            var command = "Add";
            send_line(command);
            send_line(filename);
            send_item(parent);
            ReceiveTimeout = 3600 * 1000;
            var newItem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newItem;
        }


        /// <inheritdoc />
        public IItem AddTarget(string name, IItem parent = null, IItem robot = null)
        {
            check_connection();
            var command = "Add_TARGET";
            send_line(command);
            send_line(name);
            send_item(parent);
            send_item(robot);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddProgram(string name, IItem robot = null)
        {
            check_connection();
            var command = "Add_PROG";
            send_line(command);
            send_line(name);
            send_item(robot);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddMachiningProject(string name = "Curve follow settings", IItem itemrobot = null)
        {
            check_connection();
            send_line("Add_MACHINING");
            send_line(name);
            send_item(itemrobot);
            IItem newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public void Render(bool alwaysRender = false)
        {
            var autoRender = !alwaysRender;
            check_connection();
            var command = "Render";
            send_line(command);
            send_int(autoRender ? 1 : 0);
            check_status();
        }

        /// <summary>
        ///    Update the screen. This updates the position of all robots and internal links according to previously set values.
        /// </summary>
        public void Update()
        {
            check_connection();
            var command = "Refresh";
            send_line(command);
            send_int(0);
            check_status();
        }

        /// <inheritdoc />
        public IItem GetItemByName(string name, ItemType itemType = ItemType.Any)
        {
            check_connection();
            string command;
            if (itemType == ItemType.Any)
            {
                command = "G_Item";
                send_line(command);
                send_line(name);
            }
            else
            {
                var type = (int)itemType;
                command = "G_Item2";
                send_line(command);
                send_line(name);
                send_int(type);
            }

            var item = rec_item();
            check_status();
            return item;
        }

        /// <inheritdoc />
        public List<string> GetItemListNames(ItemType itemType = ItemType.Any)
        {
            check_connection();
            string command;
            if (itemType == ItemType.Any)
            {
                command = "G_List_Items";
                send_line(command);
            }
            else
            {
                command = "G_List_Items_Type";
                send_line(command);
                send_int((int)itemType);
            }

            var numitems = rec_int();
            var listnames = new List<string>(numitems);
            for (var i = 0; i < numitems; i++)
            {
                var itemName = rec_line();
                listnames.Add(itemName);
            }

            check_status();
            return listnames;
        }

        /// <inheritdoc />
        public List<IItem> GetItemList(ItemType itemType = ItemType.Any)
        {
            check_connection();
            string command;
            if (itemType == ItemType.Any)
            {
                command = "G_List_Items_ptr";
                send_line(command);
            }
            else
            {
                command = "G_List_Items_Type_ptr";
                send_line(command);
                send_int((int)itemType);
            }

            var numitems = rec_int();
            var listitems = new List<IItem>(numitems);
            for (var i = 0; i < numitems; i++)
            {
                var item = rec_item();
                listitems.Add(item);
            }

            check_status();
            return listitems;
        }

        /// <inheritdoc />
        public IItem ItemUserPick(string message = "Pick one item", ItemType itemType = ItemType.Any)
        {
            check_connection();
            var command = "PickItem";
            send_line(command);
            send_line(message);
            send_int((int)itemType);

            // wait up to 1 hour for user input
            _bufferedSocket.ReceiveTimeout = 3600 * 1000;
            var item = rec_item();
            _bufferedSocket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return item;
        }

        /// <inheritdoc />
        public void ShowRoboDK()
        {
            check_connection();
            var command = "RAISE";
            send_line(command);
            check_status();
        }

        /// <inheritdoc />
        public void FitAll()
        {
            check_connection();
            send_line("FitAll");
            check_status();
        }

        /// <inheritdoc />
        public void HideRoboDK()
        {
            check_connection();
            var command = "HIDE";
            send_line(command);
            check_status();
        }

        /// <inheritdoc />
        public void SetWindowFlags(WindowFlags flags)
        {
            check_connection();
            var command = "S_RoboDK_Rights";
            send_line(command);
            send_int((int)flags);
            check_status();
        }

        /// <inheritdoc />
        public ItemFlags GetItemFlags(IItem item)
        {
            check_connection();
            send_line("G_Item_Rights");
            send_item(item);
            ItemFlags result = (ItemFlags)rec_int();
            check_status();
            return result;
        }

        /// <inheritdoc />
        public void SetItemFlags(ItemFlags itemFlags = ItemFlags.All)
        {
            var flags = (int) itemFlags;
            check_connection();
            send_line("S_Item_Rights");
            send_item(null);
            send_int(flags);
            check_status();
        }

        /// <inheritdoc />
        public void ShowMessage(string message, bool popup = true)
        {
            check_connection();
            if (popup)
            {
                var command = "ShowMessage";
                send_line(command);
                send_line(message);
                _bufferedSocket.ReceiveTimeout = 3600 * 1000;
                check_status();
                _bufferedSocket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            }
            else
            {
                var command = "ShowMessageStatus";
                send_line(command);
                send_line(message);
                check_status();
            }
        }

        /// <inheritdoc />
        public void Save(string filename, IItem itemsave = null)
        {
            check_connection();
            var command = "Save";
            send_line(command);
            send_line(filename);
            send_item(itemsave);
            check_status();
        }

        /// <inheritdoc />
        public IItem AddStation(string name)
        {
            check_connection();
            send_line("NewStation");
            send_line(name);
            IItem newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddShape(Mat trianglePoints, IItem addTo = null, bool shapeOverride = false, Color? color = null)
        {
            RequireBuild(5449);
            var clr = color ?? Color.FromArgb(255, 127, 127, 127);
            var colorArray = clr.ToRoboDKColorArray();
            check_connection();
            send_line("AddShape3");
            send_matrix(trianglePoints);
            send_item(addTo);
            send_int(shapeOverride ? 1 : 0);
            send_array(colorArray);
            ReceiveTimeout = 3600 * 1000;
            var newitem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddShape(List<Mat> listTrianglePoints, IItem add_to = null, bool shape_override = false, List<Color> listColor = null)
        {
            RequireBuild(16532);
            int nsubobjs = listTrianglePoints.Count;
            if (listColor != null)
            {
                nsubobjs = Math.Min(nsubobjs, listColor.Count);
            }
            check_connection();
            send_line("AddShape4");
            send_item(add_to);
            send_int(shape_override ? 1 : 0);
            send_int(nsubobjs);
            for (int i = 0; i < nsubobjs; i++)
            {
                send_matrix(listTrianglePoints[i]);
                if (listColor != null)
                {
                    send_array(listColor[i].ToRoboDKColorArray());
                }
                else
                {
                    send_array(null);
                }
            }
            ReceiveTimeout = 3600 * 1000;
            var newitem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddCurve(Mat curvePoints, IItem referenceObject = null, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            check_connection();
            var command = "AddWire";
            send_line(command);
            send_matrix(curvePoints);
            send_item(referenceObject);
            send_int(addToRef ? 1 : 0);
            send_int((int)projectionType);
            ReceiveTimeout = 3600 * 1000;
            var newitem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public IItem AddPoints(Mat points, IItem referenceObject = null, bool addToRef = false, ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            check_connection();
            send_line("AddPoints");
            send_matrix(points);
            send_item(referenceObject);
            send_int(addToRef ? 1 : 0);
            send_int((int)projectionType);
            ReceiveTimeout = 3600 * 1000;
            IItem newitem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public Mat ProjectPoints(Mat points, IItem objectProject,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            check_connection();
            var command = "ProjectPoints";
            send_line(command);
            send_matrix(points);
            send_item(objectProject);
            send_int((int)projectionType);
            ReceiveTimeout = 3600 * 1000;
            var projectedPoints = rec_matrix();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return projectedPoints;
        }

        /// <inheritdoc />
        public void CloseStation()
        {
            RequireBuild(12939);
            check_connection();
            var command = "RemoveStn";
            send_line(command);
            check_status();
        }

        /// <inheritdoc />
        public void Delete(List<IItem> item_list)
        {
            RequireBuild(12939);
            check_connection();
            var command = "RemoveLst";
            send_line(command);
            send_int(item_list.Count());
            foreach (IItem itm in item_list){
                send_item(itm);
                // itm.ItemId = 0; // how to make Item a friend class of Robolink in C#?
            }
            check_status();
        }

        /// <inheritdoc />
        public IItem AddFrame(string name, IItem parent = null)
        {
            check_connection();
            var command = "Add_FRAME";
            send_line(command);
            send_line(name);
            send_item(parent);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <inheritdoc />
        public int RunProgram(string function)
        {
            return RunCode(function, true);
        }

        /// <inheritdoc />
        public int RunCode(string code, bool codeIsFunctionCall = false)
        {
            check_connection();
            var command = "RunCode";
            send_line(command);
            send_int(codeIsFunctionCall ? 1 : 0);
            send_line(code);
            var progStatus = rec_int();
            check_status();
            return progStatus;
        }

        /// <inheritdoc />
        public void RunMessage(string message, bool messageIsComment = false)
        {
            check_connection();
            var command = "RunMessage";
            send_line(command);
            send_int(messageIsComment ? 1 : 0);
            send_line(message);
            check_status();
        }

        /// <inheritdoc />
        public bool IsInside(IItem objectInside, IItem objectParent)
        {
            check_connection();
            var command = "IsInside";
            send_line(command);
            send_item(objectInside);
            send_item(objectParent);
            var inside = rec_int();
            check_status();
            return inside > 0;
        }

        /// <inheritdoc />
        public int SetCollisionActive(CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOn)
        {
            check_connection();
            send_line("Collision_SetState");
            send_int((int)collisionCheck);
            var ncollisions = rec_int();
            check_status();
            return ncollisions;
        }

        /// <inheritdoc />
        public void EnableCollisionCheckingForAllItems()
        {
            Command("CollisionMap", "All");
        }

        /// <inheritdoc />
        public void DisableCollisionCheckingForAllItems()
        {
            Command("CollisionMap", "None");
        }

        /// <inheritdoc />
        public bool SetCollisionActivePair(CollisionCheckOptions collisionCheck, CollisionPair collisionPair)
        {
            check_connection();
            var command = "Collision_SetPair";
            send_line(command);
            send_item(collisionPair.Item1);
            send_item(collisionPair.Item2);
            send_int(collisionPair.RobotLinkId1);
            send_int(collisionPair.RobotLinkId2);
            send_int((int)collisionCheck);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <inheritdoc />
        public bool SetCollisionActivePair(List<CollisionCheckOptions> checkState, IReadOnlyList<CollisionPair> collisionPairs)
        {
            check_connection();
            send_line("Collision_SetPairList");
            int npairs = Math.Min(checkState.Count, collisionPairs.Count);
            send_int(npairs);
            for (int i = 0; i < npairs; i++)
            {
                // Tag1: Send items
                send_item(collisionPairs[i].Item1);
                send_item(collisionPairs[i].Item2);
                // Tag2: send id's
                send_int(collisionPairs[i].RobotLinkId1);
                send_int(collisionPairs[i].RobotLinkId2);
                // Tag3: send check state
                send_int((int)checkState[i]);
            }

            int nok = rec_int();
            check_status();
            return nok == npairs;
        }

        /// <inheritdoc />
        public int Collisions()
        {
            check_connection();
            var command = "Collisions";
            send_line(command);
            var ncollisions = rec_int();
            check_status();
            return ncollisions;
        }

        /// <inheritdoc />
        public bool Collision(IItem item1, IItem item2, bool useCollisionMap = true)
        {
            RequireBuild(5449);
            check_connection();
            send_line("Collided3");
            send_item(item1);
            send_item(item2);
            send_int(useCollisionMap ? 1 : 0);
            var ncollisions = rec_int();
            check_status();
            return ncollisions > 0;
        }

        /// <inheritdoc />
        public List<CollisionItem> GetCollisionItems()
        {
            check_connection();
            send_line("Collision_Items");
            int nitems = rec_int();
            List<CollisionItem> itemList = new List<CollisionItem>(nitems);
            for (int i = 0; i < nitems; i++)
            {
                IItem item = rec_item();
                int id = rec_int();
                itemList.Add(new CollisionItem(item, id));

                int collisionTimes = rec_int(); //number of objects it is in collisions with (unused)
            }
            check_status();
            return itemList;
        }

        /// <inheritdoc />
        public List<CollisionPair> GetCollisionPairs()
        {
            check_connection();
            send_line("Collision_Pairs");
            int nitems = rec_int();
            List<CollisionPair> list_items = new List<CollisionPair>(nitems);
            for (int i = 0; i < nitems; i++)
            {
                IItem item1 = rec_item();
                int id1 = rec_int();
                IItem item2 = rec_item();
                int id2 = rec_int();
                CollisionPair collisionPair = new CollisionPair(item1, id1, item2, id2);
                list_items.Add(collisionPair);
            }
            check_status();
            return list_items;
        }

        /// <inheritdoc />
        public List<CollisionPair> CollisionActivePairList()
        {
            check_connection();
            send_line("Collision_GetPairList");
            int nitems = rec_int();
            List<CollisionPair> list_items = new List<CollisionPair>(nitems);
            for (int i = 0; i < nitems; i++)
            {
                IItem item1 = rec_item();
                int id1 = rec_int();
                IItem item2 = rec_item();
                int id2 = rec_int();
                CollisionPair collisionPair = new CollisionPair(item1, id1, item2, id2);
                list_items.Add(collisionPair);
            }
            check_status();
            return list_items;
        }

        /// <inheritdoc />
        public void SetSimulationSpeed(double speed)
        {
            check_connection();
            var command = "SimulateSpeed";
            send_line(command);
            send_int((int)(speed * 1000.0));
            check_status();
        }

        /// <inheritdoc />
        public double GetSimulationSpeed()
        {
            check_connection();
            var command = "GetSimulateSpeed";
            send_line(command);
            var speed = rec_int() / 1000.0;
            check_status();
            return speed;
        }

        /// <inheritdoc />
        public void SetRunMode(RunMode runMode = RunMode.Simulate)
        {
            check_connection();
            var command = "S_RunMode";
            send_line(command);
            send_int((int)runMode);
            check_status();
        }

        /// <inheritdoc />
        public RunMode GetRunMode()
        {
            check_connection();
            var command = "G_RunMode";
            send_line(command);
            var runMode = (RunMode)rec_int();
            check_status();
            return runMode;
        }

        /// <inheritdoc />
        public List<KeyValuePair<string, string>> GetParameterList()
        {
            check_connection();
            const string command = "G_Params";
            send_line(command);
            var nparam = rec_int();
            var paramlist = new List<KeyValuePair<string, string>>(nparam);
            for (int i = 0; i < nparam; i++)
            {
                var param = rec_line();
                var value = rec_line();
                var paramValue = new KeyValuePair<string, string>(param, value);
                paramlist.Add(paramValue);
            }

            check_status();
            return paramlist;
        }

        /// <inheritdoc />
        public string GetParameter(string parameter)
        {
            check_connection();
            const string command = "G_Param";
            send_line(command);
            send_line(parameter);
            var value = rec_line();
            if (value.StartsWith("UNKNOWN "))
            {
                value = null;
            }

            check_status();
            return value;
        }

        /// <inheritdoc />
        public void SetParameter(string parameter, string value)
        {
            check_connection();
            var command = "S_Param";
            send_line(command);
            send_line(parameter);
            send_line(value);
            check_status();
        }

        /// <inheritdoc />
        public void SetParameter(string parameter, double value)
        {
            check_connection();
            var command = "S_Param";
            send_line(command);
            send_line(parameter);
            send_line(value.ToString(CultureInfo.InvariantCulture));
            check_status();
        }

        /// <inheritdoc />
        public byte[] GetBinaryParameter(string parameter)
        {
            check_connection();
            const string command = "G_DataParam";
            send_line(command);
            send_line(parameter);
            var value = rec_bytes();
            check_status();
            return value;
        }

        /// <inheritdoc />
        public void SetBinaryParameter(string parameter, byte[] data)
        {
            check_connection();
            var command = "S_DataParam";
            send_line(command);
            send_line(parameter);
            send_bytes(data);
            check_status();
        }

        /// <inheritdoc />
        public string Command(string cmd, string value = "")
        {
            check_connection();
            send_line("SCMD");
            send_line(cmd);
            send_line(value);
            string response = rec_line();
            check_status();
            return response;
        }

        /// <inheritdoc />
        public string Command(string cmd, bool value)
        {
            return Command(cmd, value ? "1" : "0");
        }

        /// <inheritdoc />
        public string Command(string cmd, int value)
        {
            return Command(cmd, value.ToString(CultureInfo.InvariantCulture));
        }

        /// <inheritdoc />
        public string Command(string cmd, double value)
        {
            var valueAsString = value.ToString(CultureInfo.InvariantCulture);
            return Command(cmd, valueAsString);
        }

        /// <inheritdoc />
        public List<IItem> GetOpenStation()
        {
            check_connection();
            send_line("G_AllStn");
            int nstn = rec_int();
            List < IItem > listStn = new List<IItem>(nstn);
            for (int i = 0; i < nstn; i++)
            {
                IItem station = rec_item();
                listStn.Add(station);
            }
            check_status();
            return listStn;
        }

        /// <inheritdoc />
        public IItem GetActiveStation()
        {
            check_connection();
            send_line("G_ActiveStn");
            IItem station = rec_item();
            check_status();
            return station;
        }

        /// <inheritdoc />
        public void SetActiveStation(IItem station)
        {
            check_connection();
            send_line("S_ActiveStn");
            send_item(station);
            check_status();
        }

        /// <inheritdoc />
        public double[] LaserTrackerMeasure(double[] estimate, bool search = false)
        {
            check_connection();
            var command = "MeasLT";
            send_line(command);
            send_xyz(estimate);
            send_int(search ? 1 : 0);
            var xyz = new double[3];
            rec_xyz(xyz);
            check_status();
            if (xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2] < 0.0001)
            {
                return null;
            }

            return xyz;
        }

        /// <inheritdoc />
        public void StereoCameraMeasure(out Mat pose1, out Mat pose2, out int npoints1, out int npoints2, out int time,
            out int status)
        {
            check_connection();
            var command = "MeasPose";
            send_line(command);
            pose1 = rec_pose();
            pose2 = rec_pose();
            npoints1 = rec_int();
            npoints2 = rec_int();
            time = rec_int();
            status = rec_int();
            check_status();
        }

        /// <inheritdoc />
        public bool CollisionLine(double[] p1, double[] p2)
        {
            check_connection();
            var command = "CollisionLine";
            send_line(command);
            send_xyz(p1);
            send_xyz(p2);
            var item = rec_item();
            var xyz = new double[3];
            rec_xyz(xyz);
            var collision = item.Valid();
            check_status();
            return collision;
        }

        /// <inheritdoc />
        public CollisionLineResult CollisionLine(double[] p1, double[] p2, Mat reference = null)
        {
            if (reference == null)
            {
                reference = Mat.Identity4x4();
            }

            check_connection();
            send_line("CollisionLine");
            send_xyz(reference * p1);
            send_xyz(reference * p2);
            var item = rec_item();
            var xyz = new double[3];
            rec_xyz(xyz);
            check_status();
            return new CollisionLineResult(item, xyz);
        }

        /// <inheritdoc />
        public List<Mat> SolveFK(List<IItem> robotList, List<double[]> jointsList, List<bool> solutionOkList = null)
        {
            RequireBuild(6535);
            var numberOfItems = Math.Min(robotList.Count, jointsList.Count);
            
            check_connection();
            send_line("G_LFK");
            send_int(numberOfItems);
            var listPoses = new List<Mat>();
            for (var i = 0; i < numberOfItems; i++)
            {
                send_array(jointsList[i]);
                send_item(robotList[i]);
                var pose = rec_pose();
                var status = rec_int();
                listPoses.Add(pose);
                solutionOkList?.Add(status > 0);
            }
            check_status();
            return listPoses;
        }


        /// <inheritdoc />
        public List<double[]> SolveIK(List<IItem> robotList, List<Mat> poseList)
        {
            RequireBuild(6535);
            var numberOfItems = Math.Min(robotList.Count, poseList.Count);
            check_connection();
            send_line("G_LIK");
            send_int(numberOfItems);
            var listJoints = new List<double[]>();
            for (var i = 0; i < numberOfItems; i++)
            {
                send_pose(poseList[i]);
                send_item(robotList[i]);
                var jointsSol = rec_array();
                listJoints.Add(jointsSol);
            }
            check_status();
            return listJoints;
        }


        /// <inheritdoc />
        public List<double[]> SolveIK(List<IItem> robotList, List<Mat> poseList, List<double[]> japroxList)
        {
            RequireBuild(7399);
            var numberOfItems = Math.Min(Math.Min(robotList.Count, poseList.Count), japroxList.Count);
            check_connection();
            send_line("G_LIK_jnts");
            send_int(numberOfItems);
            var listJoints = new List<double[]>();
            for (int i = 0; i < numberOfItems; i++)
            {
                send_pose(poseList[i]);
                send_array(japroxList[i]);
                send_item(robotList[i]);
                var jointsSol = rec_array();
                listJoints.Add(jointsSol);
            }
            check_status();
            return listJoints;
        }


        /// <inheritdoc />
        public List<Mat> SolveIK_All(List<IItem> robotList, List<Mat> poseList)
        {
            RequireBuild(7399);
            var numberOfItems = Math.Min(robotList.Count, poseList.Count);
            check_connection();
            send_line("G_LIK_cmpl");
            send_int(numberOfItems);
            var listJoints2d = new List<Mat>();
            for (int i = 0; i < numberOfItems; i++)
            {
                send_pose(poseList[i]);
                send_item(robotList[i]);
                var jointsSolAll = rec_matrix();
                listJoints2d.Add(jointsSolAll);
            }
            check_status();
            return listJoints2d;
        }

        /// <inheritdoc />
        public List<double[]> JointsConfig(List<IItem> robotList, List<double[]> jointsList)
        {
            RequireBuild(7399);
            var numberOfItems = Math.Min(robotList.Count, jointsList.Count);
            check_connection();
            send_line("G_LThetas_Config");
            send_int(numberOfItems);
            var listConfig = new List<double[]>();
            for (var i = 0; i < numberOfItems; i++)
            {
                send_array(jointsList[i]);
                send_item(robotList[i]);
                double[] config = rec_array();
                listConfig.Add(config);
            }
            check_status();
            return listConfig;
        }

        /// <inheritdoc />
        public void SetVisible(List<IItem> itemList, List<bool> visibleList, List<int> visibleFrames = null)
        {
            int nitm = Math.Min(itemList.Count, visibleList.Count);
            check_connection();
            send_line("S_VisibleList");
            send_int(nitm);
            for (int i = 0; i < nitm; i++)
            {
                send_item(itemList[i]);
                send_int(visibleList[i] ? 1 : 0);
                int frameVis = -1;
                if (visibleFrames != null && visibleFrames.Count > i)
                {
                    frameVis = visibleFrames[i];
                }
                send_int(frameVis);
            }
            check_status();
        }


        static char[] hexDigits = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
        public static string Color2Hex(Color color)
        {
            byte[] bytes = new byte[4];
            bytes[0] = color.A;
            bytes[1] = color.R;
            bytes[2] = color.G;
            bytes[3] = color.B;
            char[] chars = new char[bytes.Length * 2];
            for (int i = 0; i < bytes.Length; i++)
            {
                int b = bytes[i];
                chars[i * 2] = hexDigits[b >> 4];
                chars[i * 2 + 1] = hexDigits[b & 0xF];
            }
            return new string(chars);
        }

        /// <inheritdoc />
        public void SetColor(List<IItem> item_list, List<Color> color_list)
        {
            RequireBuild(6471);
            int nitm = Math.Min(item_list.Count, color_list.Count);
            check_connection();
            send_line("S_ColorList");
            send_int(nitm);
            for (int i = 0; i < nitm; i++)
            {
                send_item(item_list[i]);
                send_line("#" + Color2Hex(color_list[i]));
            }
            check_status();
        }
        public void SetColor(List<IItem> item_list, List<double[]> color_list)
        {
            RequireBuild(6471);
            int nitm = Math.Min(item_list.Count, color_list.Count);
            check_connection();
            send_line("S_ColorList2");
            send_int(nitm);
            for (int i = 0; i < nitm; i++)
            {
                send_item(item_list[i]);
                send_array(color_list[i]);
            }
            check_status();
        }



        /// <inheritdoc />
        public void ShowAsCollided(List<IItem> item_list, List<bool> collided_list, List<int> robot_link_id = null)
        {
            RequireBuild(5794);
            check_connection();
            int nitms = Math.Min(item_list.Count, collided_list.Count);
            if (robot_link_id != null)
            {
                nitms = Math.Min(nitms, robot_link_id.Count);
            }
            send_line("ShowAsCollidedList");
            send_int(nitms);
            for (int i = 0; i < nitms; i++)
            {
                send_item(item_list[i]);
                send_int(collided_list[i] ? 1 : 0);
                int link_id = 0;
                if (robot_link_id != null)
                {
                    link_id = robot_link_id[i];
                }
                send_int(link_id);
            }
            check_status();
        }

        /// <inheritdoc />
        public List<double[]> Joints(List<IItem> robotItemList)
        {
            check_connection();
            var command = "G_ThetasList";
            send_line(command);
            int nrobots = robotItemList.Count;
            send_int(nrobots);
            var jointsList = new List<double[]>();
            foreach (var robot in robotItemList)
            {
                send_item(robot);
                var joints = rec_array();
                jointsList.Add(joints);
            }

            check_status();
            return jointsList;
        }

        /// <inheritdoc />
        public void SetJoints(List<IItem> robotItemList, List<double[]> jointsList)
        {
            var nrobs = Math.Min(robotItemList.Count, jointsList.Count);
            check_connection();
            var command = "S_ThetasList";
            send_line(command);
            send_int(nrobs);
            for (var i = 0; i < nrobs; i++)
            {
                send_item(robotItemList[i]);
                send_array(jointsList[i]);
            }

            check_status();
        }

        /// <inheritdoc />
        public double[] CalibrateTool(Mat posesJoints, out double[] errorStats,
            EulerType format = EulerType.EulerRxRyRz,
            TcpCalibrationType algorithm = TcpCalibrationType.CalibrateTcpByPoint,
            IItem robot = null)
        {
            check_connection();
            var command = "CalibTCP2";
            send_line(command);
            send_matrix(posesJoints);
            send_int((int)format);
            send_int((int)algorithm);
            send_item(robot);
            var tcp = rec_array();
            errorStats = rec_array();
            var errorGraph = rec_matrix();
            check_status();
            return tcp;
        }

        /// <inheritdoc />
        public Mat CalibrateReference(Mat joints,
            ReferenceCalibrationType method = ReferenceCalibrationType.Frame3P_P1OnX,
            bool useJoints = false, IItem robot = null)
        {
            check_connection();
            var command = "CalibFrame";
            send_line(command);
            send_matrix(joints);
            send_int(useJoints ? -1 : 0);
            send_int((int)method);
            send_item(robot);
            var referencePose = rec_pose();
            var errorStats = rec_array();
            check_status();

            //errors = errors[:, 1].tolist()
            return referencePose;
        }

        /// <inheritdoc />
        public int ProgramStart(string progname, string defaultfolder = "", string postprocessor = "",
            IItem robot = null)
        {
            check_connection();
            var command = "ProgramStart";
            send_line(command);
            send_line(progname);
            send_line(defaultfolder);
            send_line(postprocessor);
            send_item(robot);
            var errors = rec_int();
            check_status();
            return errors;
        }

        /// <inheritdoc />
        public void SetViewPose(Mat pose)
        {
            check_connection();
            var command = "S_ViewPose";
            send_line(command);
            send_pose(pose);
            check_status();
        }

        /// <inheritdoc />
        public Mat GetViewPose(ViewPoseType preset = ViewPoseType.ActiveView)
        {
            RequireBuild(6700);
            check_connection();
            var command = "G_ViewPose2";
            send_line(command);
            send_int((int)preset);
            var pose = rec_pose();
            check_status();
            return pose;
        }

        /// <inheritdoc />
        public bool SetRobotParams(IItem robot, double[][] dhm, Mat poseBase, Mat poseTool)
        {
            check_connection();
            send_line("S_AbsAccParam");
            send_item(robot);
            var r2b = Mat.Identity4x4();
            send_pose(r2b);
            send_pose(poseBase);
            send_pose(poseTool);
            var ndofs = dhm.Length;
            send_int(ndofs);
            for (var i = 0; i < ndofs; i++)
            {
                send_array(dhm[i]);
            }

            // for internal use only
            send_pose(poseBase);
            send_pose(poseTool);
            send_int(ndofs);
            for (var i = 0; i < ndofs; i++)
            {
                send_array(dhm[i]);
            }

            // reserved
            send_array(null);
            send_array(null);
            check_status();
            return true;
        }

        /// <inheritdoc />
        public IItem BuildMechanism(int type, List<IItem> listObj, List<double> param, List<double> jointsBuild, List<double> jointsHome, List<double> jointsSenses, List<double> jointsLimLow, List<double> jointsLimHigh, Mat baseFrame = null, Mat tool = null, string name = "New robot", IItem robot = null)
        {
            if (tool == null)
            {
                tool = Mat.Identity4x4();
            }
            if (baseFrame == null)
            {
                baseFrame = Mat.Identity4x4();
            }
            int ndofs = listObj.Count - 1;
            check_connection();
            send_line("BuildMechanism");
            send_item(robot);
            send_line(name);
            send_int(type);
            send_int(ndofs);
            for (int i = 0; i <= ndofs; i++)
            {
                send_item(listObj[i]);
            }
            send_pose(baseFrame);
            send_pose(tool);
            send_array(param.ToArray());
            Mat jointsData = new Mat(12, 5);
            for (int i = 0; i < ndofs; i++)
            {
                jointsData[i, 0] = jointsBuild[i];
                jointsData[i, 1] = jointsHome[i];
                jointsData[i, 2] = jointsSenses[i];
                jointsData[i, 3] = jointsLimLow[i];
                jointsData[i, 4] = jointsLimHigh[i];
            }
            send_matrix(jointsData);
            IItem newRobot = rec_item();
            check_status();
            return newRobot;
        }

        /// <inheritdoc />
        public long Cam2DAdd(IItem item, string cameraParameters = "")
        {
            check_connection();
            send_line("Cam2D_Add");
            send_item(item);
            send_line(cameraParameters);
            var camHandle = rec_ptr();
            check_status();
            return camHandle;
        }

        /// <inheritdoc />
        public bool Cam2DSnapshot(string fileSaveImg, long camHandle = 0)
        {
            check_connection();
            send_line("Cam2D_Snapshot");
            send_ptr(camHandle);
            send_line(fileSaveImg);
            var success = rec_int();
            check_status();
            return success > 0;
        }
		
		/// <inheritdoc />
        public bool Cam2DSnapshot(string fileSaveImg, IItem cam, string cameraParameters="")
        {
			if (fileSaveImg.Length == 0){
				throw new Exception("Retrieving binary image data is not supported");
			}
            check_connection();
            send_line("Cam2D_PtrSnapshot");
            send_item(cam);
            send_line(fileSaveImg);
			send_line(cameraParameters);			
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <inheritdoc />
        public bool Cam2DClose(long camHandle = 0)
        {
            check_connection();
            if (camHandle == 0)
            {
                send_line("Cam2D_CloseAll");
            }
            else
            {
                send_line("Cam2D_Close");
                send_ptr(camHandle);
            }

            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <inheritdoc />
        public bool Cam2DSetParameters(string cameraParameters, long camHandle = 0)
        {
            check_connection();
            send_line("Cam2D_SetParams");
            send_ptr(camHandle);
            send_line(cameraParameters);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <inheritdoc />
        public string GetLicense()
        {
            check_connection();
            var command = "G_License2";
            send_line(command);
            var license = rec_line();
            var cid = rec_line();
            check_status();
            return license;
        }

        /// <inheritdoc />
        public List<IItem> GetSelectedItems()
        {
            check_connection();
            var command = "G_Selection";
            send_line(command);
            var nitems = rec_int();
            var listItems = new List<IItem>(nitems);
            for (var i = 0; i < nitems; i++)
            {
                var item = rec_item();
                listItems.Add(item);
            }

            check_status();
            return listItems;
        }

        /// <inheritdoc />
        public void SetSelectedItems(List<IItem> item_list)
        {
            RequireBuild(8896);
            check_connection();
            send_line("S_Selection");
            send_int(item_list.Count);
            for (int i = 0; i < item_list.Count; i++)
            {
                send_item(item_list[i]);
            }
            check_status();
        }

        /// <inheritdoc />
        public IItem MergeItems(List<IItem> item_list)
        {
            RequireBuild(8896);
            check_connection();
            send_line("MergeItems");
            send_int(item_list.Count);
            for (int i = 0; i < item_list.Count; i++)
            {
                send_item(item_list[i]);
            }
            IItem newitem = rec_item();
            check_status();
            return newitem;
        }

        public IItem Popup_ISO9283_CubeProgram(IItem robot = null)
        {
            RequireBuild(5177);
            check_connection();
            send_line("Popup_ProgISO9283");
            send_item(robot);
            ReceiveTimeout = 3600 * 1000;
            IItem isoProgram = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return isoProgram;
        }

        /// <inheritdoc />
        public void SetInteractiveMode(InteractiveType modeType = InteractiveType.MoveReferences, DisplayRefType defaultRefFlags = DisplayRefType.DEFAULT, List<IItem> customItems = null, List<DisplayRefType> customRefFlags = null)
        {
            check_connection();
            send_line("S_InteractiveMode");
            send_int((int)modeType);
            send_int((int)defaultRefFlags);
            if (customItems == null || customRefFlags == null)
            {
                send_int(-1);
            }
            else
            {
                int nCustom = Math.Min(customItems.Count, customRefFlags.Count);
                send_int(nCustom);
                for (int i = 0; i < nCustom; i++)
                {
                    send_item(customItems[i]);
                    send_int((int)customRefFlags[i]);
                }
            }
            check_status();
        }

        /// <inheritdoc />
        public IItem GetCursorXYZ(int xCoord = -1, int yCoord = -1, List<double> xyzStation = null)
        {
            check_connection();
            send_line("Proj2d3d");
            send_int(xCoord);
            send_int(yCoord);
            int selection = rec_int();
            double[] xyz = new double[3];
            IItem selectedItem = rec_item();
            rec_xyz(xyz);
            check_status();
            if (xyz != null)
            {
                xyzStation.Add(xyz[0]); xyzStation.Add(xyz[1]); xyzStation.Add(xyz[2]);
            }
            return selectedItem;
        }

        /// <inheritdoc />
        public IItem AddTargetJ(IItem pgm, string targetName, double[] joints, IItem robotBase = null, IItem robot = null)
        {
            var target = AddTarget(targetName, robotBase, robot);
            if (target == null)
            {
                throw new Exception($"Create target '{targetName}' failed.");
            }

            target.SetVisible(false);
            target.SetAsJointTarget();
            target.SetJoints(joints);
            if (robot != null)
            {
                target.SetRobot(robot);
            }

            //target
            pgm.AddMoveJ(target);

            return target;
        }

        /// <inheritdoc />
        public bool EmbedWindow(string windowName, string dockedName = null, int width = -1, int height = -1, int pid = 0, int areaAdd = 1, int areaAllowed = 15, int timeout = 500)
        {
            check_connection();
            send_line("WinProcDock");
            send_line(dockedName != null ? dockedName : windowName);
            send_line(windowName);

            double[] size = { width, height };
            send_array(size);

            send_line(pid.ToString(CultureInfo.InvariantCulture));
            send_int(areaAdd);
            send_int(areaAllowed);
            send_int(timeout);

            int result = rec_int();
            check_status();
            return (result > 0);
        }

        /// <inheritdoc />
        public GetPointsResult GetPoints(ObjectSelectionType featureType = ObjectSelectionType.HoverObjectMesh)
        {
            if (featureType < ObjectSelectionType.HoverObjectMesh)
            {
                throw new RdkException("Invalid feature type, use ObjectSelectionType.HoverObjectMesh, ObjectSelectionType.HoverObject or equivalent");
            }

            check_connection();
            send_line("G_ObjPoint");
            send_item(null);
            send_int((int)featureType);

            int featureId = 0;
            send_int(0);
            
            Mat points = null;
            if (featureType == ObjectSelectionType.HoverObjectMesh)
            {
                points = rec_matrix();
            }

            IItem item = rec_item();
            rec_int(); // IsFrame
            featureType = (ObjectSelectionType)rec_int();
            featureId = rec_int();
            string name = rec_line();
            check_status();

            return new GetPointsResult(item, featureType, featureId, name, points);
        }

        /// <inheritdoc />
        public MeasurePoseResult MeasurePose(int target = -1, int averageTime = 0, List<double> tipOffset = null)
        {
            double[] array = { (double)target, (double)averageTime, 0.0, 0.0, 0.0 };
            if (tipOffset != null && tipOffset.Count >= 3)
            {
                array[2] = tipOffset[0];
                array[3] = tipOffset[1];
                array[4] = tipOffset[2];
            }

            check_connection();
            send_line("MeasPose4");
            send_array(array);
            Mat pose = rec_pose();
            array = rec_array();
            check_status();

            return new MeasurePoseResult(pose, array[0], array[1]);
        }

        /// <inheritdoc />
        public string PluginCommand(string pluginName, string command, string value)
        {
            check_connection();
            send_line("PluginCommand");
            send_line(pluginName);
            send_line(command);
            send_line(value);
            ReceiveTimeout = 3600 * 24 * 7;
            string result = rec_line();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return result;
        }

        /// <inheritdoc />
        public bool PluginLoad(string pluginName, PluginOperation operation = PluginOperation.Load)
        {
            switch (operation)
            {
                case PluginOperation.Load:
                    return (Command("PluginLoad", pluginName) == "OK");
                case PluginOperation.Reload:
                    Command("PluginUnload", pluginName);
                    return (Command("PluginLoad", pluginName) == "OK");
            }
            return (Command("PluginUnload", pluginName) == "OK");
        }

        /// <inheritdoc />
        public double GetSimulationTime()
        {
            check_connection();
            send_line("GetSimTime");
            double result = (double)rec_int() / 1000.0;
            check_status();
            return result;
        }

        /// <inheritdoc />
        public int SprayAdd(IItem tool = null, IItem referenceObject = null, string parameters = "", Mat points = null, Mat geometry = null)
        {
            check_connection();
            send_line("Gun_Add");
            send_item(tool);
            send_item(referenceObject);
            send_line(parameters);
            send_matrix(points);
            send_matrix(geometry);
            int result = rec_int();
            check_status();
            return result;
        }

        /// <inheritdoc />
        public int SprayClear(int sprayId = -1)
        {
            check_connection();
            send_line("Gun_Clear");
            send_int(sprayId);
            int result = rec_int();
            check_status();
            return result;
        }

        /// <inheritdoc />
        public string SprayGetStats(out Mat data, int sprayId = -1)
        {
            check_connection();
            send_line("Gun_Stats");
            send_int(sprayId);
            string result = rec_line().Replace("<br>", "\t");
            data = rec_matrix();
            check_status();
            return result;
        }

        /// <inheritdoc />
        public int SpraySetState(SprayGunStates state = SprayGunStates.SprayOn, int sprayId = -1)
        {
            check_connection();
            send_line("Gun_SetState");
            send_int(sprayId);
            send_int((int)state);
            int result = rec_int();
            check_status();
            return result;
        }

        /// <inheritdoc />
        public void SetPoses(List<IItem> items, List<Mat> poses)
        {
            if (items.Count != poses.Count)
            {
                throw new RdkException("The number of items must match the number of poses");
            }

            if (items.Count == 0)
            {
                return;
            }

            check_connection();
            send_line("S_Hlocals");
            send_int(items.Count);
            for (int i = 0; i < items.Count; i++)
            {
                send_item(items[i]);
                send_pose(poses[i]);
            }
            check_status();
        }

        /// <inheritdoc />
        public void SetPosesAbs(List<IItem> items, List<Mat> poses)
        {
            if (items.Count != poses.Count)
            {
                throw new RdkException("The number of items must match the number of poses");
            }

            if (items.Count == 0)
            {
                return;
            }

            check_connection();
            send_line("S_Hlocal_AbsS");
            send_int(items.Count);
            for (int i = 0; i < items.Count; i++)
            {
                send_item(items[i]);
                send_pose(poses[i]);
            }
            check_status();
        }

        /// <inheritdoc />
        public void ShowSequence(Mat sequence)
        {
            new Item(this).ShowSequence(sequence);
        }

        /// <inheritdoc />
        public void ShowSequence(List<double[]> joints = null, List<Mat> poses = null, SequenceDisplayFlags flags = SequenceDisplayFlags.Default, int timeout = -1)
        {
            new Item(this).ShowSequence(joints, poses, flags, timeout);
        }

        #endregion

        #region Protected Methods

        // Dispose(bool disposing) executes in two distinct scenarios.
        // If disposing equals true, the method has been called directly
        // or indirectly by a user's code. Managed and unmanaged resources
        // can be disposed.
        // If disposing equals false, the method has been called by the
        // runtime from inside the finalizer and you should not reference
        // other objects. Only unmanaged resources can be disposed.
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    // Dispose managed resources.
                    _bufferedSocket?.Dispose();
                }

                _disposed = true;
            }
        }

        #endregion

        #region Private Methods

        private bool StartNewRoboDkInstance()
        {
            StartNewRoboDKProcess(RoboDKServerStartPort);
            _bufferedSocket = ConnectToRoboDK(RoboDKServerIpAddress, RoboDKServerStartPort);
            return _bufferedSocket != null;
        }

        private bool TryConnectToExistingRoboDkInstance()
        {
            for (var port = RoboDKServerStartPort; port <= RoboDKServerEndPort; port++)
            {
                _bufferedSocket = ConnectToRoboDK(RoboDKServerIpAddress, port);
                if (_bufferedSocket != null)
                {
                    return true;
                }
            }

            return RoboDKServerIpAddress == "localhost" && StartNewRoboDkInstance();
        }

        private void StartNewRoboDKProcess(int tcpServerPort)
        {
            // No application path is given. Check the registry.
            if (string.IsNullOrEmpty(ApplicationDir))
            {
                ApplicationDir = RoboDKInstallPath();
            }

            if (string.IsNullOrEmpty(ApplicationDir))
            {
                throw new FileNotFoundException("RoboDK.exe installation directory not found.");
            }

            if (!File.Exists(ApplicationDir))
            {
                throw new FileNotFoundException($"RoboDK.exe not found in the given {nameof(ApplicationDir)}:{ApplicationDir}");
            }

            _commandLineParameter.ApiTcpServerPort = tcpServerPort;
            var commandLineArgumentString = _commandLineParameter.CommandLineArgumentString;
            commandLineArgumentString += $" {CustomCommandLineArgumentString}";
            commandLineArgumentString = commandLineArgumentString.Trim();

            var processStartInfo = new ProcessStartInfo
            {
                FileName = ApplicationDir,
                Arguments = commandLineArgumentString,
                RedirectStandardOutput = true,
                UseShellExecute = false
            };

            ValidateCommandLineParameter(processStartInfo);

            Debug.WriteLine($"Start RoboDK {Name}: {ApplicationDir}\n{processStartInfo.Arguments}");

            Process = Process.Start(processStartInfo);
            if (Process == null || Process.HasExited)
            {
                throw new RdkException("Unable to start RoboDK.exe.");
            }

            // wait for RoboDK to output (stdout) RoboDK is Running. Works after v3.4.0.
            var roboDkRunning = false;
            while (!roboDkRunning)
            {
                var line = Process.StandardOutput.ReadLine();
                if (line == null)
                {
                    throw new RdkException("Unable to start RoboDK.exe. StandardOutput closed unexpectedly.");
                }
                Debug.WriteLine($"RoboDK: {line}");
                roboDkRunning = line.Contains("RoboDK is Running");
            }

            Process.StandardOutput.Close();
        }

        private static void ValidateCommandLineParameter(ProcessStartInfo processStartInfo)
        {
            // Sanity check
            // If 'NEWINSTANCE' is a command line parameter, then it must be the first parameter
            if (processStartInfo.Arguments.Contains("NEWINSTANCE"))
            {
                if (!processStartInfo.Arguments.StartsWith($"{CommandLineOption.SwitchDelimiter}NEWINSTANCE"))
                {
                    throw new RdkException("The NEWINSTANCE Parameter must be the first command line parameter.");
                }
            }
        }

        private BufferedSocketAdapter ConnectToRoboDK(string host, int port)
        {
            if (_disposed)
            {
                throw new ObjectDisposedException(this.GetType().FullName);
            }

            Socket socket = null;
            try
            {
                socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP)
                {
                    SendTimeout = 1000,
                    ReceiveTimeout = 1000
                };
                socket.Connect(host, port);
                RoboDKServerPort = port;
                return new BufferedSocketAdapter(socket);
            }
            catch (SocketException)
            {
                socket?.Dispose();
                return null;
            }
        }

        #endregion

        #region Internal Methods

        //Returns 1 if connection is valid, returns 0 if connection is invalid
        internal bool is_connected()
        {
            return _bufferedSocket != null && _bufferedSocket.Connected;
        }

        /// <summary>
        ///     If we are not connected it will attempt a connection, if it fails, it will throw an error
        /// </summary>
        internal void check_connection()
        {
            if (_disposed)
            {
                throw new ObjectDisposedException(this.GetType().FullName);
            }

            if (!is_connected() && !Connect())
            {
                throw new RdkException("Can't connect to RoboDK API");
            }
        }

        /// <summary>
        ///     checks the status of the connection
        /// </summary>
        internal void check_status()
        {
            var status = rec_int();
            LastStatusMessage = "";
            switch (status)
            {
                case 0:
                    return;

                case 1:
                    LastStatusMessage = "Invalid item provided: The item identifier provided is not valid or it does not exist.";
                    throw new RdkException(LastStatusMessage);

                case 2:
                    {
                        //output warning
                        LastStatusMessage = rec_line();

                        //TODO chu: Implement warning
                        //print("WARNING: " + strproblems);
                        //#warn(strproblems)# does not show where is the problem...
                        return;
                    }
                case 3:
                    {
                        // output error
                        LastStatusMessage = rec_line();
                        throw new RdkException(LastStatusMessage);
                    }
                case 9:
                    {
                        LastStatusMessage = "Invalid license. Contact us at: info@robodk.com";
                        throw new RdkException(LastStatusMessage);
                    }
                case 10:
                    {
                        // Target reach error
                        LastStatusMessage = rec_line();
                        throw new RdkException(LastStatusMessage);
                    }
                case 11:
                    {
                        // Stopped by user
                        LastStatusMessage = rec_line();
                        throw new RdkException(LastStatusMessage);
                    }
                case 12:
                    {
                        // Invalid input exception
                        LastStatusMessage = rec_line();
                        throw new RdkException(LastStatusMessage);
                    }
                default:
                    {
                        if (status > 0 && status < 100)
                        {
                            // dedicated exception with message
                            LastStatusMessage = rec_line();
                            throw new RdkException(LastStatusMessage);
                        }
                        else { 
                            //raise Exception('Problems running function');
                            LastStatusMessage = "Unknown problem running RoboDK API function";
                            throw new RdkException(LastStatusMessage);
                        }
                    }
            }
        }

        /// <summary>
        ///     Formats the color in a vector of size 4x1 and ranges [0,1]
        /// </summary>
        /// <param name="color"></param>
        /// <returns></returns>
        internal bool check_color(double[] color)
        {
            if (color.Length < 4)
            {
                throw new RdkException("Invalid color. A color must be a 4-size double array [r,g,b,a]");
            }

            return true;
        }

        //Sends a string of characters with a \\n
        internal void send_line(string line)
        {
            line = line.Replace('\n', ' '); // one new line at the end only!
            var data = Encoding.UTF8.GetBytes($"{line}\n");
            try
            {
                _bufferedSocket.SendData(data);
            }
            catch
            {
                throw new RdkException("Send line failed.");
            }
        }

        internal string rec_line()
        {
            //Receives a string. It reads until if finds LF (\\n)
            var byteBuffer = new byte[1];
            var stringBuffer = new List<byte>(40);
            _bufferedSocket.ReceiveData(byteBuffer, 1);
            while (byteBuffer[0] != '\n')
            {
                stringBuffer.Add(byteBuffer[0]);
                _bufferedSocket.ReceiveData(byteBuffer, 1);
            }

            // convert stringBuffer to UTF-8 encoded string
            return Encoding.UTF8.GetString(stringBuffer.ToArray());
        }

        //Sends an item pointer
        internal void send_item(IItem item)
        {
            var bytes = item == null
                ? _bitConverter.GetBytes((ulong)0)
                : _bitConverter.GetBytes(item.ItemId);

            if (bytes.Length != 8)
            {
                throw new RdkException("API error");
            }

            try
            {
                _bufferedSocket.SendData(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        //Receives an item pointer
        internal IItem rec_item(RoboDK link = null)
        {
            var idBuffer = new byte[8];
            var typeBuffer = new byte[4];
            _bufferedSocket.ReceiveData(idBuffer, idBuffer.Length);
            _bufferedSocket.ReceiveData(typeBuffer, typeBuffer.Length);
            var itemId = _bitConverter.ToInt64(idBuffer, 0);
            var type = (ItemType)_bitConverter.ToInt32(typeBuffer, 0);
            if (link == null)
            {
                link = this;
            }

            var item = new Item(link, itemId, type);
            var itemProxy = ItemInterceptFunction(item);
            return itemProxy;
        }

        //Receives a byte array
        internal byte[] rec_bytes()
        {
            int bytes_len = rec_int();
            var data = new byte[bytes_len];
            _bufferedSocket.ReceiveData(data, bytes_len);
            return data;
        }

        //Sends a byte array
        internal void send_bytes(byte [] data)
        {
            send_int(data.Length);
            _bufferedSocket.SendData(data);
        }

        //Sends an item pointer
        internal void send_ptr(long ptr = 0)
        {
            var bytes = _bitConverter.GetBytes(ptr);
            _bufferedSocket.SendData(bytes);
        }

        ///Receives a generic pointer
        internal long rec_ptr()
        {
            var bytes = new byte[sizeof(long)];
            _bufferedSocket.ReceiveData(bytes, bytes.Length);
            var ptrH = _bitConverter.ToInt64(bytes, 0);
            return ptrH;
        }

        internal void send_pose(Mat pose)
        {
            if (!pose.IsHomogeneous())
            {
                throw new Exception($"Matrix not Homogenous: {pose.Cols}x{pose.Rows}");
            }

            for (var j = 0; j < pose.Cols; j++)
            {
                for (var i = 0; i < pose.Rows; i++)
                {
                    var onedouble = _bitConverter.GetBytes(pose[i, j]);
                    _bufferedSocket.SendData(onedouble);
                }
            }
        }

        internal Mat rec_pose()
        {
            var pose = new Mat(4, 4);
            var numberOfDoubles = pose.Cols * pose.Rows;
            var bytes = new byte[numberOfDoubles * sizeof(double)];
            _bufferedSocket.ReceiveData(bytes, bytes.Length);
            var cnt = 0;
            for (var j = 0; j < pose.Cols; j++)
            {
                for (var i = 0; i < pose.Rows; i++)
                {
                    pose[i, j] = _bitConverter.ToDouble(bytes, cnt);
                    cnt += sizeof(double);
                }
            }

            return pose;
        }

        internal void send_xyz(double[] xyzpos)
        {
            for (var i = 0; i < 3; i++)
            {
                var bytes = _bitConverter.GetBytes(xyzpos[i]);
                _bufferedSocket.SendData(bytes);
            }
        }

        internal void rec_xyz(double[] xyzpos)
        {
            var bytes = new byte[3 * sizeof(double)];
            _bufferedSocket.ReceiveData(bytes, bytes.Length);
            for (var i = 0; i < 3; i++)
            {
                xyzpos[i] = _bitConverter.ToDouble(bytes, i * sizeof(double));
            }
        }

        internal void send_int(int number)
        {
            var bytes = _bitConverter.GetBytes(number);
            try
            {
                _bufferedSocket.SendData(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        internal int rec_int()
        {
            var bytes = new byte[sizeof(int)];
            _bufferedSocket.ReceiveData(bytes, bytes.Length);
            return _bitConverter.ToInt32(bytes, 0);
        }

        internal void send_double(double number)
        {
            var bytes = _bitConverter.GetBytes(number);
            try
            {
                _bufferedSocket.SendData(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        internal double rec_double()
        {
            var bytes = new byte[sizeof(double)];
            _bufferedSocket.ReceiveData(bytes, bytes.Length);
            return _bitConverter.ToDouble(bytes, 0);
        }

        // Sends an array of doubles
        internal void send_array(double[] values)
        {
            if (values == null)
            {
                send_int(0);
                return;
            }

            var nvalues = values.Length;
            send_int(nvalues);
            for (var i = 0; i < nvalues; i++)
            {
                var onedouble = _bitConverter.GetBytes(values[i]);
                _bufferedSocket.SendData(onedouble);
            }
        }

        // Receives an array of doubles
        internal double[] rec_array()
        {
            var nvalues = rec_int();
            if (nvalues > 0)
            {
                var values = new double[nvalues];
                var bytes = new byte[nvalues * sizeof(double)];
                _bufferedSocket.ReceiveData(bytes, bytes.Length);
                for (var i = 0; i < nvalues; i++)
                {
                    values[i] = _bitConverter.ToDouble(bytes, i * sizeof(double));
                }

                return values;
            }

            return null;
        }

        // sends a 2 dimensional matrix
        internal void send_matrix(Mat mat)
        {
            send_int(mat.Rows);
            send_int(mat.Cols);
            for (var j = 0; j < mat.Cols; j++)
            {
                for (var i = 0; i < mat.Rows; i++)
                {
                    var bytes = _bitConverter.GetBytes(mat[i, j]);
                    _bufferedSocket.SendData(bytes);
                }
            }
        }

        // receives a 2 dimensional matrix (nxm)
        internal Mat rec_matrix()
        {
            var size1 = rec_int();
            var size2 = rec_int();
            var recvsize = size1 * size2 * sizeof(double);
            var bytes = new byte[recvsize];
            var mat = new Mat(size1, size2);
            if (recvsize > 0)
            {
                _bufferedSocket.ReceiveData(bytes, 0, recvsize);
            }

            var cnt = 0;
            for (var j = 0; j < mat.Cols; j++)
            {
                for (var i = 0; i < mat.Rows; i++)
                {
                    mat[i, j] = _bitConverter.ToDouble(bytes, cnt);
                    cnt += sizeof(double);
                }
            }

            return mat;
        }

        // private move type, to be used by public methods (MoveJ  and MoveL)
        internal void MoveX(IItem target, double[] joints, Mat matTarget, IItem itemrobot, int movetype,
            bool blocking = true)
        {
            RequireBuild(12939);
            itemrobot.WaitMove();
            if (blocking){
                send_line("MoveXb");
            } else {
                send_line("MoveX");
            }  
            send_int(movetype);
            if (target != null)
            {
                send_int(3);
                send_array(null);
                send_item(target);
            }
            else if (joints != null)
            {
                send_int(1);
                send_array(joints);
                send_item(null);
            }
            else if (matTarget != null && matTarget.IsHomogeneous())
            {
                send_int(2);
                send_array(matTarget.ToDoubles());
                send_item(null);
            }
            else
            {
                throw new RdkException("Invalid target type"); //raise Exception('Problems running function');
            }

            send_item(itemrobot);
            check_status();
            if (blocking)
            {
                //itemrobot.WaitMove();
                ReceiveTimeout = 360000 * 1000;
                check_status();//will wait here;
                ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            }
        }

        // private move type, to be used by public methods (MoveJ  and MoveL)
        internal void moveC_private(IItem target1, double[] joints1, Mat matTarget1, IItem target2, double[] joints2,
            Mat matTarget2, IItem itemrobot, bool blocking = true)
        {
            RequireBuild(12939);
            itemrobot.WaitMove();
            if (blocking){
                send_line("MoveCb");
            } else {
                send_line("MoveC");
            }            
            send_int(3);
            if (target1 != null)
            {
                send_int(3);
                send_array(null);
                send_item(target1);
            }
            else if (joints1 != null)
            {
                send_int(1);
                send_array(joints1);
                send_item(null);
            }
            else if (matTarget1 != null && matTarget1.IsHomogeneous())
            {
                send_int(2);
                send_array(matTarget1.ToDoubles());
                send_item(null);
            }
            else
            {
                throw new RdkException("Invalid type of target 1");
            }

            /////////////////////////////////////
            if (target2 != null)
            {
                send_int(3);
                send_array(null);
                send_item(target2);
            }
            else if (joints2 != null)
            {
                send_int(1);
                send_array(joints2);
                send_item(null);
            }
            else if (matTarget2 != null && matTarget2.IsHomogeneous())
            {
                send_int(2);
                send_array(matTarget2.ToDoubles());
                send_item(null);
            }
            else
            {
                throw new RdkException("Invalid type of target 2");
            }

            /////////////////////////////////////
            send_item(itemrobot);
            check_status();
            if (blocking)
            {
                //itemrobot.WaitMove();
                ReceiveTimeout = 360000 * 1000;
                check_status();//will wait here;
                ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            }
        }

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        /// <returns></returns>
        internal void Finish()
        {
            Disconnect();
        }

        internal bool VerifyConnection()
        {
            try
            {
                _bufferedSocket.ReceiveTimeout = 1000;

                var response = "";
                switch (_connectionType)
                {
                    case ConnectionType.Api:
                        send_line("RDK_API");
                        send_int(0);

                        //send_array(new double[] {0,0});
                        //send_array(new double[] { SafeMode ? 1 : 0, AutoUpdate ? 1 : 0 });
                        response = rec_line();
                        ApiVersion = rec_int();
                        RoboDKBuild = rec_int();
                        check_status();
                        return response == "RDK_API";

                    case ConnectionType.Event:
						if (_eventFilter.Count == 0){
							send_line("RDK_EVT");
						} else {
							// WARNING: RoboDK v5.6.4 required
							send_line("RDK_EVT_FILTER");
							send_int(_eventFilter.Count);
							for (int i = 0; i < _eventFilter.Count; i++){
								send_int(_eventFilter[i]);
							}								
						}
                        send_int(0);
                        response = rec_line();
                        EventChannelVersion = rec_int();
                        check_status();
                        return response == "RDK_EVT";

                    case ConnectionType.None:
                    default:
                        throw new RdkException($"unknown ConnectionType: {_connectionType}");
                }
            }
            catch (SocketException socketException)
            {
                return false;
            }
        }

        internal bool RequireBuild(int buildRequired)
        {
            if (RoboDKBuild == 0)
            {
                return true;
            }

            if (RoboDKBuild < buildRequired)
            {
                throw new RdkException("This function is unavailable. Update RoboDK to use this function through the API.");
            }

            return true;
        }

        public IRoboDKLink GetRoboDkLink()
        {
            return new RoboDKLink(this);
        }

        #endregion

        public interface IRoboDKLink
        {
            void CheckConnection();
            void SendLine(string line);
            void SendItem(IItem item);
            Mat ReceivePose();
            int ReceiveInt();
            double[] ReceiveArray();
            void CheckStatus();
        }


        public sealed class RoboDKLink : IRoboDKLink, IDisposable
        {
            public IRoboDK RoboDK { get; }

            private RoboDK Rdk => (RoboDK)RoboDK;

            public RoboDKLink(IRoboDK roboDK)
            {
                RoboDK = roboDK.CloneRoboDkConnection();
            }

            public void Dispose()
            {
                ((IDisposable)RoboDK).Dispose();
            }

            public void CheckConnection()
            {
                Rdk.check_connection();
            }

            public void SendLine(string line)
            {
                Rdk.send_line(line);
            }
            public void SendItem(IItem item)
            {
                Rdk.send_item(item);
            }

            public Mat ReceivePose()
            {
                return Rdk.rec_pose();
            }
            public int ReceiveInt()
            {
                return Rdk.rec_int();
            }

            public double[] ReceiveArray()
            {
                return Rdk.rec_array();
            }

            public void CheckStatus()
            {
                Rdk.check_status();
            }

        }

    }
}