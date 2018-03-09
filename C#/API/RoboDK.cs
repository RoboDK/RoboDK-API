#region Namespaces

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net.Sockets;
using System.Text;
using Microsoft.Win32;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    /// <summary>
    ///     This class is the link to allows to create macros and automate Robodk.
    ///     Any interaction is made through \"items\" (Item() objects). An item is an object in the
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

        #endregion

        #region Constructors

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   

        /// <summary>
        ///     Creates a link with RoboDK
        /// </summary>
        /// <param name="robodk_ip"></param>
        /// <param name="start_hidden"></param>
        /// <param name="com_port"></param>
        public RoboDK(string robodk_ip = "localhost", bool start_hidden = false, int com_port = -1, string args = "",
            string path = "")
        {
            //A connection is attempted upon creation of the object"""
            if (robodk_ip != "")
                IP = robodk_ip;
            START_HIDDEN = start_hidden;
            if (com_port > 0)
            {
                PORT_FORCED = com_port;
                PORT_START = com_port;
                PORT_END = com_port;
            }

            if (path != "")
                ApplicationDir = path;
            if (args != "")
                ARGUMENTS = args;
            Connect();
        }

        #endregion

        #region Properties

        /// <summary>
        ///     timeout for communication, in miliseconds
        /// </summary>
        internal int TIMEOUT { get; private set; } = 10 * 1000;

        /// <summary>
        ///     arguments to provide to RoboDK on startup
        /// </summary>
        private string ARGUMENTS { get; } = "";

        /// <summary>
        ///     checks that provided items exist in memory
        /// </summary>
        private int SAFE_MODE { get; set; } = 1;

        /// <summary>
        ///     if AUTO_UPDATE is zero, the scene is rendered after every function call
        /// </summary>
        private int AUTO_UPDATE { get; set; }

        /// <summary>
        ///     IP address of the simulator (localhost if it is the same computer),
        ///     otherwise, use RL = Robolink('yourip') to set to a different IP
        /// </summary>
        private string IP { get; } = "localhost";

        /// <summary>
        ///     port to start looking for app connection
        /// </summary>
        private int PORT_START { get; } = 20500;

        /// <summary>
        ///     port to stop looking for app connection
        /// </summary>
        private int PORT_END { get; } = 20500;

        /// <summary>
        ///     forces to start hidden. ShowRoboDK must be used to show the window
        /// </summary>
        private bool START_HIDDEN { get; }

        /// <summary>
        ///     port where connection succeeded
        /// </summary>
        private int PORT { get; set; } = -1;

        /// <summary>
        ///     port to force RoboDK to start listening
        /// </summary>
        private int PORT_FORCED { get; } = -1;

        public int ReceiveTimeout
        {
            get { return _socket.ReceiveTimeout; }
            set { _socket.ReceiveTimeout = value; }
        }

        public Process Process { get; private set; } // pointer to the process

        public string ApplicationDir { get; private set; } =
            ""; // file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK

        #endregion

        #region Public Methods

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        ///     Checks if the object is currently linked to RoboDK
        /// </summary>
        /// <returns></returns>
        public bool Connected()
        {
            //return _socket.Connected;//does not work well
            if (_socket == null)
                return false;
            var part1 = _socket.Poll(1000, SelectMode.SelectRead);
            var part2 = _socket.Available == 0;
            if (part1 && part2)
                return false;
            return true;
        }

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        public void Disconnect()
        {
            if (_socket != null && _socket.Connected)
                _socket.Disconnect(false);
        }

        /// <summary>
        ///     Starts the link with RoboDK (automatic upon creation of the object)
        /// </summary>
        /// <returns>True if connected; False otherwise</returns>
        public bool Connect()
        {
            //Establishes a connection with robodk. robodk must be running, otherwise, the variable APPLICATION_DIR must be set properly.
            var connected = false;
            int port;
            for (var i = 0; i < 2; i++)
            {
                for (port = PORT_START; port <= PORT_END; port++)
                {
                    _socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
                    //_socket = new Socket(SocketType.Stream, ProtocolType.IPv4);
                    _socket.SendTimeout = 1000;
                    _socket.ReceiveTimeout = 1000;
                    try
                    {
                        _socket.Connect(IP, port);
                        connected = is_connected();
                        if (connected)
                        {
                            _socket.SendTimeout = TIMEOUT;
                            _socket.ReceiveTimeout = TIMEOUT;
                            break;
                        }
                    }
                    catch (Exception e)
                    {
                        var s = e.Message;
                        //connected = false;
                    }
                }

                if (connected)
                {
                    PORT = port;
                    break;
                }

                if (IP != "localhost")
                    break;
                var arguments = "";
                if (PORT_FORCED > 0)
                    arguments = "/PORT=" + PORT_FORCED + " " + arguments;
                if (START_HIDDEN)
                    arguments = "/NOSPLASH /NOSHOW /HIDDEN " + arguments;
                if (ARGUMENTS != "")
                    arguments = arguments + ARGUMENTS;
                if (ApplicationDir == "")
                {
                    string install_path = null;

                    // retrieve install path from the registry:
                    /*RegistryKey localKey = RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, RegistryView.Registry64);
                    localKey = localKey.OpenSubKey(@"SOFTWARE\RoboDK");
                    if (localKey != null)
                    {
                        install_path = localKey.GetValue("INSTDIR").ToString();
                        if (install_path != null)
                        {
                            APPLICATION_DIR = install_path + "\\bin\\RoboDK.exe";
                        }
                    }*/
                    var bits = IntPtr.Size * 8;
                    using (var hklm = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var regKey = hklm.OpenSubKey(@"SOFTWARE\RoboDK"))
                    {
                        if (regKey != null)
                        {
                            // key now points to the 64-bit key
                            install_path = regKey.GetValue("INSTDIR").ToString();
                            if (!string.IsNullOrEmpty(install_path))
                                ApplicationDir = install_path + "\\bin\\RoboDK.exe";
                        }
                    }
                }

                if (ApplicationDir == "")
                    ApplicationDir = "C:/RoboDK/bin/RoboDK.exe";
                Process = Process.Start(ApplicationDir, arguments);
                // wait for the process to get started
                Process.WaitForInputIdle(10000);
            }

            if (connected && !Set_connection_params())
            {
                connected = false;
                Process = null;
            }

            return connected;
        }

        /// <summary>
        ///     Closes RoboDK window and finishes RoboDK execution
        /// </summary>
        public void CloseRoboDK()
        {
            check_connection();
            var command = "QUIT";
            send_line(command);
            check_status();
            _socket.Disconnect(false);
            Process = null;
        }

        public Item AddStation(string name = "New station")
        {
            return null;
        }

        /// <summary>
        ///     Set the state of the RoboDK window
        /// </summary>
        /// <param name="windowState"></param>
        public void SetWindowState(WindowState windowState = WindowState.Normal)
        {
            check_connection();
            var command = "S_WindowState";
            send_line(command);
            send_int((int) windowState);
            check_status();
        }

        /////////////// Add More methods

        /// <summary>
        ///     Loads a file and attaches it to parent. It can be any file supported by robodk.
        /// </summary>
        /// <param name="filename">absolute path of the file</param>
        /// <param name="parent">parent to attach. Leave empty for new stations or to load an object at the station root</param>
        /// <returns>Newly added object. Check with item.Valid() for a successful load</returns>
        public Item AddFile(string filename, Item parent = null)
        {
            if (!File.Exists(filename))
                throw new FileNotFoundException(filename);

            check_connection();
            var command = "Add";
            send_line(command);
            send_line(filename);
            send_item(parent);
            var newitem = rec_item();
            check_status();
            return newitem;
        }


        /// <summary>
        ///     Adds a new target that can be reached with a robot.
        /// </summary>
        /// <param name="name">name of the target</param>
        /// <param name="itemparent">parent to attach to (such as a frame)</param>
        /// <param name="itemrobot">main robot that will be used to go to self target</param>
        /// <returns>the new target created</returns>
        public Item AddTarget(string name, Item itemparent = null, Item itemrobot = null)
        {
            check_connection();
            var command = "Add_TARGET";
            send_line(command);
            send_line(name);
            send_item(itemparent);
            send_item(itemrobot);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <summary>
        ///     Adds a new Frame that can be referenced by a robot.
        /// </summary>
        /// <param name="name">name of the program</param>
        /// <param name="itemparent">robot that will be used</param>
        /// <returns>the new program created</returns>
        public Item AddProgram(string name, Item itemrobot = null)
        {
            check_connection();
            var command = "Add_PROG";
            send_line(command);
            send_line(name);
            send_item(itemrobot);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <summary>
        ///     Renders the scene. This function turns off rendering unless always_render is set to true.
        /// </summary>
        /// <param name="alwaysRender"></param>
        public void Render(bool alwaysRender = false)
        {
            var autoRender = !alwaysRender;
            check_connection();
            var command = "Render";
            send_line(command);
            send_int(autoRender ? 1 : 0);
            check_status();
        }

        //Sends a string of characters with a \\n
        public void send_line(string line)
        {
            line = line.Replace('\n', ' '); // one new line at the end only!
            var data = Encoding.UTF8.GetBytes(line + "\n");
            try
            {
                _socket.Send(data);
            }
            catch
            {
                throw new RdkException("Send line failed.");
            }
        }


        // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        // public methods
        /// <summary>
        ///     Returns an item by its name. If there is no exact match it will return the last closest match.
        /// </summary>
        /// <param name="name">Item name</param>
        /// <param name="itemType">Filter by itemType</param>
        /// <returns></returns>
        public Item GetItemByName(string name, ItemType itemType = ItemType.Any)
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
                var type = (int) itemType;
                command = "G_Item2";
                send_line(command);
                send_line(name);
                send_int(type);
            }

            var item = rec_item();
            check_status();
            return item;
        }

        /// <summary>
        ///     Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
        ///     Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
        /// </summary>
        /// <param name="filter">ITEM_TYPE</param>
        /// <returns></returns>
        public string[] getItemListNames(int filter = -1)
        {
            check_connection();
            string command;
            if (filter < 0)
            {
                command = "G_List_Items";
                send_line(command);
            }
            else
            {
                command = "G_List_Items_Type";
                send_line(command);
                send_int(filter);
            }

            var numitems = rec_int();
            var listnames = new string[numitems];
            for (var i = 0; i < numitems; i++)
                listnames[i] = rec_line();
            check_status();
            return listnames;
        }

        /// <summary>
        ///     Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
        ///     Optionally, use a filter to return items of a specific type
        /// </summary>
        /// <param name="filter">Only return items of this type</param>
        /// <returns>List of Items</returns>
        public List<Item> GetItemList(ItemType filter = ItemType.Any)
        {
            check_connection();
            string command;
            if (filter == ItemType.Any)
            {
                command = "G_List_Items_ptr";
                send_line(command);
            }
            else
            {
                var itemFilter = (int) filter;
                command = "G_List_Items_Type_ptr";
                send_line(command);
                send_int(itemFilter);
            }

            var numitems = rec_int();
            var listitems = new List<Item>(numitems);
            for (var i = 0; i < numitems; i++)
                listitems.Add(rec_item());
            check_status();
            return listitems;
        }

        /////// add more methods

        /// <summary>
        ///     Shows a RoboDK popup to select one object from the open station.
        ///     An item type can be specified to filter desired items. If no type is specified, all items are selectable.
        /// </summary>
        /// <param name="message">Message to pop up</param>
        /// <param name="itemtype">optionally filter by RoboDK.ITEM_TYPE_*</param>
        /// <returns></returns>
        public Item ItemUserPick(string message = "Pick one item", int itemtype = -1)
        {
            check_connection();
            var command = "PickItem";
            send_line(command);
            send_line(message);
            send_int(itemtype);
            _socket.ReceiveTimeout = 3600 * 1000;
            var item = rec_item();
            _socket.ReceiveTimeout = TIMEOUT;
            check_status();
            return item;
        }

        /// <summary>
        ///     Shows or raises the RoboDK window
        /// </summary>
        public void ShowRoboDK()
        {
            check_connection();
            var command = "RAISE";
            send_line(command);
            check_status();
        }

        /// <summary>
        ///     Hides the RoboDK window
        /// </summary>
        public void HideRoboDK()
        {
            check_connection();
            var command = "HIDE";
            send_line(command);
            check_status();
        }

        /// <summary>
        ///     Update the RoboDk Window flags.
        ///     RoboDK flags allow defining how much access the user has to RoboDK features.
        /// </summary>
        /// <param name="flags">RoboDk Window Flags</param>
        public void SetWindowFlags(WindowFlags flags = WindowFlags.All)
        {
            check_connection();
            var command = "S_RoboDK_Rights";
            send_line(command);
            send_int((int) flags);
            check_status();
        }

        /// <summary>
        ///     Show a message in RoboDK (it can be blocking or non blocking in the status bar)
        /// </summary>
        /// <param name="message">Message to display</param>
        /// <param name="popup">Set to true to make the message blocking or set to false to make it non blocking</param>
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
                _socket.ReceiveTimeout = TIMEOUT;
            }
            else
            {
                var command = "ShowMessageStatus";
                send_line(command);
                send_line(message);
                check_status();
            }
        }


        /////////////// Add More methods

        /// <summary>
        ///     Save an item to a file. If no item is provided, the open station is saved.
        /// </summary>
        /// <param name="filename">absolute path to save the file</param>
        /// <param name="itemsave">object or station to save. Leave empty to automatically save the current station.</param>
        public void Save(string filename, Item itemsave = null)
        {
            check_connection();
            var command = "Save";
            send_line(command);
            send_line(filename);
            send_item(itemsave);
            check_status();
        }

        /// <summary>
        ///     Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can
        ///     be provided optionally.
        /// </summary>
        /// <param name="trianglePoints">
        ///     List of vertices grouped by triangles (3xN or 6xN matrix, N must be multiple of 3 because
        ///     vertices must be stacked by groups of 3)
        /// </param>
        /// <param name="addTo">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
        /// <param name="shapeOverride">Set to true to replace any other existing geometry</param>
        /// <returns></returns>
        public Item AddShape(Mat trianglePoints, Item addTo = null, bool shapeOverride = false)
        {
            check_connection();
            send_line("AddShape2");
            send_matrix(trianglePoints);
            send_item(addTo);
            send_int(shapeOverride ? 1 : 0);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <summary>
        ///     Adds a curve provided point coordinates.
        ///     The provided points must be a list of vertices.
        ///     A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="curvePoints">matrix 3xN or 6xN -> N must be multiple of 3</param>
        /// <param name="referenceObject">object to add the curve and/or project the curve to the surface</param>
        /// <param name="addToRef">
        ///     If True, the curve will be added as part of the object in the RoboDK item tree (a reference
        ///     object must be provided)
        /// </param>
        /// <param name="projectionType">
        ///     Type of projection. For example:  ProjectionType.AlongNormalRecalc will project along the
        ///     point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>added object/curve (null if failed)</returns>
        public Item AddCurve(Mat curvePoints, Item referenceObject = null, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            check_connection();
            var command = "AddWire";
            send_line(command);
            send_matrix(curvePoints);
            send_item(referenceObject);
            send_int(addToRef ? 1 : 0);
            send_int((int) projectionType);
            var newitem = rec_item();
            check_status();
            return newitem;
        }

        /// <summary>
        ///     Projects a point given its coordinates.
        ///     The provided points must be a list of [XYZ] coordinates.
        ///     Optionally, a vertex normal can be provided [XYZijk].
        /// </summary>
        /// <param name="points">matrix 3xN or 6xN -> list of points to project</param>
        /// <param name="objectProject">object to project</param>
        /// <param name="projectionType">
        ///     Type of projection. For example: ProjectionType.AlongNormalRecalc will project along the
        ///     point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>
        ///     It returns the projected points as a list of points (empty matrix if failed).
        /// </returns>
        public Mat ProjectPoints(Mat points, Item objectProject,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc)
        {
            check_connection();
            var command = "ProjectPoints";
            send_line(command);
            send_matrix(points);
            send_item(objectProject);
            send_int((int) projectionType);
            var projectedPoints = rec_matrix();
            check_status();
            return projectedPoints;
        }

        /// <summary>
        ///     Closes the current station without suggesting to save
        /// </summary>
        public void CloseStation()
        {
            check_connection();
            var command = "Remove";
            send_line(command);
            send_item(new Item(this));
            check_status();
        }

        /// <summary>
        ///     Adds a new Frame that can be referenced by a robot.
        /// </summary>
        /// <param name="name">name of the reference frame</param>
        /// <param name="itemparent">parent to attach to (such as the robot base frame)</param>
        /// <returns>the new reference frame created</returns>
        public Item AddFrame(string name, Item itemparent = null)
        {
            check_connection();
            var command = "Add_FRAME";
            send_line(command);
            send_line(name);
            send_item(itemparent);
            var newitem = rec_item();
            check_status();
            return newitem;
        }


        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        /// <summary>
        ///     Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific
        ///     robot. If the program exists it will also run the program in simulate mode.
        /// </summary>
        /// <param name="function_w_params">Function name with parameters (if any)</param>
        /// <returns></returns>
        public int RunProgram(string function_w_params)
        {
            return RunCode(function_w_params, true);
        }

        /// <summary>
        ///     Adds code to run in the program output. If the program exists it will also run the program in simulate mode.
        /// </summary>
        /// <param name="code"></param>
        /// <param name="code_is_fcn_call"></param>
        /// <returns></returns>
        public int RunCode(string code, bool code_is_fcn_call = false)
        {
            check_connection();
            var command = "RunCode";
            send_line(command);
            send_int(code_is_fcn_call ? 1 : 0);
            send_line(code);
            var prog_status = rec_int();
            check_status();
            return prog_status;
        }

        /// <summary>
        ///     Shows a message or a comment in the output robot program.
        /// </summary>
        /// <param name="message"></param>
        /// <param name="message_is_comment"></param>
        public void RunMessage(string message, bool message_is_comment = false)
        {
            check_connection();
            var command = "RunMessage";
            send_line(command);
            send_int(message_is_comment ? 1 : 0);
            send_line(message);
            check_status();
        }

        /// <summary>
        ///     Returns (1/True) if objectInside is inside the objectParent
        /// </summary>
        /// <param name="objectInside"></param>
        /// <param name="objectParent"></param>
        /// <returns></returns>
        public bool IsInside(Item objectInside, Item objectParent)
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

        /// <summary>
        ///     Set collision checking ON or OFF (COLLISION_OFF/COLLISION_OFF) according to the collision map. If collision check
        ///     is activated it returns the number of pairs of objects that are currently in a collision state.
        /// </summary>
        /// <param name="collisionCheck"></param>
        /// <returns>Number of pairs of objects in a collision state</returns>
        public int SetCollisionActive(CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOn)
        {
            check_connection();
            send_line("Collision_SetState");
            send_int((int) collisionCheck);
            var ncollisions = rec_int();
            check_status();
            return ncollisions;
        }

        /// <summary>
        ///     Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. This allows altering
        ///     the collision map for Collision checking.
        ///     Specify the link id for robots or moving mechanisms (id 0 is the base).
        /// </summary>
        /// <param name="collisionCheck">Set to COLLISION_ON or COLLISION_OFF</param>
        /// <param name="item1">Item 1</param>
        /// <param name="item2">Item 2</param>
        /// <param name="id1">Joint id for Item 1 (if Item 1 is a robot or a mechanism)</param>
        /// <param name="id2">Joint id for Item 2 (if Item 2 is a robot or a mechanism)</param>
        /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
        public bool SetCollisionActivePair(CollisionCheckOptions collisionCheck, Item item1, Item item2, int id1 = 0,
            int id2 = 0)
        {
            check_connection();
            var command = "Collision_SetPair";
            send_line(command);
            send_item(item1);
            send_item(item2);
            send_int(id1);
            send_int(id2);
            send_int((int) collisionCheck);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <summary>
        ///     Returns the number of pairs of objects that are currently in a collision state.
        /// </summary>
        /// <returns></returns>
        public int Collisions()
        {
            check_connection();
            var command = "Collisions";
            send_line(command);
            var ncollisions = rec_int();
            check_status();
            return ncollisions;
        }

        /// <summary>
        ///     Returns 1 if item1 and item2 collided. Otherwise returns 0.
        /// </summary>
        /// <param name="item1"></param>
        /// <param name="item2"></param>
        /// <returns></returns>
        public int Collision(Item item1, Item item2)
        {
            check_connection();
            var command = "Collided";
            send_line(command);
            send_item(item1);
            send_item(item2);
            var ncollisions = rec_int();
            check_status();
            return ncollisions;
        }

        /// <summary>
        ///     Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is
        ///     0.001 times the real speed. Set to a high value (>100) for fast simulation results.
        /// </summary>
        /// <param name="speed"></param>
        public void setSimulationSpeed(double speed)
        {
            check_connection();
            var command = "SimulateSpeed";
            send_line(command);
            send_int((int) (speed * 1000.0));
            check_status();
        }

        /// <summary>
        ///     Gets the current simulation speed. Set the speed to 1 for a real-time simulation.
        /// </summary>
        /// <returns></returns>
        public double SimulationSpeed()
        {
            check_connection();
            var command = "GetSimulateSpeed";
            send_line(command);
            var speed = rec_int() / 1000.0;
            check_status();
            return speed;
        }

        /// <summary>
        ///     Sets the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions
        ///     (run_mode=1=RUNMODE_SIMULATE).
        ///     Setting the run_mode to RUNMODE_QUICKVALIDATE allows performing a quick check to see if the path is feasible.
        ///     if robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
        /// </summary>
        /// <param name="runMode">
        ///     int = RUNMODE
        ///     RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
        ///     RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
        ///     RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
        ///     RUNMODE_RUN_REAL=4        moves the real robot is it is connected
        /// </param>
        public void SetRunMode(RunMode runMode = RunMode.Simulate)
        {
            check_connection();
            var command = "S_RunMode";
            send_line(command);
            send_int((int) runMode);
            check_status();
        }

        /// <summary>
        ///     Returns the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions
        ///     (run_mode=1)
        /// </summary>
        /// <returns>
        ///     int = RUNMODE
        ///     RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
        ///     RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
        ///     RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
        ///     RUNMODE_RUN_REAL=4        moves the real robot is it is connected
        /// </returns>
        public RunMode GetRunMode()
        {
            check_connection();
            var command = "G_RunMode";
            send_line(command);
            var runMode = (RunMode) rec_int();
            check_status();
            return runMode;
        }

        /// <summary>
        ///     Gets all the user parameters from the open RoboDK station.
        ///     The parameters can also be modified by right clicking the station and selecting "shared parameters"
        ///     User parameters can be added or modified by the user
        /// </summary>
        /// <returns>list of pairs of strings as parameter-value (list of a list)</returns>
        public List<List<string>> getParams()
        {
            check_connection();
            var command = "G_Params";
            send_line(command);
            var paramlist = new List<List<string>>();
            var nparam = rec_int();
            for (var i = 0; i < nparam; i++)
            {
                var param = rec_line();
                var value = rec_line();

                var param_value = new List<string>();
                param_value.Add(param);
                param_value.Add(value);
                paramlist.Add(param_value);
            }

            check_status();
            return paramlist;
        }

        /// <summary>
        ///     Gets a global or a user parameter from the open RoboDK station.
        ///     The parameters can also be modified by right clicking the station and selecting "shared parameters"
        ///     Some available parameters:
        ///     PATH_OPENSTATION = folder path of the current .stn file
        ///     FILE_OPENSTATION = file path of the current .stn file
        ///     PATH_DESKTOP = folder path of the user's folder
        ///     Other parameters can be added or modified by the user
        /// </summary>
        /// <param name="param">RoboDK parameter</param>
        /// <returns>value</returns>
        public string getParam(string param)
        {
            check_connection();
            var command = "G_Param";
            send_line(command);
            send_line(param);
            var value = rec_line();
            if (value.StartsWith("UNKNOWN "))
                value = null;
            check_status();
            return value;
        }

        /// <summary>
        ///     Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be
        ///     added to the station.
        ///     The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// </summary>
        /// <param name="param">RoboDK parameter</param>
        /// <param name="value">value</param>
        /// <returns></returns>
        public void setParam(string param, string value)
        {
            check_connection();
            var command = "S_Param";
            send_line(command);
            send_line(param);
            send_line(value);
            check_status();
        }


        /// <summary>
        ///     Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the
        ///     laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
        /// </summary>
        /// <param name="estimate"></param>
        /// <param name="search">
        ///     Returns the XYZ coordinates of the target (in mm). If the target was not found it retuns a null
        ///     pointer.
        /// </param>
        /// <returns></returns>
        public double[] LaserTracker_Measure(double[] estimate, bool search = false)
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
                return null;
            return xyz;
        }

        /// <summary>
        ///     Takes a measurement with the C-Track stereocamera. It returns two poses, the base reference frame and the measured
        ///     object reference frame.Status is 0 if measurement succeeded.
        /// </summary>
        /// <param name="pose1">Pose of the measurement reference</param>
        /// <param name="pose2">Pose of the tool measurement</param>
        /// <param name="npoints1">number of visible targets for the measurement pose</param>
        /// <param name="npoints2">number of visible targets for the tool pose</param>
        /// <param name="time">time stamp in milliseconds</param>
        /// <param name="status">Status is 0 if measurement succeeded</param>
        public void StereoCamera_Measure(out Mat pose1, out Mat pose2, out int npoints1, out int npoints2, out int time,
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

        /// <summary>
        ///     Checks the collision between a line and any objects in the station. The line is composed by 2 points.
        ///     Returns the collided item. Use Item.Valid() to check if there was a valid collision.
        /// </summary>
        /// <param name="p1">start point of the line</param>
        /// <param name="p2">end point of the line</param>
        /// <param name="ref_abs">Reference of the two points with respect to the absolute station reference.</param>
        /// <param name="xyz_collision">Collided point.</param>
        /// <summary>
        ///     Checks the collision between a line and any objects in the station. The line is composed by 2 points.
        /// </summary>
        /// <param name="p1">Start point [x,y,z] of the line</param>
        /// <param name="p2">Ebd point [x,y,z] of the line</param>
        /// <returns>Collision (true or false)</returns>
        public bool Collision_Line(double[] p1, double[] p2)
        {
            check_connection();
            var command = "CollisionLine";
            send_line(command);
            send_xyz(p1);
            send_xyz(p2);
            var item = rec_item();
            var xyz = new double[3] {0, 0, 0};
            rec_xyz(xyz);
            var collision = item.Valid();
            check_status();
            return collision;
        }

        /// <summary>
        ///     Returns the current joints of a list of robots.
        /// </summary>
        /// <param name="robot_item_list">list of robot items</param>
        /// <returns>list of robot joints (double x nDOF)</returns>
        public double[][] Joints(Item[] robot_item_list)
        {
            check_connection();
            var command = "G_ThetasList";
            send_line(command);
            var nrobs = robot_item_list.Length;
            send_int(nrobs);
            var joints_list = new double[nrobs][];
            for (var i = 0; i < nrobs; i++)
            {
                send_item(robot_item_list[i]);
                joints_list[i] = rec_array();
            }

            check_status();
            return joints_list;
        }

        /// <summary>
        ///     Sets the current robot joints for a list of robot items and a list of a set of joints.
        /// </summary>
        /// <param name="robot_item_list">list of robot items</param>
        /// <param name="joints_list">list of robot joints (double x nDOF)</param>
        public void setJoints(Item[] robot_item_list, double[][] joints_list)
        {
            var nrobs = Math.Min(robot_item_list.Length, joints_list.Length);
            check_connection();
            var command = "S_ThetasList";
            send_line(command);
            send_int(nrobs);
            for (var i = 0; i < nrobs; i++)
            {
                send_item(robot_item_list[i]);
                send_array(joints_list[i]);
            }

            check_status();
        }

        /// <summary>
        ///     Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated,
        ///     provide joint values to maximize accuracy.
        /// </summary>
        /// <param name="posesJoints">matrix of poses in a given format or a list of joints</param>
        /// <param name="errorStats">stats[mean, standard deviation, max] - Output error stats summary</param>
        /// <param name="format">Euler format. Optionally, use EulerType.JointFormat and provide the robot.</param>
        /// <param name="algorithm">type of algorithm (by point, plane, ...)</param>
        /// <param name="robot">Robot used for calibration (if using joint values)</param>
        /// <returns>TCP as [x, y, z] - calculated TCP</returns>
        public double[] CalibrateTool(Mat posesJoints, out double[] errorStats,
            EulerType format = EulerType.EulerRxRyRz,
            TcpCalibrationType algorithm = TcpCalibrationType.CalibrateTcpByPoint, Item robot = null)
        {
            check_connection();
            var command = "CalibTCP2";
            send_line(command);
            send_matrix(posesJoints);
            send_int((int) format);
            send_int((int) algorithm);
            send_item(robot);
            var tcp = rec_array();
            errorStats = rec_array();
            var errorGraph = rec_matrix();
            check_status();
            return tcp;
            //errors = errors[:, 1].tolist()
        }

        /// <summary>
        ///     Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide
        ///     joint values to maximize accuracy.
        /// </summary>
        /// <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints</param>
        /// <param name="method">type of algorithm(by point, plane, ...)</param>
        /// <param name="useJoints">use points or joint values. The robot item must be provided if joint values is used.</param>
        /// <param name="robot"></param>
        /// <returns></returns>
        public Mat CalibrateReference(Mat joints,
            ReferenceCalibrationType method = ReferenceCalibrationType.Frame3P_P1OnX,
            bool useJoints = false, Item robot = null)
        {
            check_connection();
            var command = "CalibFrame";
            send_line(command);
            send_matrix(joints);
            send_int(useJoints ? -1 : 0);
            send_int((int) method);
            send_item(robot);
            var referencePose = rec_pose();
            var errorStats = rec_array();
            check_status();
            //errors = errors[:, 1].tolist()
            return referencePose;
        }

        /// <summary>
        ///     Defines the name of the program when the program is generated. It is also possible to specify the name of the post
        ///     processor as well as the folder to save the program.
        ///     This method must be called before any program output is generated (before any robot movement or other instruction).
        /// </summary>
        /// <param name="progname">name of the program</param>
        /// <param name="defaultfolder">folder to save the program, leave empty to use the default program folder</param>
        /// <param name="postprocessor">
        ///     name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is
        ///     possible to provide "Fanuc_post.py" or simply "Fanuc_post")
        /// </param>
        /// <param name="robot">Robot to link</param>
        /// <returns></returns>
        public int ProgramStart(string progname, string defaultfolder = "", string postprocessor = "",
            Item robot = null)
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

        /// <summary>
        ///     Set the pose of the wold reference frame with respect to the view (camera/screen)
        /// </summary>
        /// <param name="pose"></param>
        public void setViewPose(Mat pose)
        {
            check_connection();
            var command = "S_ViewPose";
            send_line(command);
            send_pose(pose);
            check_status();
        }

        /// <summary>
        ///     Get the pose of the wold reference frame with respect to the view (camera/screen)
        /// </summary>
        /// <param name="pose"></param>
        public Mat ViewPose()
        {
            check_connection();
            var command = "G_ViewPose";
            send_line(command);
            var pose = rec_pose();
            check_status();
            return pose;
        }


        /// <summary>
        ///     Gets the nominal robot parameters
        /// </summary>
        /// <param name="robot"></param>
        /// <param name="dhm"></param>
        /// <param name="pose_base"></param>
        /// <param name="pose_tool"></param>
        /// <returns></returns>
        public bool setRobotParams(Item robot, double[][] dhm, Mat pose_base, Mat pose_tool)
        {
            check_connection();
            send_line("S_AbsAccParam");
            send_item(robot);
            var r2b = Mat.Identity4x4();
            send_pose(r2b);
            send_pose(pose_base);
            send_pose(pose_tool);
            var ndofs = dhm.Length;
            send_int(ndofs);
            for (var i = 0; i < ndofs; i++)
                send_array(dhm[i]);

            // for internal use only
            send_pose(pose_base);
            send_pose(pose_tool);
            send_int(ndofs);
            for (var i = 0; i < ndofs; i++)
                send_array(dhm[i]);
            // reserved
            send_array(null);
            send_array(null);
            check_status();
            return true;
        }


        //------------------------------------------------------------------
        //----------------------- CAMERA VIEWS -----------------------------
        /// <summary>
        ///     Open a simulated 2D camera view. Returns a handle pointer that can be used in case more than one simulated view is
        ///     used.
        /// </summary>
        /// <param name="item">Reference frame or other object to attach the camera</param>
        /// <param name="cam_params">Camera parameters as a string. Refer to the documentation for more information.</param>
        /// <returns>Camera pointer/handle. Keep the handle if more than 1 simulated camera is used</returns>
        public ulong Cam2D_Add(Item itemObject, string cam_params = "")
        {
            check_connection();
            send_line("Cam2D_Add");
            send_item(itemObject);
            send_line(cam_params);


            var camHandle = rec_ptr();
            check_status();
            //return 0;
            return camHandle;
        }

        /// <summary>
        ///     Take a snapshot from a simulated camera view and save it to a file. Returns 1 if success, 0 otherwise.
        /// </summary>
        /// <param name="file_save_img">file path to save.Formats supported include PNG, JPEG, TIFF, ...</param>
        /// <param name="cam_handle">amera handle(pointer returned by Cam2D_Add)</param>
        /// <returns></returns>
        public bool Cam2D_Snapshot(string file_save_img, ulong cam_handle = 0)
        {
            check_connection();
            send_line("Cam2D_Snapshot");
            send_ptr(cam_handle);
            send_line(file_save_img);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <summary>
        ///     Closes all camera windows or one specific camera if the camera handle is provided. Returns 1 if success, 0
        ///     otherwise.
        /// </summary>
        /// <param name="cam_handle">camera handle(pointer returned by Cam2D_Add). Leave to 0 to close all simulated views.</param>
        /// <returns></returns>
        public bool Cam2D_Close(ulong cam_handle = 0)
        {
            check_connection();
            if (cam_handle == 0)
            {
                send_line("Cam2D_CloseAll");
            }
            else
            {
                send_line("Cam2D_Close");
                send_ptr(cam_handle);
            }

            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <summary>
        ///     Set the parameters of the simulated camera.
        /// </summary>
        /// <param name="cam_params">parameter settings according to the parameters supported by Cam2D_Add</param>
        /// <param name="cam_handle">camera handle (optional)</param>
        /// <returns></returns>
        public bool Cam2D_SetParams(string cam_params, ulong cam_handle = 0)
        {
            check_connection();
            send_line("Cam2D_SetParams");
            send_ptr(cam_handle);
            send_line(cam_params);
            var success = rec_int();
            check_status();
            return success > 0;
        }

        /// <summary>
        ///     Returns the license string (as shown in the RoboDK main window)
        /// </summary>
        /// <returns></returns>
        public string License()
        {
            check_connection();
            var command = "G_License";
            send_line(command);
            var license = rec_line();
            check_status();
            return license;
        }

        /// <summary>
        ///     Returns the list of items selected (it can be one or more items)
        /// </summary>
        /// <returns></returns>
        public List<Item> Selection()
        {
            check_connection();
            var command = "G_Selection";
            send_line(command);
            var nitems = rec_int();
            var list_items = new List<Item>(nitems);
            for (var i = 0; i < nitems; i++)
                list_items[i] = rec_item();
            check_status();
            return list_items;
        }

        public void AddTargetJ(Item pgm, string targetName, double[] joints, Item robotBase = null, Item robot = null)
        {
            var target = AddTarget(targetName, robotBase);
            if (target == null)
                throw new Exception($"Create target '{targetName}' failed.");
            target.setVisible(false);
            target.setAsJointTarget();
            target.setJoints(joints);
            if (robot != null)
                target.setRobot(robot);

            //target
            pgm.addMoveJ(target);
        }

        #endregion

        #region Protected Methods

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                    if (_socket != null)
                        _socket.Dispose();

                _disposed = true;
            }
        }

        #endregion

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
                throw new RdkException("Can't connect to RoboDK library");
        }

        /// <summary>
        ///     checks the status of the connection
        /// </summary>
        internal void check_status()
        {
            var status = rec_int();
            switch (status)
            {
                case 0:
                    return;

                case 1:
                    throw new RdkException(
                        "Invalid item provided: The item identifier provided is not valid or it does not exist.");

                case 2:
                {
                    //output warning
                    var strproblems = rec_line();
                    //TODO chu: Implement warning
                    //print("WARNING: " + strproblems);
                    //#warn(strproblems)# does not show where is the problem...
                    return;
                }
                case 3:
                {
                    // output error
                    var strproblems = rec_line();
                    throw new RdkException(strproblems);
                }
                case 9:
                {
                    throw new RdkException("Invalid license. Contact us at: info@robodk.com");
                }
                default:
                    //raise Exception('Problems running function');
                    throw new RdkException("Problems running function");
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
                throw new RdkException("Invalid color. A color must be a 4-size double array [r,g,b,a]");
            return true;
        }

        internal string rec_line()
        {
            //Receives a string. It reads until if finds LF (\\n)
            var buffer = new byte[1];
            var bytesread = _socket.Receive(buffer, 1, SocketFlags.None);
            var line = "";
            while (bytesread > 0 && buffer[0] != '\n')
            {
                line = line + Encoding.UTF8.GetString(buffer);
                bytesread = _socket.Receive(buffer, 1, SocketFlags.None);
            }

            return line;
        }

        //Sends an item pointer
        internal void send_item(Item item)
        {
            byte[] bytes;
            if (item == null)
                bytes = BitConverter.GetBytes((ulong) 0);
            else
                bytes = BitConverter.GetBytes(item.get_item());
            if (bytes.Length != 8)
                throw new RdkException("API error");
            Array.Reverse(bytes);
            try
            {
                _socket.Send(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        //Receives an item pointer
        internal Item rec_item()
        {
            //TODO CHU 32/64bit?
            var buffer1 = new byte[8];
            var buffer2 = new byte[4];
            var read1 = _socket.Receive(buffer1, 8, SocketFlags.None);
            var read2 = _socket.Receive(buffer2, 4, SocketFlags.None);
            if (read1 != 8 || read2 != 4)
                return null;
            Array.Reverse(buffer1);
            Array.Reverse(buffer2);
            var item = BitConverter.ToUInt64(buffer1, 0);
            //Console.WriteLine("Received item: " + item.ToString());
            var type = BitConverter.ToInt32(buffer2, 0);
            return new Item(this, item, type);
        }

        //Sends an item pointer
        internal void send_ptr(ulong ptr = 0)
        {
            var bytes = BitConverter.GetBytes(ptr);
            if (bytes.Length != 8)
                throw new RdkException("RoboDK API error");
            Array.Reverse(bytes);
            _socket.Send(bytes);
        }

        ///Receives a generic pointer
        internal ulong rec_ptr()
        {
            //TODO CHU 32/64bit?


            var bytes = new byte[8];
            var read = _socket.Receive(bytes, 8, SocketFlags.None);
            if (read != 8)
                throw new Exception("Something went wrong");
            Array.Reverse(bytes);
            var ptrH = BitConverter.ToUInt64(bytes, 0);
            return ptrH;
        }

        internal void send_pose(Mat pose)
        {
            if (!pose.IsHomogeneous())
                throw new Exception($"Matrix not Homogenous: {pose.Cols}x{pose.Rows}");
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

            _socket.Send(bytesarray, 8 * nvalues, SocketFlags.None);
        }

        internal Mat rec_pose()
        {
            var pose = new Mat(4, 4);
            var bytes = new byte[16 * 8];
            var nbytes = _socket.Receive(bytes, 16 * 8, SocketFlags.None);
            if (nbytes != 16 * 8)
                throw new RdkException("Invalid pose sent"); //raise Exception('Problems running function');
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
                _socket.Send(bytes, 8, SocketFlags.None);
            }
        }

        internal void rec_xyz(double[] xyzpos)
        {
            var bytes = new byte[3 * 8];
            var nbytes = _socket.Receive(bytes, 3 * 8, SocketFlags.None);
            if (nbytes != 3 * 8)
                throw new RdkException("Invalid pose sent"); //raise Exception('Problems running function');
            for (var i = 0; i < 3; i++)
            {
                var onedouble = new byte[8];
                Array.Copy(bytes, i * 8, onedouble, 0, 8);
                Array.Reverse(onedouble);
                xyzpos[i] = BitConverter.ToDouble(onedouble, 0);
            }
        }

        internal void send_int(int number)
        {
            var bytes = BitConverter.GetBytes(number);
            Array.Reverse(bytes); // convert from big endian to little endian
            try
            {
                _socket.Send(bytes);
            }
            catch
            {
                throw new RdkException("_socket.Send failed.");
            }
        }

        internal int rec_int()
        {
            var bytes = new byte[4];
            var read = _socket.Receive(bytes, 4, SocketFlags.None);
            if (read < 4)
                return 0;
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

            _socket.Send(bytesarray, 8 * nvalues, SocketFlags.None);
        }

        // Receives an array of doubles
        internal double[] rec_array()
        {
            var nvalues = rec_int();
            if (nvalues > 0)
            {
                var values = new double[nvalues];
                var bytes = new byte[nvalues * 8];
                var read = _socket.Receive(bytes, nvalues * 8, SocketFlags.None);
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
            send_int(mat.Rows);
            send_int(mat.Cols);
            for (var j = 0; j < mat.Cols; j++)
            for (var i = 0; i < mat.Rows; i++)
            {
                var bytes = BitConverter.GetBytes(mat[i, j]);
                Array.Reverse(bytes);
                _socket.Send(bytes, 8, SocketFlags.None);
            }
        }

        // receives a 2 dimensional matrix (nxm)
        internal Mat rec_matrix()
        {
            var size1 = rec_int();
            var size2 = rec_int();
            var recvsize = size1 * size2 * 8;
            var bytes = new byte[recvsize];
            var mat = new Mat(size1, size2);
            var BUFFER_SIZE = 256;
            var received = 0;
            if (recvsize > 0)
            {
                var to_receive = Math.Min(recvsize, BUFFER_SIZE);
                while (to_receive > 0)
                {
                    var nbytesok = _socket.Receive(bytes, received, to_receive, SocketFlags.None);
                    if (nbytesok <= 0)
                        throw new RdkException(
                            "Can't receive matrix properly"); //raise Exception('Problems running function');
                    received = received + nbytesok;
                    to_receive = Math.Min(recvsize - received, BUFFER_SIZE);
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
        internal void moveX(Item target, double[] joints, Mat mat_target, Item itemrobot, int movetype,
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
            else if (mat_target != null && mat_target.IsHomogeneous())
            {
                send_int(2);
                send_array(mat_target.ToDoubles());
                send_item(null);
            }
            else
            {
                throw new RdkException("Invalid target type"); //raise Exception('Problems running function');
            }

            send_item(itemrobot);
            check_status();
            if (blocking)
                itemrobot.WaitMove();
        }

        // private move type, to be used by public methods (MoveJ  and MoveL)
        internal void moveC_private(Item target1, double[] joints1, Mat mat_target1, Item target2, double[] joints2,
            Mat mat_target2, Item itemrobot, bool blocking = true)
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
            else if (mat_target1 != null && mat_target1.IsHomogeneous())
            {
                send_int(2);
                send_array(mat_target1.ToDoubles());
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
            else if (mat_target2 != null && mat_target2.IsHomogeneous())
            {
                send_int(2);
                send_array(mat_target2.ToDoubles());
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
                itemrobot.WaitMove();
        }

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        /// <returns></returns>
        internal void Finish()
        {
            Disconnect();
        }

        internal bool Set_connection_params(int safe_mode = 1, int auto_update = 0, int timeout = -1)
        {
            //Sets some behavior parameters: SAFE_MODE, AUTO_UPDATE and TIMEOUT.
            SAFE_MODE = safe_mode;
            AUTO_UPDATE = auto_update;
            if (timeout >= 0)
                TIMEOUT = timeout;
            send_line("CMD_START");
            send_line(Convert.ToString(SAFE_MODE) + " " + Convert.ToString(AUTO_UPDATE));
            var response = rec_line();
            if (response == "READY")
                return true;
            return false;
        }
    }
}