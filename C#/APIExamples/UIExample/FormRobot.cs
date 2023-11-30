using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;
using RoboDk.API;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;
using SamplePanelRoboDK.Properties;

namespace SamplePanelRoboDK
{
    public partial class FormRobot : Form
    {
        // Define if the robot movements will be blocking
        private const bool MoveBlocking = false;

        // RDK holds the main object to interact with RoboDK.
        // The RoboDK application starts when a RoboDK object is created.
        private IRoboDK _rdk;

        // Keep the ROBOT item as a global variable
        private IItem _robot;

        public FormRobot()
        {
            InitializeComponent();
        }

        private void FormRobot_Load(object sender, EventArgs e)
        {
            // This will create a new icon in the windows toolbar that shows how we can lock/unlock the application
            Setup_Notification_Icon();

            // Start RoboDK here if we want to start it before the Form is displayed
            if (!Check_RDK())
            {
                // RoboDK starts here. We can optionally pass arguments to start it hidden or start it remotely on another computer provided the computer IP.
                // If RoboDK was already running it will just connect to the API. We can force a new RoboDK instance and specify a communication port
                _rdk = new RoboDK();

                // Check if RoboDK started properly
                if (Check_RDK())
                {
                    notifybar.Text = @"RoboDK is Running...";

                    // attempt to auto select the robot:
                    SelectRobot();
                }

                // set default movement on the simulator only:
                rad_RunMode_Simulation.PerformClick();

                // display RoboDK by default:
                rad_RoboDK_show.PerformClick();

                // Set incremental moves in cartesian space with respect to the robot reference frame
                rad_Move_wrt_Reference.PerformClick();

                numStep.Value = 10; // set movement steps of 50 mm or 50 deg by default


                // other ways to Start RoboDK
                //bool START_HIDDEN = false;
                //RDK = new RoboDK("", START_HIDDEN); // default connection, starts RoboDK visible if it has not been started
                //RDK = new RoboDK("localhost", false, 20599); //start visible, use specific communication port to not interfere with other applications
                //RDK = new RoboDK("localhost", true, 20599); //start hidden,  use specific communication port to not interfere with other applications

                Icon = Resources.IconRoboDK;
            }
        }

        private void FormRobot_Shown(object sender, EventArgs e)
        {
            // Start RoboDK here if we want to start it after the form is displayed
        }

        /// <summary>
        ///     Stop running RoboDK when the Form is closed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void FormRobot_FormClosed(object sender, FormClosedEventArgs e)
        {
            if (!Check_RDK()) return;
            // Force to stop and close RoboDK (optional)
            // RDK.CloseAllStations(); // close all stations
            // RDK.Save("path_to_save.rdk"); // save the project if desired
            _rdk.CloseRoboDK();
            _rdk = null;
        }

        /// <summary>
        ///     Check if the RDK object is ready.
        ///     Returns True if the RoboDK API is available or False if the RoboDK API is not available.
        /// </summary>
        /// <returns></returns>
        public bool Check_RDK()
        {
            // check if the RDK object has been initialized:
            if (_rdk == null)
            {
                notifybar.Text = @"RoboDK has not been started";
                return false;
            }

            // Check if the RDK API is connected
            if (!_rdk.Connected())
            {
                notifybar.Text = @"Connecting to RoboDK...";
                // Attempt to connect to the RDK API
                if (!_rdk.Connect())
                {
                    notifybar.Text = @"Problems using the RoboDK API. The RoboDK API is not available...";
                    return false;
                }
            }

            return true;
        }

        private void btnLoadFile_Click(object sender, EventArgs e)
        {
            // Make sure the RoboDK API is running:
            if (!Check_RDK()) return;

            // Show the File dialog to select a file:
            var selectFile = new OpenFileDialog
            {
                Title = @"Select a file to open with RoboDK",
                InitialDirectory = _rdk.GetParameter("PATH_LIBRARY").Replace("/", "\\")
            };
            // open the RoboDK library by default
            if (selectFile.ShowDialog() == DialogResult.OK) // show the dialog
            {
                var filename = selectFile.FileName;
                // Check if it is a RoboDK station file (.rdk extension)
                // If desired, close any other stations that have previously been open
                /*if (filename.EndsWith(".rdk", StringComparison.InvariantCultureIgnoreCase))
                {
                    CloseAllStations();
                }*/

                // retrieve the newly added item
                var item = _rdk.AddFile(selectFile.FileName);
                if (item.Valid())
                {
                    notifybar.Text = $@"Loaded: {item.Name()}";
                    // attempt to retrieve the ROBOT variable (a robot available in the station)
                    SelectRobot();
                }
                else
                {
                    notifybar.Text = $@"Could not load: {filename}";
                }
            }
        }

        /// <summary>
        ///     Update the ROBOT variable by choosing the robot available in the currently open station
        ///     If more than one robot is available, a popup will be displayed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void btnSelectRobot_Click(object sender, EventArgs e)
        {
            SelectRobot();
        }

        /// <summary>
        ///     Update the ROBOT variable by choosing the robot available in the currently open station
        ///     If more than one robot is available, a popup will be displayed
        /// </summary>
        public void SelectRobot()
        {
            notifybar.Text = @"Selecting robot...";
            if (!Check_RDK())
            {
                _robot = null;
                return;
            }

            _robot = _rdk.ItemUserPick("Select a robot", ItemType.Robot); // select robot among available robots
            //ROBOT = RL.getItem("ABB IRB120", ITEM_TYPE_ROBOT); // select by name
            //ITEM = RL.ItemUserPick("Select an item"); // Select any item in the station
            if (_robot.Valid())
            {
                _robot.NewLink(); // This will create a new communication link (another instance of the RoboDK API), this is useful if we are moving 2 robots at the same time.                
                notifybar.Text = $@"Using robot: {_robot.Name()}";
            }
            else
            {
                notifybar.Text = @"Robot not available. Load a file first";
            }
        }

