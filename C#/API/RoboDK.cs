// ----------------------------------------------------------------------------------------------------------
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
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Media;
using System.Threading.Tasks;
using Microsoft.Win32;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    /// <summary>
    ///     This class is the link to allows to create macros and automate Robodk.
    ///     Any interaction is made through \"items\" (IItem() objects). An item is an object in the
    ///     robodk tree (it can be either a robot, an object, a tool, a frame, a program, ...).
    /// </summary>
    public class RoboDK : IRoboDK, IDisposable
    {
        #region Constants

        // Station parameters request
        public const string PATH_OPENSTATION = "PATH_OPENSTATION";
        public const string FILE_OPENSTATION = "FILE_OPENSTATION";
        public const string PATH_DESKTOP = "PATH_DESKTOP";

        #endregion

        #region Fields

        private bool _disposed;

        private Socket _socket; // tcpip com
        private RoboDKEventSource _roboDkEventSource;

        #endregion

        #region Constructors

        /// <summary>
        /// Creates a link with RoboDK
        /// </summary>
        public RoboDK()
        {
            CommandLineOptions = "";
            ApplicationDir = "";

            DefaultSocketTimeoutMilliseconds = 10 * 1000;

            SafeMode = true;
            AutoUpdate = false;
            StartHidden = false;

            RoboDKServerIpAdress = "localhost";
            RoboDKServerStartPort = 20500;
            RoboDKServerEndPort = RoboDKServerStartPort;

            RoboDKBuild = 0;
        }

        #endregion

        #region Properties

        /// <summary>
        /// Default Socket send / receive timeout in miliseconds: 10 seconds
        /// </summary>
        public int DefaultSocketTimeoutMilliseconds { get; set; }

        /// <summary>
        /// Command line arguments to provide to RoboDK on startup
        /// See https://robodk.com/doc/en/RoboDK-API.html#CommandLine
        /// </summary>
        public string CommandLineOptions { get; set; }

        /// <summary>
        /// True: checks that provided items exist in memory
        /// </summary>
        public bool SafeMode { get; set; }

        /// <summary>
        ///     if AutoUpdate is false, the scene is rendered after every function call
        /// </summary>
        public bool AutoUpdate { get; set; }

        /// <summary>
        /// Defines the RoboDK Simulator IP Address.
        /// Default: localhost (Client and RoboDK Server runs on same computer)
        /// </summary>
        public string RoboDKServerIpAdress { get; set; }

        /// <summary>
        /// Port to start looking for a RoboDK connection.
        /// </summary>
        public int RoboDKServerStartPort { get; set; }

        /// <summary>
        /// Port to stop looking for a RoboDK connection.
        /// </summary>
        public int RoboDKServerEndPort { get; set; }

        /// <summary>
        /// The RoboDK build id and is used for version checking. This value always increases with new versions
        /// </summary>
        public int RoboDKBuild { get; set; }

        /// <summary>
        /// Forces to start RoboDK in hidden mode. 
        /// ShowRoboDK must be used to show the window.
        /// </summary>
        public bool StartHidden { get; set; }

        /// <summary>
        /// TCP Port to which RoboDK is connected.
        /// </summary>
        public int RoboDKServerPort { get; private set; }

        internal int ReceiveTimeout
        {
            get { return _socket.ReceiveTimeout; }
            set { _socket.ReceiveTimeout = value; }
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
            string iniFile = System.Environment.GetFolderPath(System.Environment.SpecialFolder.ApplicationData) + "\\RoboDK\\RecentFiles.ini";
            string str = "";
            if (File.Exists(iniFile))
            {
                foreach (string line in File.ReadLines(iniFile))
                {
                    if (line.Contains("RecentFileList="))
                    {
                        str = line.Remove(0, "RecentFileList=".Length);
                        break;
                    }
                }
            }
            List<string> rdkList = new List<string>();
            string[] readList = str.Split(',');
            foreach (string st in readList)
            {
                string st2 = st.Trim();
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
        #endregion

        #region Public Methods

        /// <inheritdoc />
        public IRoboDK NewLink()
        {
            var rdk = new RoboDK()
            {
                RoboDKServerStartPort = this.RoboDKServerStartPort,
                RoboDKServerEndPort = this.RoboDKServerEndPort
            };
            rdk.Connect();
            return rdk;
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <inheritdoc />
        public bool Connected()
        {
            //return _socket.Connected;//does not work well
            // See:
            // https://stackoverflow.com/questions/2661764/how-to-check-if-a-socket-is-connected-disconnected-in-c
            if (_socket == null)
            {
                return false;
            }

            var part1 = _socket.Poll(10000, SelectMode.SelectRead);
            var part2 = _socket.Available == 0;

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
            if (_socket != null && _socket.Connected)
            {
                _socket.Disconnect(false);
            }
        }

        /// <inheritdoc />
        public bool Connect()
        {
            // Establishes a connection with robodk. 
            // robodk must be running, otherwise, the variable APPLICATION_DIR must be set properly.
            var connected = false;
            for (var i = 0; i < 2; i++)
            {
                if (RoboDKServerEndPort < RoboDKServerStartPort)
                {
                    RoboDKServerEndPort = RoboDKServerStartPort;
                }

                int port;
                for (port = RoboDKServerStartPort; port <= RoboDKServerEndPort; port++)
                {
                    _socket = ConnectToRoboDK(RoboDKServerIpAdress, port);
                    if (_socket != null)
                    {
                        connected = true;
                        break;
                    }
                }

                if (connected)
                {
                    RoboDKServerPort = port;
                    break;
                }

                if (RoboDKServerIpAdress != "localhost")
                {
                    break;
                }

                StartNewRoboDKProcess(RoboDKServerStartPort);
            }

            if (connected && !VerifyConnection())
            {
                connected = false;
                Process = null;
            }

            return connected;
        }

        public bool StartNewRoboDKProcess(int port)
        {
            bool started = false;

            var arguments = string.Format($"/PORT={port}");

            if (StartHidden)
            {
                arguments = string.Format($"/NOSPLASH /NOSHOW /HIDDEN {arguments}");
            }

            if (!string.IsNullOrEmpty(CommandLineOptions))
            {
                arguments = string.Format($"{arguments} {CommandLineOptions}");
            }

            // No application path is given. Check the registry.
            if (string.IsNullOrEmpty(ApplicationDir))
            {
                using (var hklm = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var regKey = hklm.OpenSubKey(@"SOFTWARE\RoboDK"))
                {
                    // key now points to the 64-bit key
                    var installPath = regKey?.GetValue("INSTDIR").ToString();
                    if (!string.IsNullOrEmpty(installPath))
                    {
                        ApplicationDir = installPath + "\\bin\\RoboDK.exe";
                    }
                }
            }

            // Still no application path. User Default installation directory
            if (string.IsNullOrEmpty(ApplicationDir))
            {
                ApplicationDir = @"C:\RoboDK\bin\RoboDK.exe";
            }

            // Validate if executable exists
            if (!File.Exists(ApplicationDir))
            {
                throw new FileNotFoundException(ApplicationDir);
            }

            var processStartInfo = new ProcessStartInfo
            {
                FileName = ApplicationDir,
                Arguments = arguments,
                RedirectStandardOutput = true,
                UseShellExecute = false
            };
            Process = Process.Start(processStartInfo);

            // wait for RoboDK to output (stdout) RoboDK is Running. Works after v3.4.0.
            string line = "";
            while (line != null && !line.Contains("RoboDK is Running"))
            {
                line = Process.StandardOutput.ReadLine();
            }

            Process.StandardOutput.Close();
            if (line != null)
            {
                started = true;
            }

            return started;
        }

        private static bool WaitForTcpServerPort(int serverPort, int millisecondsTimeout)
        {
            int sleepTime = 100;
            bool serverPortIsOpen = false;
            while ((serverPortIsOpen == false) && (millisecondsTimeout > 0))
            {
                //TcpConnectionInformation[] tcpConnInfoArray = IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpConnections();
                IPEndPoint[] objEndPoints = System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpListeners();
                foreach (var tcpEndPoint in objEndPoints)
                {
                    if (tcpEndPoint.Port == serverPort)
                    {
                        serverPortIsOpen = true;
                        break;
                    }
                }
                if (serverPortIsOpen == false)
                {
                    Thread.Sleep(sleepTime);
                    millisecondsTimeout -= sleepTime;
                }
            }
            return serverPortIsOpen;
        }

        public void EventsListenClose()
        {
            if (_roboDkEventSource != null)
            {
                _roboDkEventSource.Close();
                _roboDkEventSource = null;
            }
        }

        /// <inheritdoc />
        public IRoboDKEventSource EventsListen()
        {
            if (_roboDkEventSource != null)
            {
                throw new RdkException("event socket already open.");
            }

            var socketEvents = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
            socketEvents.SendTimeout = 1000;
            socketEvents.ReceiveTimeout = 1000;
            try
            {
                socketEvents.Connect(RoboDKServerIpAdress, RoboDKServerPort);
                if (socketEvents.Connected)
                {
                    socketEvents.SendTimeout = DefaultSocketTimeoutMilliseconds;
                    socketEvents.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
                }
            }
            catch //Exception e)
            {
                return null;
            }
            send_line("RDK_EVT", socketEvents);
            send_int(0, socketEvents);
            string response = rec_line(socketEvents);
            int verEvt = rec_int(socketEvents);
            int status = rec_int(socketEvents);
            if (response != "RDK_EVT" || status != 0)
            {
                return null;
            }
            socketEvents.ReceiveTimeout = 3600 * 1000;

            return _roboDkEventSource = new RoboDKEventSource(this, socketEvents);
        }

        /// <inheritdoc />
        public bool SampleRoboDkEvent(EventType evt, IItem itm)
        {
            bool eventReceived = true;

            switch (evt)
            {
                case EventType.SelectionChanged:
                    Console.WriteLine("Event: Selection changed");
                    if (itm.Valid())
                        Console.WriteLine("  -> Selected: " + itm.Name());
                    else
                        Console.WriteLine("  -> Nothing selected");

                    break;

                case EventType.ItemMoved:
                    Console.WriteLine("Event: Item Moved");
                    if (itm.Valid())
                        Console.WriteLine("  -> Moved: " + itm.Name() + " ->\n" + itm.Pose().ToString());
                    else
                        Console.WriteLine("  -> This should never happen");

                    break;

                default:
                    Console.WriteLine("Unknown event " + evt.ToString());
                    eventReceived = false;
                    break;
            }
            return eventReceived;
        }

        /// <inheritdoc />
        public bool EventsLoop()
        {
            Console.WriteLine("Events loop started");
            var eventSource = EventsListen();
            while (eventSource.Connected)
            {
                EventResult eventResult = eventSource.WaitForEvent(timeout: 3600 * 1000);
                SampleRoboDkEvent(eventResult.EventType, eventResult.Item);
            }
            Console.WriteLine("Event loop finished");
            return true;
        }

        /// <inheritdoc />
        public void CloseRoboDK()
        {
            check_connection();
            var command = "QUIT";
            send_line(command);
            check_status();
            _socket.Disconnect(false);
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
        public IItem AddFile(string filename, IItem parent = null)
        {
            if (!File.Exists(filename))
            {
                throw new FileNotFoundException(filename);
            }

            check_connection();
            var command = "Add";
            send_line(command);
            send_line(filename);
            send_item(parent);
            ReceiveTimeout = 3600 * 1000;
            var newitem = rec_item();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
            check_status();
            return newitem;
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
            _socket.ReceiveTimeout = 3600 * 1000;
            var item = rec_item();
            _socket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
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
        public void ShowMessage(string message, bool popup = true)
        {
            check_connection();
            if (popup)
            {
                var command = "ShowMessage";
                send_line(command);
                send_line(message);
                _socket.ReceiveTimeout = 3600 * 1000;
                check_status();
                _socket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
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
            Color clr = color?? Color.FromRgb(127,127,127);
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
            check_connection();
            var command = "Remove";
            send_line(command);
            send_item(new Item(this));
            ReceiveTimeout = 3600 * 1000;
            check_status();
            ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
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
        public bool SetCollisionActivePair(CollisionCheckOptions collisionCheck, IItem item1, IItem item2, int id1 = 0,
            int id2 = 0)
        {
            check_connection();
            var command = "Collision_SetPair";
            send_line(command);
            send_item(item1);
            send_item(item2);
            send_int(id1);
            send_int(id2);
            send_int((int)collisionCheck);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <inheritdoc />
        public bool SetCollisionActivePair(List<CollisionCheckOptions> checkState, List<IItem> item1, List<IItem> item2, List<int> id1 = null, List<int> id2 = null)
        {
            check_connection();
            send_line("Collision_SetPairList");
            int npairs = Math.Min(checkState.Count, Math.Min(item1.Count, item2.Count));
            // pre-allocate send buffer
            // 4: sendIntToBuffer(npairs, buffer);
            // (npairs * 2 * 8) : see Tag1: Send items
            // (npairs * 3 * 4) : see Tag2: send joint id's and checkState
            // 
            List<byte> buffer = new List<byte>(4 + (npairs * 2 * 8) + (npairs * 3 * 4) );
            buffer = sendIntToBuffer(npairs, buffer);
            for (int i = 0; i < npairs; i++)
            {
                // Tag1: Send items
                buffer = sendItemToBuffer(item1[i], buffer);
                buffer = sendItemToBuffer(item2[i], buffer);
                int idok1 = 0;
                int idok2 = 0;
                if (id1 != null && id1.Count > i)
                {
                    idok1 = id1[i];
                }
                if (id2 != null && id2.Count > i)
                {
                    idok2 = id2[i];
                }
                // Tag2: send id's and checkState
                buffer = sendIntToBuffer(idok1, buffer);
                buffer = sendIntToBuffer(idok2, buffer);
                buffer = sendIntToBuffer((int)checkState[i], buffer);
            }
            _socket.SendData(buffer.ToArray());
 
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
        public List<IItem> GetCollisionItems()
        {
            check_connection();
            send_line("Collision_Items");
            int nitems = rec_int();
            List<IItem> itemList = new List<IItem>(nitems);
            for (int i = 0; i < nitems; i++)
            {
                itemList.Add(rec_item());
                int linkId = rec_int();//link id for robot items (ignored)
                int collisionTimes = rec_int();//number of objects it is in collisions with
            }
            check_status();
            return itemList;
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
            send_line(value.ToString());
            check_status();
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
            var xyz = new double[] { 0, 0, 0 };
            rec_xyz(xyz);
            var collision = item.Valid();
            check_status();
            return collision;
        }


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
        public Mat GetViewPose()
        {
            check_connection();
            var command = "G_ViewPose";
            send_line(command);
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
            send_arrayList(param);
            Mat jointsData = new Mat(ndofs, 5);
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
        public void SetInteractiveMode(InteractiveType modeType = InteractiveType.MOVE, DisplayRefType defaultRefFlags = DisplayRefType.DEFAULT, List<IItem> customItems = null, List<InteractiveType> customRefFlags = null)
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



        public void AddTargetJ(IItem pgm, string targetName, double[] joints, IItem robotBase = null, IItem robot = null)
        {
            var target = AddTarget(targetName, robotBase);
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
        }

        #endregion

        #region Protected Methods

        protected virtual void Dispose(bool disposing)
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

        #region Private Methods

        private Socket ConnectToRoboDK(string ipAdress, int port)
        {
            bool connected = false;
            var socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP)
            {
                SendTimeout = 1000,
                ReceiveTimeout = 1000
            };

            try
            {
                socket.Connect(ipAdress, port);
                if (socket.Connected)
                {
                    socket.SendTimeout = DefaultSocketTimeoutMilliseconds;
                    socket.ReceiveTimeout = DefaultSocketTimeoutMilliseconds;
                    connected = true;
                }
            }
            catch (Exception e)
            {
                var s = e.Message;

                //connected = false;
            }

            if (!connected)
            {
                socket.Dispose();
                socket = null;
            }

            return socket;
        }

        #endregion

        #region Internal Methods

        //Returns 1 if connection is valid, returns 0 if connection is invalid
        internal bool is_connected()
        {
            return _socket.Connected;
        }

        /// <summary>
        ///     If we are not connected it will attempt a connection, if it fails, it will throw an error
        /// </summary>
        internal void check_connection()
        {
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
                default:

                    //raise Exception('Problems running function');
                    LastStatusMessage = "Unknown problem running RoboDK API function";
                    throw new RdkException(LastStatusMessage);
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
        internal void send_line(string line, Socket sckt=null)
        {
            if (sckt == null)
                sckt = _socket;

            line = line.Replace('\n', ' '); // one new line at the end only!
            var data = Encoding.UTF8.GetBytes(line + "\n");
            try
            {
                sckt.SendData(data);
            }
            catch
            {
                throw new RdkException("Send line failed.");
            }
        }

        internal string rec_line(Socket sckt = null)
        {
            if (sckt == null)
                sckt = _socket;

            //Receives a string. It reads until if finds LF (\\n)
            var buffer = new byte[1];
            var bytesread = sckt.ReceiveData(buffer, 1, SocketFlags.None);
            var line = "";
            while (bytesread > 0 && buffer[0] != '\n')
            {
                line = line + Encoding.UTF8.GetString(buffer);
                bytesread = sckt.ReceiveData(buffer, 1, SocketFlags.None);
            }

            return line;
        }

        //Sends an item pointer
        internal void send_item(IItem item)
        {
            byte[] bytes;
            if (item == null)
            {
                bytes = BitConverter.GetBytes((ulong)0);
            }
            else
            {
                bytes = BitConverter.GetBytes(item.ItemId);
            }

            if (bytes.Length != 8)
            {
                throw new RdkException("API error");
            }

            Array.Reverse(bytes);
            try
            {
                _socket.SendData(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        // Same as send_item except it will add the data to the provided buffer 
        // and return the buffer as result.
        internal List<byte> sendItemToBuffer(IItem item, List<byte> buffer)
        {
            byte[] bytes;
            if (item == null)
            {
                bytes = BitConverter.GetBytes((ulong)0);
            }
            else
            {
                bytes = BitConverter.GetBytes(item.ItemId);
            }

            if (bytes.Length != 8)
            {
                throw new RdkException("API error");
            }

            Array.Reverse(bytes);
            buffer.AddRange(bytes);
            return buffer;
        }


        //Receives an item pointer
        internal IItem rec_item(Socket sckt = null)
        {
            if (sckt == null)
                sckt = _socket;

            var buffer1 = new byte[8];
            var buffer2 = new byte[4];
            var read1 = sckt.ReceiveData(buffer1, 8, SocketFlags.None);
            var read2 = sckt.ReceiveData(buffer2, 4, SocketFlags.None);
            if (read1 != 8 || read2 != 4)
            {
                return null;
            }

            Array.Reverse(buffer1);
            Array.Reverse(buffer2);
            var item = BitConverter.ToInt64(buffer1, 0);

            //Console.WriteLine("Received item: " + item.ToString());
            var type = (ItemType)BitConverter.ToInt32(buffer2, 0);
            return new Item(this, item, type);
        }

        //Sends an item pointer
        internal void send_ptr(long ptr = 0)
        {
            var bytes = BitConverter.GetBytes(ptr);
            if (bytes.Length != 8)
            {
                throw new RdkException("RoboDK API error");
            }

            Array.Reverse(bytes);
            _socket.SendData(bytes);
        }

        ///Receives a generic pointer
        internal long rec_ptr()
        {
            var bytes = new byte[8];
            var read = _socket.ReceiveData(bytes, 8, SocketFlags.None);
            if (read != 8)
            {
                throw new Exception("Something went wrong");
            }

            Array.Reverse(bytes);
            var ptrH = BitConverter.ToInt64(bytes, 0);
            return ptrH;
        }

        internal void send_pose(Mat pose)
        {
            if (!pose.IsHomogeneous())
            {
                throw new Exception($"Matrix not Homogenous: {pose.Cols}x{pose.Rows}");
            }

            const int nvalues = 16;
            var bytesarray = new byte[8 * nvalues];
            var cnt = 0;
            for (var j = 0; j < pose.Cols; j++)
                for (var i = 0; i < pose.Rows; i++)
                {
                    var onedouble = BitConverter.GetBytes(pose[i, j]);
                    Array.Reverse(onedouble);
                    Array.Copy(onedouble, 0, bytesarray, cnt * 8, 8);
                    cnt = cnt + 1;
                }

            _socket.SendData(bytesarray, 8 * nvalues, SocketFlags.None);
        }

        internal Mat rec_pose()
        {
            var pose = new Mat(4, 4);
            var bytes = new byte[16 * 8];
            var nbytes = _socket.ReceiveData(bytes, 16 * 8, SocketFlags.None);
            if (nbytes != 16 * 8)
            {
                throw new RdkException("Invalid pose sent"); //raise Exception('Problems running function');
            }

            var cnt = 0;
            for (var j = 0; j < pose.Cols; j++)
                for (var i = 0; i < pose.Rows; i++)
                {
                    var onedouble = new byte[8];
                    Array.Copy(bytes, cnt, onedouble, 0, 8);
                    Array.Reverse(onedouble);
                    pose[i, j] = BitConverter.ToDouble(onedouble, 0);
                    cnt = cnt + 8;
                }

            return pose;
        }

        internal void send_xyz(double[] xyzpos)
        {
            for (var i = 0; i < 3; i++)
            {
                var bytes = BitConverter.GetBytes(xyzpos[i]);
                Array.Reverse(bytes);
                _socket.SendData(bytes, 8, SocketFlags.None);
            }
        }

        internal void rec_xyz(double[] xyzpos)
        {
            var bytes = new byte[3 * 8];
            var nbytes = _socket.ReceiveData(bytes, 3 * 8, SocketFlags.None);
            if (nbytes != 3 * 8)
            {
                throw new RdkException("Invalid pose sent"); //raise Exception('Problems running function');
            }

            for (var i = 0; i < 3; i++)
            {
                var onedouble = new byte[8];
                Array.Copy(bytes, i * 8, onedouble, 0, 8);
                Array.Reverse(onedouble);
                xyzpos[i] = BitConverter.ToDouble(onedouble, 0);
            }
        }

        internal void send_int(int number, Socket sckt = null)
        {
            if (sckt == null)
                sckt = _socket;

            var bytes = BitConverter.GetBytes(number);
            Array.Reverse(bytes); // convert from big endian to little endian
            try
            {
                sckt.SendData(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        // Same as send_int except it will add the data to the provided buffer 
        // and returns the buffer as result.
        internal List<byte> sendIntToBuffer(int number, List<byte> buffer)
        {
            var bytes = BitConverter.GetBytes(number);
            // convert from big endian to little endian
            Array.Reverse(bytes); 
            buffer.AddRange(bytes);
            return buffer;
        }

        internal int rec_int(Socket sckt=null)
        {
            if (sckt == null)
                sckt = _socket;
            
            var bytes = new byte[4];
            var read = sckt.ReceiveData(bytes, 4, SocketFlags.None);
            if (read < 4)
            {
                return 0;
            }

            Array.Reverse(bytes); // convert from little endian to big endian
            return BitConverter.ToInt32(bytes, 0);
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
            var bytesarray = new byte[8 * nvalues];
            for (var i = 0; i < nvalues; i++)
            {
                var onedouble = BitConverter.GetBytes(values[i]);
                Array.Reverse(onedouble);
                Array.Copy(onedouble, 0, bytesarray, i * 8, 8);
            }

            _socket.SendData(bytesarray, 8 * nvalues, SocketFlags.None);
        }
        // sends a list of doubles
        internal void send_arrayList(List<double> values)
        {
            double[] values2 = new double[values.Count];
            for (int i = 0; i < values.Count; i++)
            {
                values2[i] = values[i];
            }
            send_array(values2);
        }

        // Receives an array of doubles
        internal double[] rec_array()
        {
            var nvalues = rec_int();
            if (nvalues > 0)
            {
                var values = new double[nvalues];
                var bytes = new byte[nvalues * 8];
                var read = _socket.ReceiveData(bytes, nvalues * 8, SocketFlags.None);
                for (var i = 0; i < nvalues; i++)
                {
                    var onedouble = new byte[8];
                    Array.Copy(bytes, i * 8, onedouble, 0, 8);
                    Array.Reverse(onedouble);
                    values[i] = BitConverter.ToDouble(onedouble, 0);
                }

                return values;
            }

            return null;
        }

        // sends a 2 dimensional matrix
        internal void send_matrix(Mat mat)
        {
            var sendBuffer = new byte[mat.Cols * mat.Rows * sizeof(double) /*8*/];
            send_int(mat.Rows);
            send_int(mat.Cols);
            var index = 0;
            for (var j = 0; j < mat.Cols; j++)
            {
                for (var i = 0; i < mat.Rows; i++)
                {
                    var bytes = BitConverter.GetBytes(mat[i, j]);
                    // Convert to big Endian.
                    // Factor 2 performance gain compared to Array.Reverse(onedouble);
                    sendBuffer[index++] = bytes[7];
                    sendBuffer[index++] = bytes[6];
                    sendBuffer[index++] = bytes[5];
                    sendBuffer[index++] = bytes[4];
                    sendBuffer[index++] = bytes[3];
                    sendBuffer[index++] = bytes[2];
                    sendBuffer[index++] = bytes[1];
                    sendBuffer[index++] = bytes[0];
                }
            }

            _socket.SendData(sendBuffer, sendBuffer.Length, SocketFlags.None);
        }

        // receives a 2 dimensional matrix (nxm)
        internal Mat rec_matrix()
        {
            var size1 = rec_int();
            var size2 = rec_int();
            var recvsize = size1 * size2 * 8;
            var bytes = new byte[recvsize];
            var mat = new Mat(size1, size2);
            var bufferSize = 256;
            var received = 0;
            if (recvsize > 0)
            {
                var toReceive = Math.Min(recvsize, bufferSize);
                while (toReceive > 0)
                {
                    var nbytesok = _socket.ReceiveData(bytes, received, toReceive, SocketFlags.None);
                    if (nbytesok <= 0)
                    {
                        throw new RdkException(
                            "Can't receive matrix properly"); //raise Exception('Problems running function');
                    }

                    received = received + nbytesok;
                    toReceive = Math.Min(recvsize - received, bufferSize);
                }
            }

            var cnt = 0;
            for (var j = 0; j < mat.Cols; j++)
                for (var i = 0; i < mat.Rows; i++)
                {
                    var onedouble = new byte[8];
                    Array.Copy(bytes, cnt, onedouble, 0, 8);
                    Array.Reverse(onedouble);
                    mat[i, j] = BitConverter.ToDouble(onedouble, 0);
                    cnt = cnt + 8;
                }

            return mat;
        }

        // private move type, to be used by public methods (MoveJ  and MoveL)
        internal void MoveX(IItem target, double[] joints, Mat matTarget, IItem itemrobot, int movetype,
            bool blocking = true)
        {
            itemrobot.WaitMove();
            var command = "MoveX";
            send_line(command);
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
                itemrobot.WaitMove();
            }
        }

        // private move type, to be used by public methods (MoveJ  and MoveL)
        internal void moveC_private(IItem target1, double[] joints1, Mat matTarget1, IItem target2, double[] joints2,
            Mat matTarget2, IItem itemrobot, bool blocking = true)
        {
            itemrobot.WaitMove();
            var command = "MoveC";
            send_line(command);
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
                itemrobot.WaitMove();
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
            bool useNewVersion = false; // this flag will be soon updated to support build/version check and prevent calling unsupported functions by RoboDK.
            if (useNewVersion)
            {
                send_line("RDK_API");
                send_int(0);
                string response = rec_line();
                int verApi = rec_int();
                RoboDKBuild = rec_int();
                check_status();
                return response == "RDK_API";
            } else {
                send_line("CMD_START");
                var startParameter = string.Format($"{Convert.ToInt32(SafeMode)} {Convert.ToInt32(AutoUpdate)}");
                send_line(startParameter);
                var response = rec_line();
                if (response == "READY")
                {
                    return true;
                }
            }
            return false;
        }

        internal bool RequireBuild(int buildRequired)
        {
            if (RoboDKBuild == 0)
                return true;
        
            if (RoboDKBuild < buildRequired)
                throw new Exception("This function is unavailable. Update RoboDK to use this function through the API.");
    
            return true;
        }


        #endregion

        public sealed class RoboDKLink : IDisposable
        {
            private RoboDK _roboDK;

            public IRoboDK RoboDK => _roboDK;

            public RoboDKLink(IRoboDK roboDK)
            {
                _roboDK = (RoboDK)roboDK.NewLink();
            }

            public void Dispose()
            {
                var tempRoboDK = _roboDK;
                _roboDK = null;
                tempRoboDK._socket.Close();
                tempRoboDK._socket.Dispose();
            }
        }

        private sealed class RoboDKEventSource : IRoboDKEventSource
        {
            private readonly RoboDK _roboDK;
            private Socket _socketEvents;

            public RoboDKEventSource(RoboDK roboDK, Socket socketEvents)
            {
                _roboDK = roboDK;
                _socketEvents = socketEvents;
            }

            public bool Connected => _socketEvents.Connected;

            public EventResult WaitForEvent(int timeout = 1000)
            {
                if (_socketEvents == null)
                {
                    throw new RdkException("Event channel has already been closed");
                }

                try
                {
                    _socketEvents.ReceiveTimeout = timeout;
                    var eventType = (EventType)_roboDK.rec_int(_socketEvents);
                    var item = _roboDK.rec_item(_socketEvents);
                    return EventResult.Create(eventType, item);
                }
                catch (Exception)
                {
                    // Todo: ignored
                }

                return EventResult.None;
            }

            public void Close()
            {
                if (_socketEvents != null)
                {
                    _socketEvents.Close();
                    _socketEvents = null;
                }
            }
        }
    }

    internal static class RoboDKAsyncSendReceive
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

        internal static int ReceiveDataTask(this Socket s, byte[] data, int offset, int len, SocketFlags flags)
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

        internal static int ReceiveData(this Socket s, byte[] data, int offset, int len, SocketFlags flags)
        {
            // Only execute as Task if we run on the main UI Thread
            if (Thread.CurrentThread == System.Windows.Application.Current?.Dispatcher?.Thread )
            {
                // TASK.RUN
                var receiveTask = Task.Run(() => ReceiveDataTask(s, data, offset, len, flags));
                receiveTask.Wait();
                return receiveTask.Result;
            }
            else
            {
                // Any other background thread. Call receive synchronously
                return ReceiveDataTask(s, data, offset, len, flags);
            }

        }

        internal static int ReceiveData(this Socket s, byte[] data, int len, SocketFlags flags)
        {
            return s.ReceiveData(data, 0, len, flags);
        }
    }
}