        /// <summary>
        ///     Check if the ROBOT object is available and valid. It will make sure that we can operate with the ROBOT object.
        /// </summary>
        /// <returns></returns>
        public bool Check_ROBOT(bool ignoreBusyStatus = false)
        {
            if (!Check_RDK()) return false;
            if (_robot == null || !_robot.Valid())
            {
                notifybar.Text = @"A robot has not been selected. Load a station or a robot file first.";
                return false;
            }

            try
            {
                notifybar.Text = $@"Using robot: {_robot.Name()}";
            }
            catch (RdkException rdkException)
            {
                notifybar.Text = $@"The robot has been deleted: {rdkException.Message}";
                return false;
            }

            // Safe check: If we are doing non blocking movements, we can check if the robot is doing other movements with the Busy command
            // ReSharper disable once RedundantLogicalConditionalExpressionOperand
            if (!MoveBlocking && !ignoreBusyStatus && _robot.Busy())
            {
                notifybar.Text = @"The robot is busy!! Try later...";
                return false;
            }

            return true;
        }

        /// <summary>
        ///     Close all the stations available in RoboDK (top level items)
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        public void CloseAllStations()
        {
            // Get all the RoboDK stations available
            var allStations = _rdk.GetItemList(ItemType.Station);
            foreach (var station in allStations)
            {
                notifybar.Text = $@"Closing {station.Name()}";
                // this will close a station without asking to save:
                station.Delete();
            }
        }


        ////////////////////////////////////////////////////////////////
        ////////////////////////////////////////////////////////////////
        //////////////// Example to get/set robot position /////////////////

        private void BtnMoveRobotHome_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT()) return;

            var jointsHome = _robot.JointsHome();

            _robot.MoveJ(jointsHome);
        }

        private void BtnGetJoints_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT(true)) return;

            var joints = _robot.Joints();
            var pose = _robot.Pose();

            // update the joints
            var strjoints = Values_2_String(joints);
            txtJoints.Text = strjoints;

            // update the pose as xyzwpr
            var xyzwpr = pose.ToTxyzRxyz();
            var strpose = Values_2_String(xyzwpr);
            txtPosition.Text = strpose;
        }

        private void BtnMoveJoints_Click(object sender, EventArgs e)
        {
            // retrieve the robot joints from the text and validate input
            var joints = String_2_Values(txtJoints.Text);

            // make sure RDK is running and we have a valid input
            if (!Check_ROBOT() || joints == null) return;

            try
            {
                //bool jnts_valid = ROBOT.setJoints(joints, RoboDK.SETJOINTS_SATURATE_APPLY);
                //Console.WriteLine("Robot joints are valid: " + jnts_valid.ToString());
                _robot.MoveJ(joints, MoveBlocking);
            }
            catch (RdkException rdkException)
            {
                notifybar.Text = $@"Problems moving the robot: {rdkException.Message}";
                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
            }
        }

        private void BtnMovePose_Click(object sender, EventArgs e)
        {
            // retrieve the robot position from the text and validate input
            var xyzwpr = String_2_Values(txtPosition.Text);

            // make sure RDK is running and we have a valid input
            if (!Check_ROBOT() || xyzwpr == null) return;

            //Mat pose = Mat.FromXYZRPW(xyzwpr);
            var pose = Mat.FromTxyzRxyz(xyzwpr);
            try
            {
                _robot.MoveJ(pose, MoveBlocking);
            }
            catch (RdkException rdkex)
            {
                notifybar.Text = $@"Problems moving the robot: {rdkex.Message}";
                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
            }
        }


        /// <summary>
        ///     Convert a list of numbers provided as a string to an array of values
        /// </summary>
        /// <param name="strvalues"></param>
        /// <returns></returns>
        public double[] String_2_Values(string strvalues)
        {
            double[] dvalues = null;
            try
            {
                dvalues = Array.ConvertAll(strvalues.Split(','), double.Parse);
            }
            catch (FormatException ex)
            {
                notifybar.Text = $@"Invalid input: {strvalues}: {ex.Message}";
            }

            return dvalues;
        }

        /// <summary>
        ///     Convert an array of values as a string
        /// </summary>
        /// <param name="dvalues"></param>
        /// <returns></returns>
        public string Values_2_String(double[] dvalues)
        {
            if (dvalues == null || dvalues.Length < 1) return "Invalid values";
            // Not supported on .NET Framework 2.0:
            //string strvalues = String.Join(" , ", dvalues.Select(p => p.ToString("0.0")).ToArray());
            var strvalues = dvalues[0].ToString("0.0");
            for (var i = 1; i < dvalues.Length; i++) strvalues += $" , {dvalues[i]:0.0}";

            return strvalues;
            //return "";
        }

        //////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////
        ///////// Run mode types: ///////////////
        ///////// 1- Simulation (default): RUNMODE_SIMULATE
        ///////// 2- Offline programming (default): RUNMODE_MAKE_ROBOTPROG
        ///////// 3- Online programming: RUNMODE_RUN_ROBOT. It moves the real robot
        private void rad_RunMode_Simulation_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            // Check that there is a link with RoboDK:
            btnOLPdone.Enabled = false;
            if (!Check_ROBOT()) return;

            // Important: stop any previous program generation (if we selected offline programming mode)
            _rdk.Disconnect();

            // Set to simulation mode:
            _rdk.SetRunMode();
        }

        private void rad_RunMode_Program_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            btnOLPdone.Enabled = true;
            if (!Check_ROBOT()) return;

            // Important: Disconnect from the robot for safety
            _robot.Finish();

            // Set to simulation mode:
            _rdk.SetRunMode(RunMode.MakeRobotProgram);

            // specify a program name, a folder to save the program and a post processor if desired
            _rdk.ProgramStart("NewProgram");
        }

        private void BtnOLPdone_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT()) return;

            // this will trigger program generation
            //RDK.Finish();
            _robot.Finish(); // we must close the socket linked to the robot

            // set back to simulation
            rad_RunMode_Simulation.PerformClick();
        }

        private void rad_RunMode_Online_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            btnOLPdone.Enabled = false;
            // Check that there is a link with RoboDK:
            if (!Check_ROBOT()) return;

            // Important: stop any previous program generation (if we selected offline programming mode)
            _rdk.Disconnect();

            // Connect to real robot
            if (_robot.Connect())
            {
                // Set to Run on Robot robot mode:
                _rdk.SetRunMode(RunMode.RunRobot);
            }
            else
            {
                notifybar.Text = @"Can't connect to the robot. Check connection and parameters.";
                rad_RunMode_Simulation.AutoCheck = true;
            }
        }


        ///////////////////////////////////////////////////////////////
        ///////////////////////////////////////////////////////////////
        ////////////// Example to run a program //////////////

        private void btnRun_Program_Click(object sender, EventArgs e)
        {
            // Check that there is a link with RoboDK:
            if (!Check_RDK()) return;

            var programName = txtRunProgram.Text;

            // Retrieve the program item program
            var program = _rdk.GetItemByName(programName);

            if (program.Valid() && (program.GetItemType() == ItemType.ProgramPython ||
                                    program.GetItemType() == ItemType.Program))
            {
                program.RunProgram();
                return;

                //double percent_OK = prog.Update(RoboDK.COLLISION_ON, 3600, null, 4, 4) * 100.0;
                //notifybar.Text = "Program check: " + percent_OK.ToString("0.0") + " % " + (percent_OK == 100.0 ? " OK " : " WARNING!!");

                program.InstructionListJoints(out var errorMsg, out var jointsMat, 4, 4, "",
                    CollisionCheckOptions.CollisionCheckOn);
                var result = jointsMat.ToString();

                return;

                if (rad_RunMode_Online.Checked)
                    // force to run on robot
                    program.SetRunType(ProgramExecutionType.RunOnRobot);
                else if (rad_RunMode_Program.Checked)
                    // generate a program call to another program
                    _robot.RunCodeCustom(programName);
                else
                    // force to run in simulation mode
                    program.SetRunType(ProgramExecutionType.RunOnSimulator);

                //prog.setRunType(RoboDK.PROGRAM_RUN_ON_SIMULATOR);
                //if RunMode == RUNMODE_RUN_ON_ROBOT it will start the program on the robot controller
                notifybar.Text = $@"Running program: {txtRunProgram.Text}";
                program.RunProgram();
            }

            notifybar.Text = $@"The program {txtRunProgram.Text} does not exist.";
            //MessageBox.Show("The program does not exist.");
        }


        //////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////
        ///////////////// GROUP DISPLAY MODE ////////////////
        // Import SetParent/GetParent command from user32 dll to identify if the main window is a subprocess
        [DllImport("user32.dll")]
        private static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        private void Rad_RoboDK_show_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            // Check RoboDK connection
            if (!Check_RDK()) return;

            // unhook from the integrated panel it is inside the main panel
            SetParent(_rdk.GetWindowHandle(), IntPtr.Zero);

            _rdk.SetWindowState(); // removes Cinema mode and shows the screen
            _rdk.SetWindowState(RoboDk.API.Model.WindowState.Maximized); // shows maximized

            // set the form to the minimum size
            Height = MinimumSize.Height;
            Width = MinimumSize.Width;


            //Alternatively: RDK.ShowRoboDK();
            BringToFront(); // show on top of RoboDK
        }

        private void Rad_RoboDK_hide_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            if (!Check_RDK()) return;

            _rdk.SetWindowState(RoboDk.API.Model.WindowState.Hidden);
            //Alternatively: RDK.HideRoboDK();

            // set the form to the minimum size
            Size = MinimumSize;
            Width = MinimumSize.Width;
        }

        private void Rad_RoboDK_Integrated_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            // skip if the radio button became unchecked
            if (!rad_RoboDK_Integrated.Checked) return;

            if (!Check_RDK()) return;

            // hook window pointer to the integrated panel
            //SetParent(RDK.PROCESS.MainWindowHandle, panel_rdk.Handle);
            SetParent(_rdk.GetWindowHandle(), panel_rdk.Handle);

            //RDK.SetWindowState(RoboDk.API.Model.WindowState.Show); // show RoboDK window if it was hidden
            _rdk.SetWindowState(RoboDk.API.Model.WindowState
                .Cinema); // sets cinema mode (remove the menu, the toolbar, the title bar and the status bar)
            _rdk.SetWindowState(RoboDk.API.Model.WindowState.Fullscreen); // maximizes the screen and sets cinema mode

            // make form height larger
            Size = new Size(Size.Width, 700);
        }


        [DllImport("user32.dll", SetLastError = true)]
        public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);

        private void Panel_Resized(object sender, EventArgs e)
        {
            if (!rad_RoboDK_Integrated.Checked) return;

            // resize the content of the panel_rdk when it is resized
            MoveWindow(_rdk.GetWindowHandle(), 0, 0, panel_rdk.Width, panel_rdk.Height, true);
        }

        //////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////
        /////////////////// FOR INCREMENTAL MOVEMENT ////////////////////////

        private void Rad_Move_wrt_Reference_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            Set_Incremental_Buttons_Cartesian();
        }

        private void rad_Move_wrt_Tool_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            Set_Incremental_Buttons_Cartesian();
        }

        private void Rad_Move_Joints_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            var radSender = (RadioButton) sender;
            if (!radSender.Checked) return;

            Set_Incremental_Buttons_Joints();
        }

        private void Set_Incremental_Buttons_Cartesian()
        {
            // update label units for the step:
            lblstepIncrement.Text = @"Step (mm):";

            // Text to display on the positive motion buttons for incremental Cartesian movements:
            btnTXpos.Text = @"+Tx";
            btnTYpos.Text = @"+Ty";
            btnTZpos.Text = @"+Tz";
            btnRXpos.Text = @"+Rx";
            btnRYpos.Text = @"+Ry";
            btnRZpos.Text = @"+Rz";

            // Text to display on the negative motion buttons for incremental Cartesian movements:
            btnTXneg.Text = @"-Tx";
            btnTYneg.Text = @"-Ty";
            btnTZneg.Text = @"-Tz";
            btnRXneg.Text = @"-Rx";
            btnRYneg.Text = @"-Ry";
            btnRZneg.Text = @"-Rz";
        }

        private void Set_Incremental_Buttons_Joints()
        {
            // update label units for the step:
            lblstepIncrement.Text = @"Step (deg):";

            // Text to display on the positive motion buttons for Incremental Joint movement:
            btnTXpos.Text = @"+J1";
            btnTYpos.Text = @"+J2";
            btnTZpos.Text = @"+J3";
            btnRXpos.Text = @"+J4";
            btnRYpos.Text = @"+J5";
            btnRZpos.Text = @"+J6";

            // Text to display on the positive motion buttons for Incremental Joint movement:
            btnTXneg.Text = @"-J1";
            btnTYneg.Text = @"-J2";
            btnTZneg.Text = @"-J3";
            btnRXneg.Text = @"-J4";
            btnRYneg.Text = @"-J5";
            btnRZneg.Text = @"-J6";
        }


        /// <summary>
        ///     Move the the robot relative to the TCP
        /// </summary>
        private void Incremental_Move(string buttonName)
        {
            if (!Check_ROBOT()) return;

            notifybar.Text = $@"Button selected: {buttonName}";

            if (buttonName.Length < 3)
            {
                notifybar.Text = @"Internal problem! Button name should be like +J1, -Tx, +Rz or similar";
                return;
            }

            // get the the sense of motion the first character as '+' or '-'
            double moveStep;
            switch (buttonName[0])
            {
                case '+':
                    moveStep = +Convert.ToDouble(numStep.Value);
                    break;
                case '-':
                    moveStep = -Convert.ToDouble(numStep.Value);
                    break;
                default:
                    notifybar.Text = @"Internal problem! Unexpected button name";
                    return;
            }

            //////////////////////////////////////////////
            //////// if we are moving in the joint space:
            if (rad_Move_Joints.Checked)
            {
                var joints = _robot.Joints();

                // get the moving axis (1, 2, 3, 4, 5 or 6)
                var jointId = Convert.ToInt32(buttonName[2].ToString()) - 1; // important, double array starts at 0

                joints[jointId] = joints[jointId] + moveStep;

                try
                {
                    _robot.MoveJ(joints, MoveBlocking);
                    //ROBOT.MoveL(joints, MOVE_BLOCKING);
                }
                catch (RdkException rdkException)
                {
                    notifybar.Text = $@"The robot can't move to the target joints: {rdkException.Message}";
                    //MessageBox.Show("The robot can't move to " + new_pose.ToString());
                }
            }
            else
            {
                //////////////////////////////////////////////
                //////// if we are moving in the cartesian space
                // Button name examples: +Tx, -Tz, +Rx, +Ry, +Rz

                var moveId = 0;

                var moveTypes = new string[6] {"Tx", "Ty", "Tz", "Rx", "Ry", "Rz"};

                for (var i = 0; i < 6; i++)
                    if (buttonName.EndsWith(moveTypes[i]))
                    {
                        moveId = i;
                        break;
                    }

                var move_xyzwpr = new double[6] {0, 0, 0, 0, 0, 0};
                move_xyzwpr[moveId] = moveStep;
                var movementPose = Mat.FromTxyzRxyz(move_xyzwpr);

                // the the current position of the robot (as a 4x4 matrix)
                var robotPose = _robot.Pose();

                // Calculate the new position of the robot
                Mat newRobotPose;
                var isTcpRelativeMove = rad_Move_wrt_Tool.Checked;
                if (isTcpRelativeMove)
                {
                    // if the movement is relative to the TCP we must POST MULTIPLY the movement
                    newRobotPose = robotPose * movementPose;
                }
                else
                {
                    // if the movement is relative to the reference frame we must PRE MULTIPLY the XYZ translation:
                    // new_robot_pose = movement_pose * robot_pose;
                    // Note: Rotation applies from the robot axes.

                    var transformationAxes = new Mat(robotPose);
                    transformationAxes.setPos(0, 0, 0);
                    var movementPoseAligned = transformationAxes.inv() * movementPose * transformationAxes;
                    newRobotPose = robotPose * movementPoseAligned;
                }

                // Then, we can do the movement:
                try
                {
                    _robot.MoveJ(newRobotPose, MoveBlocking);
                }
                catch (RdkException rdkException)
                {
                    notifybar.Text = $@"The robot can't move to {newRobotPose.ToString()} : {rdkException.Message}";
                    //MessageBox.Show("The robot can't move to " + new_pose.ToString());
                }


                // Some tips:
                // retrieve the current pose of the robot: the active TCP with respect to the current reference frame
                // Tip 1: use
                // ROBOT.setFrame()
                // to set a reference frame (object link or pose)
                //
                // Tip 2: use
                // ROBOT.setTool()
                // to set a tool frame (object link or pose)
                //
                // Tip 3: use
                // ROBOT.MoveL_Collision(j1, new_move)
                // to test if a movement is feasible by the robot before doing the movement
                //
            }
        }


        private void btnTXpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTXneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTYpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTYneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTZpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTZneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRXpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRXneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRYpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRYneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRZpos_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRZneg_Click(object sender, EventArgs e)
        {
            var btn = (Button) sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }


        /*
        /// <summary>
        /// Move the the robot relative to the TCP
        /// </summary>
        /// <param name="movement"></param>
        private void Robot_Move_Cartesian(Mat add_move, bool is_relative_TCP = false)
        {
            if (!Check_ROBOT()) { return; }

            // retrieve the current pose of the robot: the active TCP with respect to the current reference frame
            // Tip 1: use
            // ROBOT.setPoseFrame()
            // to set a reference frame (object link or pose)
            //
            // Tip 2: use
            // ROBOT.setPoseTool()
            // to set a tool frame (object link or pose)
            //
            // Tip 3: use
            // ROBOT.MoveL_Collision(j1, new_move)
            // to test if a movement is feasible by the robot before doing the movement
            // Collisions are not detected if collision detection is turned off.
            Mat robot_pose = ROBOT.Pose();

            // calculate the new pose of the robot (post multiply)
            Mat new_pose = robot_pose * add_move;
            try
            {
                ROBOT.MoveJ(new_pose, MOVE_BLOCKING);
            }
            catch (RdkException rdkex)
            {
                notifybar.Text = "The robot can't move to " + new_pose.ToString();
                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
            }
        }



        /// <summary>
        /// This shows an example that moves the robot to a relative position given joint coordinates. The forward kinematics is calculated.
        /// </summary>
        /// <param name="joints"></param>
        private void Move_2_Approach(double[] joints)
        {
            if (!Check_ROBOT()) { return; }
            double approach_dist = 100; // Double.Parse(txtApproach.Text);
            Mat approach_mat = Mat.transl(0, 0, -approach_dist);

            // calculate the position of the robot * tool            
            Mat tool_pose = ROBOT.PoseTool();                       // get the tool pose of the robot
            Mat robot_tool_pose = ROBOT.SolveFK(joints) * tool_pose * approach_mat; // get the new position (approach) of the robot*tool
            Mat robot_pose = robot_tool_pose * tool_pose.inv();  // get the position of the robot (from the base frame to the tool flange)
            double[] joints_app = ROBOT.SolveIK(robot_pose);           // calculate inverse kinematics to get the robot joints for the approach position
            if (joints_app == null)
            {
                MessageBox.Show("Position not reachable");
                return;
            }
            ROBOT.MoveJ(joints_app, MOVE_BLOCKING);
        }
        */

        //////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////
        ////////// Test button for general purpose tests ///////////////////////

        private void btnRunTestProgram_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT()) return;


            var n_sides = 6;

            var poseRef = _robot.Pose();

            // Set the simulation speed (ratio = real time / simulated time)
            // 1 second of the simulator equals 5 second in real time
            _rdk.SetSimulationSpeed(5);

            try
            {
                // retrieve the reference frame and the tool frame (TCP)
                var frame = _robot.PoseFrame();
                var tool = _robot.PoseTool();
                var runmode = _rdk.GetRunMode(); // retrieve the run mode 

                // Program start
                _robot.MoveJ(poseRef);
                _robot.SetPoseFrame(frame); // set the reference frame
                _robot.SetPoseTool(tool); // set the tool frame: important for Online Programming
                _robot.SetSpeed(100); // Set Speed to 100 mm/s
                _robot.SetRounding(
                    5); // set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
                _robot.RunCodeCustom("CallOnStart");
                for (var i = 0; i <= n_sides; i++)
                {
                    var angle = (double) i / n_sides * 2.0 * Math.PI;

                    // calculate the next position
                    var pose_i = poseRef * Mat.rotz(angle) * Mat.transl(100, 0, 0) * Mat.rotz(-angle);

                    // Add an instruction (comment)
                    _robot.RunCodeCustom($"Moving to point {i}", ProgramRunType.Comment);
                    var xyzwpr = pose_i.ToXYZRPW(); // read the target as XYZWPR
                    _robot.MoveL(pose_i);
                }

                _robot.RunCodeCustom("CallOnStart");
                _robot.MoveL(poseRef);
            }
            catch (RdkException rdkException)
            {
                notifybar.Text = $@"Failed to complete the movement: {rdkException.Message}";
            }

            return;


            var eventChannel = _rdk.OpenRoboDkEventChannel();
            var ev = eventChannel.WaitForEvent();
            eventChannel.Close();
            return;


            // API communication speed tests
            var stopwatch = new Stopwatch();
            var ntests = 1000;

            stopwatch.Reset();
            stopwatch.Start();
            for (var i = 0; i < ntests; i++)
            {
                var robotName = _robot.Name();
            }

            stopwatch.Stop();
            Console.WriteLine(
                $@"Calling .Name() took {stopwatch.ElapsedMilliseconds * 1000 / ntests} micro seconds on average");

            stopwatch.Reset();
            stopwatch.Start();
            for (var i = 0; i < ntests; i++)
            {
                var joints = _robot.Joints();
            }

            stopwatch.Stop();
            Console.WriteLine(
                $@"Calling .Joints() took {stopwatch.ElapsedMilliseconds * 1000 / ntests} micro seconds on average");

            return;


            //--------------------------------------------------
            // Other tests used for debugging...

            //RDK.SetInteractiveMode(RoboDK.SELECT_MOVE, RoboDK.DISPLAY_REF_TX | RoboDK.DISPLAY_REF_TY | RoboDK.DISPLAY_REF_PXY | RoboDK.DISPLAY_REF_RZ, new List<RoboDK.Item>() { ROBOT }, new List<int>() { RoboDK.DISPLAY_REF_ALL });
            //return;


            var references = _rdk.GetItemList(ItemType.Frame);
            var camList = new long[references.Count];
            for (var i = 0; i < references.Count; i++)
                camList[i] = _rdk.Cam2DAdd(references[i], "FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480");

            Thread.Sleep(2000);

            for (var i = 0; i < references.Count; i++) _rdk.Cam2DSetParameters(references[i].Name(), camList[i]);

            Thread.Sleep(2000);

            // close all cameras
            _rdk.Cam2DClose();

            return;

            // Example to change the robot parameters (DHM parameters as defined by Craig 1986)
            // for joints 1 to 6, index i changes from 0 to 5:
            // dhm[i][] = [alpha, a, theta, d];


            // first point
            //double[] p1 = { 0, 0, 0 };
            //double[] p2 = { 1000, 0, 0 };
            //var reference = Mat.transl(0, 0, 100);
            //var p_collision = new double[3]; // this can be null if we don't need the collision point

            //IItem item = RDK.Collision_Line(p1, p2, reference, p_collision);

            //string name;
            //if (item.Valid())
            //{
            //    name = item.Name();
            //}
            //else
            //{
            //    // item not valid
            //}

            //return;


            //-------------------------------------------------------------
            // Test forward/inverse kinematics calculation for multiple robots
            var station = _rdk.AddStation("Speed Tests");

            var robotFile = $"{_rdk.GetParameter("PATH_LIBRARY")}/KUKA-KR-210-R2700.robot";
            var n_robots = 10;
            var n_tests = 100;
            var robotList = new List<IItem>();
            var jointsList = new List<double[]>();

            for (var i = 0; i < n_robots; i++)
            {
                var robot = _rdk.AddFile(robotFile);
                var joints = new double[] {i * 5, -90, 90, 0, 90, 0};
                robot.SetJoints(joints);
                robotList.Add(robot);
                jointsList.Add(joints);
            }


            double timeAverageMs = 0;

            for (var t = 0; t < n_tests; t++)
            {
                var t1 = DateTime.Now;

                // Bulk calculation (new): you can provide a list of robots: 2.5 ms for 10 robots on avg
                var poseSolutions = _rdk.SolveFK(robotList, jointsList);
                var jointSolutions = _rdk.SolveIK(robotList, poseSolutions);
                var jointsSolutions2 = _rdk.SolveIK(robotList, poseSolutions, jointsList);
                var jnts = _rdk.SolveIK_All(robotList, poseSolutions);
                var cnfigs = _rdk.JointsConfig(robotList, jointsList);


                /*
                // Individual calculation (typical operation): 5.5 ms for 10 robots on avg
                for (int i = 0; i < n_robots; i++)
                {
                    Mat pose = robot_list[i].SolveFK(joints_list[i]);
                    var solution = robot_list[i].SolveIK(pose); // pose_solutions[i]);                    
                }
                */

                var t2 = DateTime.Now;
                var elapsedMs = t2.Subtract(t1).TotalMilliseconds;
                timeAverageMs += elapsedMs;
                Console.WriteLine($@"Forward/inverse kinematics Calculated in (ms){elapsedMs}");
            }

            timeAverageMs /= n_tests;
            Console.WriteLine($@"=> Average calculation time (ms): {timeAverageMs}");

            station.Delete();

            return;

            // double[][] dhm;
            // Mat pose_base;
            // Mat pose_tool;
            // // get the current robot parameters:
            ///* RDK.getRobotParams(ROBOT, out dhm, out pose_base, out pose_tool);

            // // change the mastering values:
            // for (int i = 0; i < 6; i++)
            // {
            //     dhm[i][2] = dhm[i][2] + 1 * Math.PI / 180.0; // change theta i (mastering value, add 1 degree)
            // }

            // // change the base and tool distances:
            // dhm[0][3] = dhm[0][3] + 5; // add 5 mm to d1
            // dhm[5][3] = dhm[5][3] + 5; // add 5 mm to d6

            // // update the robot parameters back:
            // RDK.setRobotParams(ROBOT, dhm, pose_base, pose_tool);*/

            return;

            // Example to rotate the view around the Z axis
            /*RoboDK.Item item_robot = RDK.ItemUserPick("Select the robot you want", RoboDK.ITEM_TYPE_ROBOT);
            item_robot.MoveL(item_robot.Pose() * Mat.transl(0, 0, 50));
            return;*/


            _rdk.SetViewPose(_rdk.GetViewPose() * Mat.rotx(10 * 3.141592 / 180));
            return;

            //---------------------------------------------------------
            // Sample to generate a program using a C# script
            if (_robot != null && _robot.Valid())
            {
                //ROBOT.Finish();
                //RDK.Finish();
                // RDK.Connect(); // redundant
                _rdk.Disconnect(); // ignores any previous activity to generate the program
                _rdk.SetRunMode(RunMode.MakeRobotProgram); // Very important to set first
                _rdk.ProgramStart("TestProg1", "C:\\Users\\Albert\\Desktop\\", "KAIRO.py", _robot);
                var joints1 = new double[6] {1, 2, -50, 4, 5, 6};
                var joints2 = new double[6] {-1, -2, -50, 4, 5, 6};

                _robot.MoveJ(joints1);
                _robot.MoveJ(joints2);
                _robot.Finish(); // provoke program generation


                _rdk.Disconnect(); // ignores any previous activity to generate the program
                _rdk.SetRunMode(RunMode.MakeRobotProgram); // Very important to set first
                _rdk.ProgramStart("TestProg2_no_robot", "C:\\Users\\Albert\\Desktop\\", "Fanuc_RJ3.py");
                _rdk.RunProgram("Program1");
                _rdk.RunCode("Output Raw code");
                _rdk.Disconnect(); // provoke program generation


                _robot.Finish(); // ignores any previous activity to generate the program
                _rdk.SetRunMode(RunMode.MakeRobotProgram); // Very important to set first
                _rdk.ProgramStart("TestProg3", "C:\\Users\\Albert\\Desktop\\", "GSK.py", _robot);
                var joints3 = new double[6] {10, 20, 30, 40, 50, 60};
                var joints4 = new double[6] {-10, -20, -30, 40, 50, 60};

                _robot.MoveJ(joints3);
                _robot.MoveJ(joints4);
                _robot.Finish(); // provoke program generation
            }
            else
            {
                Console.WriteLine(@"No robot selected");
            }

            return;

            //---------------------------------------------------------
            var prog = _rdk.GetItemByName("", ItemType.Program);
            //prog.InstructionListJoints(out err_msg, out jnt_list, 0.5, 0.5);
            prog.InstructionListJoints(out _, out var jntList, 5);
            for (var j = 0; j < jntList.Cols; j++)
            {
                for (var i = 0; i < jntList.Rows; i++)
                {
                    Console.Write(jntList[i, j]);
                    Console.Write(@"    ");
                }

                Console.WriteLine("");
            }


            return;


            // Example to retrieve the selected point and normal of a surface and create a target.
            // get the robot reference frame
            var robotRef = _robot.GetLink(ItemType.Frame);
            if (!robotRef.Valid())
            {
                Console.WriteLine(
                    @"The robot doesn't have a reference frame selected. Selecting a robot reference frame (or make a reference frame active is required to add a target).");
                return;
            }

            //var obj = RDK.getItem("box", ITEM_TYPE_OBJECT);//RDK.ItemUserPick("Select an object", ITEM_TYPE_OBJECT);
            //var obj = RDK.getItem("tide", ITEM_TYPE_OBJECT);//RDK.ItemUserPick("Select an object", ITEM_TYPE_OBJECT);

            //int feature_type = -1;
            //int feature_id = -1;

            // Remember the information relating to the selected point (XYZ and surface normal).
            // These values are retrieved in Absolute coordinates (with respect to the station).
            double[] point_xyz = null;
            double[] point_ijk = null;

            while (true)
            {
                var objSelected = _rdk.GetSelectedItems();
                if (objSelected.Count == 1 && objSelected[0].GetItemType() == ItemType.Object)
                {
                    var obj = objSelected[0];
                    // RDK.SetSelectedItems(); // ideally we need this function to clear the selection
                    var isSelected = obj.SelectedFeature(out var featureType, out var featureId);
                    if (isSelected && featureType == ObjectSelectionType.Surface)
                    {
                        var description = obj.GetPoints(featureType, featureId, out var pointList);
                        // great, we got the point from the surface. This will be size 6x1
                        Console.WriteLine($@"Point information: {description}");
                        if (pointList.Cols < 1 || pointList.Rows < 6)
                        {
                            // something is wrong! This should not happen....
                            Console.WriteLine(pointList.ToString());
                            continue;
                        }

                        var value = pointList.GetCol(0).ToDoubles();
                        point_xyz = new[] {value[0], value[1], value[2]};
                        // invert the IJK values (RoboDK provides the normal coming out of the surface but we usually want the Z axis to go into the object)
                        point_ijk = new[] {-value[3], -value[4], -value[5]};
                        var objPoseAbs = obj.PoseAbs();

                        // Calculate the point in Absolute coordinates (with respect to the station)
                        point_xyz = objPoseAbs * point_xyz;
                        point_ijk = objPoseAbs.Rot3x3() * point_ijk;
                        break;
                    }
                }
            }


            // Calculate the absolute pose of the robot reference
            var refPoseAbs = robotRef.PoseAbs();

            // Calculate the absolute pose of the robot tool 
            var robotPoseAbs = refPoseAbs * robotRef.Pose();

            // Calculate the robot pose for the selected target and use the tool Y axis as a reference
            // (we try to get the pose that has the Y axis as close as possible as the current robot position)
            var pose_surface_abs = Mat.xyzijk_2_pose(point_xyz, point_ijk, robotPoseAbs.VY());

            if (!pose_surface_abs.IsHomogeneous())
            {
                Console.WriteLine(@"Something went wrong");
                return;
            }

            // calculate the pose of the target (relative to the reference frame)
            var pose_surface_rel = refPoseAbs.inv() * pose_surface_abs;

            // add a target and update the pose
            var target_new = _rdk.AddTarget("T1", robotRef, _robot);
            target_new.SetAsCartesianTarget();
            target_new.SetJoints(_robot
                .Joints()); // this is only important if we want to remember the current configuration
            target_new.SetPose(pose_surface_rel);


            /*RoboDK.Item frame = RDK.getItem("FrameTest");
            double[] xyzwpr = { 1000.0, 2000.0, 3000.0, 12.0 * Math.PI / 180.0, 84.98 * Math.PI / 180.0, 90.0 * Math.PI / 180.0 };
            Mat pose;
            pose = Mat.FromUR(xyzwpr);
            double[] xyzwpr_a = pose.ToUR();
            double[] xyzwpr_b = pose.ToUR_Alternative();

            Console.WriteLine("Option one:");
            Console.Write(Mat.FromUR(xyzwpr_a).ToString());
            Console.Write(xyzwpr_a[0]); Console.WriteLine("");
            Console.Write(xyzwpr_a[1]); Console.WriteLine("");
            Console.Write(xyzwpr_a[2]); Console.WriteLine("");
            Console.Write(xyzwpr_a[3] * 180.0 / Math.PI); Console.WriteLine("");
            Console.Write(xyzwpr_a[4] * 180.0 / Math.PI); Console.WriteLine("");
            Console.Write(xyzwpr_a[5] * 180.0 / Math.PI); Console.WriteLine("");

            Console.WriteLine("Option Two:");
            Console.Write(Mat.FromUR(xyzwpr_b).ToString());
            Console.Write(xyzwpr_b[0]); Console.WriteLine("");
            Console.Write(xyzwpr_b[1]); Console.WriteLine("");
            Console.Write(xyzwpr_b[2]); Console.WriteLine("");
            Console.Write(xyzwpr_b[3] * 180.0 / Math.PI); Console.WriteLine("");
            Console.Write(xyzwpr_b[4] * 180.0 / Math.PI); Console.WriteLine("");
            Console.Write(xyzwpr_b[5] * 180.0 / Math.PI); Console.WriteLine("");*/
        }

        //----------------------------------------------------------------------------------------------
        //----------------------------------------------------------------------------------------------
        //----------------------------------------------------------------------------------------------
        //----------------------------------------------------------------------------------------------
        // The following code is meant to show a sample to manage different administrator rights 
        // to provide acces to a subset of RoboDK features.
        // The Setup_Notification_Icon will add a notification icon in the task bar with lock/unlock options
        private void Setup_Notification_Icon()
        {
            // Create the NotifyIcon.
            var ProcessTaskBar = new NotifyIcon();

            // setup context menu
            var components = new Container();
            var contextMenu = new ContextMenu();
            var optionLock = new MenuItem();
            var optionUnlock = new MenuItem();

            // Initialize contextMenu
            contextMenu.MenuItems.AddRange(new[] {optionLock, optionUnlock});

            // Initialize option_Lock
            optionLock.Index = 0;
            optionLock.Text = @"Lock RoboDK Station";
            optionLock.Click += RoboDK_Lock;
            // Initialize option_Unlock
            optionUnlock.Index = 1;
            optionUnlock.Text = @"Unlock RoboDK Station";
            optionUnlock.Click += RoboDK_Unlock;
            //
            ProcessTaskBar.ContextMenu = contextMenu;

            // The Text property sets the text that will be displayed,
            // in a tooltip, when the mouse hovers over the systray icon.
            ProcessTaskBar.Icon = Resources.IconRoboDK;
            ProcessTaskBar.Text = @"RoboDK";
            ProcessTaskBar.Visible = true;

            // Handle the DoubleClick event to activate the form.
            ProcessTaskBar.DoubleClick += Show_RoboDK;
        }

        private void Show_RoboDK(object sender, EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) return;
            _rdk.ShowRoboDK();
        }

        private void RoboDK_Lock(object sender, EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) return;

            //RDK.setFlagsRoboDK(RoboDK.FLAG_ROBODK_MENUEDIT_ACTIVE | RoboDK.FLAG_ROBODK_MENUEDIT_ACTIVE);
            _rdk.SetWindowFlags(WindowFlags.None);
            _rdk.SetItemFlags(null, ItemFlags.None);
            if (_robot.Valid()) _robot.SetItemFlags();
        }

        // Called when the user selects to unlock a feature
        private void RoboDK_Unlock(object sender, EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) return;

            var code = "1234";
            if (ShowInputDialog(ref code, "Default admin: 1234 or 0000") == DialogResult.OK)
            {
                if (code == "1234")
                {
                    _rdk.SetWindowFlags(WindowFlags.All);
                    _rdk.SetItemFlags(null);
                    _rdk.ShowRoboDK();
                }
                else if (code == "0000")
                {
                    _rdk.SetWindowFlags(
                        WindowFlags.DoubleClick |
                        WindowFlags.MenuActive |
                        WindowFlags.MenuEditActive |
                        WindowFlags.MenuToolsActive);
                    _rdk.SetItemFlags(null, ItemFlags.Editable);
                    _rdk.ShowRoboDK();
                }
                else
                {
                    MessageBox.Show(@"Invalid code!");
                }
            }
        }

        // ShowInputDialog will create a dialog box on the fly to provide an access code
        private static DialogResult ShowInputDialog(ref string input, string message)
        {
            var size = new Size(250, 70 + 23);
            var inputBox = new Form
            {
                FormBorderStyle = FormBorderStyle.FixedDialog, ClientSize = size, Text = @"Enter Code"
            };

            // (default admin: 1234, or 0000)";

            var label = new Label {Size = new Size(size.Width - 10, 23), Location = new Point(5, 5), Text = message};
            inputBox.Controls.Add(label);

            var textBox = new TextBox
            {
                Size = new Size(size.Width - 10, 23), Location = new Point(5, 5 + 23), Text = input
            };
            inputBox.Controls.Add(textBox);

            var okButton = new Button
            {
                DialogResult = DialogResult.OK,
                Name = "okButton",
                Size = new Size(75, 23),
                Text = @"&OK",
                Location = new Point(size.Width - 80 - 80, 39 + 23)
            };
            inputBox.Controls.Add(okButton);

            var cancelButton = new Button
            {
                DialogResult = DialogResult.Cancel,
                Name = "cancelButton",
                Size = new Size(75, 23),
                Text = @"&Cancel",
                Location = new Point(size.Width - 80, 39 + 23)
            };
            inputBox.Controls.Add(cancelButton);

            inputBox.AcceptButton = okButton;
            inputBox.CancelButton = cancelButton;

            var result = inputBox.ShowDialog();
            input = textBox.Text;
            return result;
        }
    }
}