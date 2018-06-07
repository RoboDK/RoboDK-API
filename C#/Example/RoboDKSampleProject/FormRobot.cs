using System;
using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Diagnostics;

namespace ProjectRoboDK
{
    public partial class FormRobot : Form
    {

        // RDK holds the main object to interact with RoboDK.
        // The RoboDK application starts when a RoboDK object is created.
        RoboDK RDK = null;

        // Keep the ROBOT item as a global variable
        RoboDK.Item ROBOT = null;

        // Define if the robot movements will be blocking
        const bool MOVE_BLOCKING = false;
        
        public FormRobot() {
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
                RDK = new RoboDK();

                // Check if RoboDK started properly
                if (Check_RDK())
                {
                    notifybar.Text = "RoboDK is Running...";

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

                this.Icon = SamplePanelRoboDK.Properties.Resources.IconRoboDK;
            }
        }
        
        private void FormRobot_Shown(object sender, EventArgs e)
        {
            // Start RoboDK here if we want to start it after the form is displayed
        }

        /// <summary>
        /// Stop running RoboDK when the Form is closed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void FormRobot_FormClosed(object sender, FormClosedEventArgs e)
        {
            if (!Check_RDK()) { return; }
            // Force to stop and close RoboDK (optional)
            // RDK.CloseAllStations(); // close all stations
            // RDK.Save("path_to_save.rdk"); // save the project if desired
            RDK.CloseRoboDK();
            RDK = null;
        }

        /// <summary>
        /// Check if the RDK object is ready.
        /// Returns True if the RoboDK API is available or False if the RoboDK API is not available.
        /// </summary>
        /// <returns></returns>
        public bool Check_RDK()
        {
            // check if the RDK object has been initialised:
            if (RDK == null)
            {
                notifybar.Text = "RoboDK has not been started";
                return false;
            }

            // Check if the RDK API is connected
            if (!RDK.Connected()) 
            {
                notifybar.Text = "Connecting to RoboDK...";
                // Attempt to connect to the RDK API
                if (!RDK.Connect())
                {
                    notifybar.Text = "Problems using the RoboDK API. The RoboDK API is not available...";
                    return false;
                }
            }
            return true;
        }

        private void btnLoadFile_Click(object sender, EventArgs e)
        {
            // Make sure the RoboDK API is running:
            if (!Check_RDK()) { return; }

            // Show the File dialog to select a file:
            OpenFileDialog select_file = new OpenFileDialog();
            select_file.Title = "Select a file to open with RoboDK";
            select_file.InitialDirectory = RDK.getParam("PATH_LIBRARY").Replace("/", "\\"); // open the RoboDK library by default
            if (select_file.ShowDialog() == DialogResult.OK)  // show the dialog
            {
                string filename = select_file.FileName;
                // Check if it is a RoboDK station file (.rdk extension)
                // If desired, close any other stations that have previously been open
                /*if (filename.EndsWith(".rdk", StringComparison.InvariantCultureIgnoreCase))
                {
                    CloseAllStations();
                }*/

                // retrieve the newly added item
                RoboDK.Item item = RDK.AddFile(select_file.FileName);
                if (item.Valid())
                {
                    notifybar.Text = "Loaded: " + item.Name();
                    // attempt to retrieve the ROBOT variable (a robot available in the station)
                    SelectRobot();
                }
                else
                {
                    notifybar.Text = "Could not load: " + filename;
                }
            }
        }

        /// <summary>
        /// Update the ROBOT variable by choosing the robot available in the currently open station
        /// If more than one robot is available, a popup will be displayed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void btnSelectRobot_Click(object sender, EventArgs e)
        {
            SelectRobot();
        }

        /// <summary>
        /// Update the ROBOT variable by choosing the robot available in the currently open station
        /// If more than one robot is available, a popup will be displayed
        /// </summary>
        public void SelectRobot()
        {
            notifybar.Text = "Selecting robot...";
            if (!Check_RDK()) {
                ROBOT = null;
                return;
            }
            ROBOT = RDK.ItemUserPick("Select a robot", RoboDK.ITEM_TYPE_ROBOT); // select robot among available robots
            //ROBOT = RL.getItem("ABB IRB120", ITEM_TYPE_ROBOT); // select by name
            //ITEM = RL.ItemUserPick("Select an item"); // Select any item in the station
            if (ROBOT.Valid())
            {
                ROBOT.NewLink(); // This will create a new communication link (another instance of the RoboDK API), this is useful if we are moving 2 robots at the same time.                
                notifybar.Text = "Using robot: " + ROBOT.Name();
            }
            else
            {
                notifybar.Text = "Robot not available. Load a file first";
            }
        }

        /// <summary>
        /// Check if the ROBOT object is available and valid. It will make sure that we can operate with the ROBOT object.
        /// </summary>
        /// <returns></returns>
        public bool Check_ROBOT(bool ignore_busy_status=false)
        {
            if (!Check_RDK()) {
                return false;
            }
            if (ROBOT == null || !ROBOT.Valid()) {
                notifybar.Text = "A robot has not been selected. Load a station or a robot file first.";
                return false;
            }
            try
            {
                notifybar.Text = "Using robot: " + ROBOT.Name();
            }
            catch (RoboDK.RDKException rdkex)
            {
                notifybar.Text = "The robot has been deleted: " + rdkex.Message;
                return false;
            }

            // Safe check: If we are doing non blocking movements, we can check if the robot is doing other movements with the Busy command
            if (!MOVE_BLOCKING && (!ignore_busy_status && ROBOT.Busy()))
            {
                notifybar.Text = "The robot is busy!! Try later...";
                return false;
            }
            return true;
        }

        /// <summary>
        /// Close all the stations available in RoboDK (top level items)
        /// </summary>
        public void CloseAllStations()
        {
            // Get all the RoboDK stations available
            RoboDK.Item[] all_stations = RDK.getItemList(RoboDK.ITEM_TYPE_STATION);
            foreach (RoboDK.Item station in all_stations)
            {
                notifybar.Text = "Closing " + station.Name();
                // this will close a station without asking to save:
                station.Delete();
            }
        }




        ////////////////////////////////////////////////////////////////
        ////////////////////////////////////////////////////////////////
        //////////////// Example to get/set robot position /////////////////
        
        private void btnMoveRobotHome_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT()) { return; }

            double[] joints_home = ROBOT.JointsHome();

            ROBOT.MoveJ(joints_home);
        }

        private void btnGetJoints_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT(true)) { return; }

            double[] joints = ROBOT.Joints();
            Mat pose = ROBOT.Pose();

            // update the joints
            string strjoints = Values_2_String(joints);
            txtJoints.Text = strjoints;

            // update the pose as xyzwpr
            double[] xyzwpr = pose.ToTxyzRxyz();
            string strpose = Values_2_String(xyzwpr);
            txtPosition.Text = strpose;
        }

        private void btnMoveJoints_Click(object sender, EventArgs e)
        {
            // retrieve the robot joints from the text and validate input
            double[] joints = String_2_Values(txtJoints.Text);

            // make sure RDK is running and we have a valid input
            if (!Check_ROBOT() || joints == null) { return; }

            try
            {
                ROBOT.MoveJ(joints, MOVE_BLOCKING);
            }
            catch (RoboDK.RDKException rdkex)
            {
                notifybar.Text = "Problems moving the robot: " + rdkex.Message;
                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
            }
        }

        private void btnMovePose_Click(object sender, EventArgs e)
        {
            // retrieve the robot position from the text and validate input
            double[] xyzwpr = String_2_Values(txtPosition.Text);

            // make sure RDK is running and we have a valid input
            if (!Check_ROBOT() || xyzwpr == null) { return; }

            //Mat pose = Mat.FromXYZRPW(xyzwpr);
            Mat pose = Mat.FromTxyzRxyz(xyzwpr);
            try
            {
                ROBOT.MoveJ(pose, MOVE_BLOCKING);
            }
            catch (RoboDK.RDKException rdkex)
            {
                notifybar.Text = "Problems moving the robot: " + rdkex.Message;
                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
            }
        }


        /// <summary>
        /// Convert a list of numbers provided as a string to an array of values
        /// </summary>
        /// <param name="strvalues"></param>
        /// <returns></returns>
        public double[] String_2_Values(string strvalues)
        {
            double[] dvalues = null;
            try
            {
                dvalues = Array.ConvertAll(strvalues.Split(','), Double.Parse);
            }
            catch (System.FormatException ex)
            {
                notifybar.Text = "Invalid input: " + strvalues;
            }
            return dvalues;
        }

        /// <summary>
        /// Convert an array of values as a string
        /// </summary>
        /// <param name="dvalues"></param>
        /// <returns></returns>
        public string Values_2_String(double[] dvalues)
        {
            if (dvalues == null || dvalues.Length < 1)
            {
                return "Invalid values";
            }
            // Not supported on .NET Framework 2.0:
            //string strvalues = String.Join(" , ", dvalues.Select(p => p.ToString("0.0")).ToArray());
            string strvalues = dvalues[0].ToString();
            for (int i=1; i<dvalues.Length; i++)
            {
                strvalues += " , " + dvalues[i].ToString();
            }
            
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
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            // Check that there is a link with RoboDK:
            btnOLPdone.Enabled = false;
            if (!Check_ROBOT()) { return; }            

            // Important: stop any previous program generation (if we selected offline programming mode)
            RDK.Finish();

            // Set to simulation mode:
            RDK.setRunMode(RoboDK.RUNMODE_SIMULATE);
        }
        private void rad_RunMode_Program_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            btnOLPdone.Enabled = true;
            if (!Check_ROBOT()) { return; }

            // Important: Disconnect from the robot for safety
            ROBOT.Finish();

            // Set to simulation mode:
            RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG);

            // specify a program name, a folder to save the program and a post processor if desired
            RDK.ProgramStart("NewProgram");
        }
        private void btnOLPdone_Click(object sender, EventArgs e)
        {
            if (!Check_ROBOT()) { return; }

            // this will trigger program generation
            //RDK.Finish();
            ROBOT.Finish(); // we must close the socket linked to the robot

            // set back to simulation
            rad_RunMode_Simulation.PerformClick();
        }

        private void rad_RunMode_Online_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            btnOLPdone.Enabled = false;
            // Check that there is a link with RoboDK:
            if (!Check_ROBOT()) { return; }

            // Important: stop any previous program generation (if we selected offline programming mode)
            RDK.Finish();

            // Connect to real robot
            if (ROBOT.Connect())
            {
                // Set to Run on Robot robot mode:
                RDK.setRunMode(RoboDK.RUNMODE_RUN_ROBOT);
            }
            else
            {
                notifybar.Text = "Can't connect to the robot. Check connection and parameters.";
                rad_RunMode_Simulation.AutoCheck = true;

            }
        }


        ///////////////////////////////////////////////////////////////
        ///////////////////////////////////////////////////////////////
        ////////////// Example to run a program //////////////

        private void btnRun_Program_Click(object sender, EventArgs e)
        {
            // Check that there is a link with RoboDK:
            if (!Check_RDK()) { return; }

            string progname = txtRunProgram.Text;

            // Retrieve the program item program
            RoboDK.Item prog = RDK.getItem(progname);
            if (prog.Valid() && (prog.Type() == RoboDK.ITEM_TYPE_PROGRAM_PYTHON || prog.Type() == RoboDK.ITEM_TYPE_PROGRAM))
            {
                prog.RunProgram();
                return;

                //double percent_OK = prog.Update(RoboDK.COLLISION_ON, 3600, null, 4, 4) * 100.0;
                //notifybar.Text = "Program check: " + percent_OK.ToString("0.0") + " % " + (percent_OK == 100.0 ? " OK " : " WARNING!!");


                string error_msg;
                Mat joints_mat;
                prog.InstructionListJoints(out error_msg, out joints_mat, 4, 4, "", RoboDK.COLLISION_ON);
                string result = joints_mat.ToString();


                return;

                if (rad_RunMode_Online.Checked)
                {
                    // force to run on robot
                    prog.setRunType(RoboDK.PROGRAM_RUN_ON_ROBOT);      
                }
                else if (rad_RunMode_Program.Checked)
                {
                    // generate a program call to another program
                    ROBOT.RunCodeCustom(progname);
                }
                else
                {
                    // force to run in simulation mode
                    prog.setRunType(RoboDK.PROGRAM_RUN_ON_SIMULATOR); 
                }
                                                                   //prog.setRunType(RoboDK.PROGRAM_RUN_ON_SIMULATOR);  // if RunMode == RUNMODE_RUN_ON_ROBOT it will start the program on the robot controller
                notifybar.Text = "Running program: " + txtRunProgram.Text;
                prog.RunProgram();
            }
            else
            {
                notifybar.Text = "The program " + txtRunProgram.Text + " does not exist.";
                //MessageBox.Show("The program does not exist.");
            }
        }



        //////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////
        ///////////////// GROUP DISPLAY MODE ////////////////
        // Import SetParent/GetParent command from user32 dll to identify if the main window is a subprocess
        [DllImport("user32.dll")]
        static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        private void rad_RoboDK_show_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            // Check RoboDK connection
            if (!Check_RDK()) { return; }

            // unhook from the integrated panel it is inside the main panel
            if (RDK.PROCESS != null)
            {
                SetParent(RDK.PROCESS.MainWindowHandle, IntPtr.Zero);
            }

            RDK.setWindowState(RoboDK.WINDOWSTATE_NORMAL); // removes Cinema mode and shows the screen
            RDK.setWindowState(RoboDK.WINDOWSTATE_MAXIMIZED); // shows maximized

            // set the form to the minimum size
            this.Height = this.MinimumSize.Height;
            this.Width = this.MinimumSize.Width;


            //Alternatively: RDK.ShowRoboDK();
            this.BringToFront(); // show on top of RoboDK
        }

        private void rad_RoboDK_hide_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            if (!Check_RDK()) { return; }

            RDK.setWindowState(RoboDK.WINDOWSTATE_HIDDEN);
            //Alternatively: RDK.HideRoboDK();

            // set the form to the minimum size
            this.Size = this.MinimumSize;
            this.Width = this.MinimumSize.Width;
        }

        private void rad_RoboDK_Integrated_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            // skip if the radio button became unchecked
            if (!rad_RoboDK_Integrated.Checked) { return; }

            if (!Check_RDK()) { return; }
            if (RDK.PROCESS == null)
            {
                notifybar.Text = "Invalid handle. Close RoboDK and open RoboDK with this application";
                rad_RoboDK_show.PerformClick();
                return;
            }

            // hook window pointer to the integrated panel
            SetParent(RDK.PROCESS.MainWindowHandle, panel_rdk.Handle);

            //RDK.setWindowState(RoboDK.WINDOWSTATE_SHOW); // shows if it was hidden
            RDK.setWindowState(RoboDK.WINDOWSTATE_CINEMA); // sets cinema mode (no toolbar, no title bar)
            RDK.setWindowState(RoboDK.WINDOWSTATE_MAXIMIZED); // maximizes the screen

            // make form height larger
            this.Size = new Size(this.Size.Width, 700); 
                   
            // Alternatively: RDK.setWindowState(RoboDK.WINDOWSTATE_SHOW);
        }


        [DllImport("user32.dll", SetLastError = true)]
        public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);

        private void panel_Resized(object sender, EventArgs e)
        {
            if (!rad_RoboDK_Integrated.Checked) { return; }

            // resize the content of the panel_rdk when it is resized
            MoveWindow(RDK.PROCESS.MainWindowHandle, 0, 0, panel_rdk.Width, panel_rdk.Height, true);
        }

        //////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////
        /////////////////// FOR INCREMENTAL MOVEMENT ////////////////////////

        private void rad_Move_wrt_Reference_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            Set_Incremental_Buttons_Cartesian();
        }

        private void rad_Move_wrt_Tool_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            Set_Incremental_Buttons_Cartesian();
        }

        private void rad_Move_Joints_CheckedChanged(object sender, EventArgs e)
        {
            // skip if the radio button became unchecked
            RadioButton rad_sender = (RadioButton)sender;
            if (!rad_sender.Checked) { return; }

            Set_Incremental_Buttons_Joints();
        }

        private void Set_Incremental_Buttons_Cartesian()
        {
            // update label units for the step:
            lblstepIncrement.Text = "Step (mm):";

            // Text to display on the positive motion buttons for incremental Cartesian movements:
            btnTXpos.Text = "+Tx";
            btnTYpos.Text = "+Ty";
            btnTZpos.Text = "+Tz";
            btnRXpos.Text = "+Rx";
            btnRYpos.Text = "+Ry";
            btnRZpos.Text = "+Rz";

            // Text to display on the negative motion buttons for incremental Cartesian movements:
            btnTXneg.Text = "-Tx";
            btnTYneg.Text = "-Ty";
            btnTZneg.Text = "-Tz";
            btnRXneg.Text = "-Rx";
            btnRYneg.Text = "-Ry";
            btnRZneg.Text = "-Rz";
        }

        private void Set_Incremental_Buttons_Joints()
        {
            // update label units for the step:
            lblstepIncrement.Text = "Step (deg):";

            // Text to display on the positive motion buttons for Incremental Joint movement:
            btnTXpos.Text = "+J1";
            btnTYpos.Text = "+J2";
            btnTZpos.Text = "+J3";
            btnRXpos.Text = "+J4";
            btnRYpos.Text = "+J5";
            btnRZpos.Text = "+J6";

            // Text to display on the positive motion buttons for Incremental Joint movement:
            btnTXneg.Text = "-J1";
            btnTYneg.Text = "-J2";
            btnTZneg.Text = "-J3";
            btnRXneg.Text = "-J4";
            btnRYneg.Text = "-J5";
            btnRZneg.Text = "-J6";
        }


        /// <summary>
        /// Move the the robot relative to the TCP
        /// </summary>
        /// <param name="movement"></param>
        private void Incremental_Move(string button_name)
        {
            if (!Check_ROBOT()) { return; }

            notifybar.Text = "Button selected: " + button_name;

            if (button_name.Length < 3)
            {
                notifybar.Text = "Internal problem! Button name should be like +J1, -Tx, +Rz or similar";
                return;
            }

            // get the the sense of motion the first character as '+' or '-'
            double move_step = 0.0;
            if (button_name[0] == '+')
            {
                move_step = +Convert.ToDouble(numStep.Value);
            }
            else if (button_name[0] == '-')
            {
                move_step = -Convert.ToDouble(numStep.Value);
            }
            else
            {
                notifybar.Text = "Internal problem! Unexpected button name";
                return;
            }

            //////////////////////////////////////////////
            //////// if we are moving in the joint space:
            if (rad_Move_Joints.Checked)
            {
                double[] joints = ROBOT.Joints();
                
                // get the moving axis (1, 2, 3, 4, 5 or 6)
                int joint_id = Convert.ToInt32(button_name[2].ToString()) - 1; // important, double array starts at 0

                joints[joint_id] = joints[joint_id] + move_step;

                try
                {
                    ROBOT.MoveJ(joints, MOVE_BLOCKING);
                    //ROBOT.MoveL(joints, MOVE_BLOCKING);
                }
                catch (RoboDK.RDKException rdkex)
                {
                    notifybar.Text = "The robot can't move to the target joints: " + rdkex.Message;
                    //MessageBox.Show("The robot can't move to " + new_pose.ToString());
                }
            }
            else
            {
                //////////////////////////////////////////////
                //////// if we are moving in the cartesian space
                // Button name examples: +Tx, -Tz, +Rx, +Ry, +Rz

                int move_id = 0;

                string[] move_types = new string[6] { "Tx", "Ty", "Tz", "Rx", "Ry", "Rz" };
                
                for (int i=0; i<6; i++)
                {
                    if (button_name.EndsWith(move_types[i]))
                    {
                        move_id = i;
                        break;
                    }
                }
                double[] move_xyzwpr = new double[6] { 0, 0, 0, 0, 0, 0 };
                move_xyzwpr[move_id] = move_step;
                Mat movement_pose = Mat.FromTxyzRxyz(move_xyzwpr);

                // the the current position of the robot (as a 4x4 matrix)
                Mat robot_pose = ROBOT.Pose();

                // Calculate the new position of the robot
                Mat new_robot_pose;
                bool is_TCP_relative_move = rad_Move_wrt_Tool.Checked;
                if (is_TCP_relative_move)
                {
                    // if the movement is relative to the TCP we must POST MULTIPLY the movement
                    new_robot_pose = robot_pose * movement_pose;
                }
                else
                {
                    // if the movement is relative to the reference frame we must PRE MULTIPLY the XYZ translation:
                    // new_robot_pose = movement_pose * robot_pose;
                    // Note: Rotation applies from the robot axes.

                    Mat transformation_axes = new Mat(robot_pose);
                    transformation_axes.setPos(0, 0, 0);
                    Mat movement_pose_aligned = transformation_axes.inv() * movement_pose * transformation_axes;
                    new_robot_pose = robot_pose * movement_pose_aligned;
                }
                
                // Then, we can do the movement:
                try
                {
                    ROBOT.MoveJ(new_robot_pose, MOVE_BLOCKING);
                }
                catch (RoboDK.RDKException rdkex)
                {
                    notifybar.Text = "The robot can't move to " + new_robot_pose.ToString();
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
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTXneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTYpos_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTYneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTZpos_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnTZneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRXpos_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRXneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRYpos_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRYneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRZpos_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            Incremental_Move(btn.Text); // send the text of the button as parameter
        }

        private void btnRZneg_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
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
            catch (RoboDK.RDKException rdkex)
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


            var stopwatch = new Stopwatch();
            int ntests = 1000;

            stopwatch.Reset();
            stopwatch.Start();
            for (var i = 0; i < ntests; i++)
            {
                var robot_name = ROBOT.Name();
            }
            stopwatch.Stop();
            Console.WriteLine($"Calling .Name() took {stopwatch.ElapsedMilliseconds*1000/ntests} micro seconds on average");

            stopwatch.Reset();
            stopwatch.Start();
            for (var i = 0; i < ntests; i++)
            {
                var joints = ROBOT.Joints();
            }
            stopwatch.Stop();
            Console.WriteLine($"Calling .Joints() took {stopwatch.ElapsedMilliseconds * 1000 / ntests} micro seconds on average");
            return;



            RDK.EventsListen();
            RDK.EventsLoop();


            RDK.WaitForEvent(out int evt, out RoboDK.Item itm);
            RDK.SampleRoboDkEvent(evt, itm);
            return;


            if (!Check_ROBOT()) { return; }

            //RDK.EventsListen();
            //return;
            
             /* if (RDK.Connected())
             {
                 RDK.CloseRoboDK();
             }*/

            int n_sides = 6;

            Mat pose_ref = ROBOT.Pose();

            // Set the simulation speed (ratio = real time / simulated time)
            RDK.setSimulationSpeed(5); // 1 second of the simulator equals 1 second in real time

            try
            {

                // retrieve the reference frame and the tool frame (TCP)
                Mat frame = ROBOT.PoseFrame();
                Mat tool = ROBOT.PoseTool();
                int runmode = RDK.RunMode(); // retrieve the run mode 
                
                // Program start
                ROBOT.MoveJ(pose_ref);
                ROBOT.setPoseFrame(frame);  // set the reference frame
                ROBOT.setPoseTool(tool);    // set the tool frame: important for Online Programming
                ROBOT.setSpeed(100);        // Set Speed to 100 mm/s
                ROBOT.setZoneData(5);       // set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
                ROBOT.RunCodeCustom("CallOnStart");
                for (int i = 0; i <= n_sides; i++)
                {
                    double angle = ((double) i / n_sides) * 2.0 * Math.PI;
                    Mat pose_i = pose_ref * Mat.rotz(angle) * Mat.transl(100, 0, 0) * Mat.rotz(-angle);
                    ROBOT.RunCodeCustom("Moving to point " + i.ToString(), RoboDK.INSTRUCTION_COMMENT);
                    double[] xyzwpr = pose_i.ToXYZRPW();
                    ROBOT.MoveL(pose_i);
                }
                ROBOT.RunCodeCustom("CallOnFinish");
                ROBOT.MoveL(pose_ref);
            }
            catch (RoboDK.RDKException rdkex)
            {
                notifybar.Text = "Failed to complete the movement: " + rdkex.Message;
            }

            return;

            //--------------------------------------------------
            // Other tests used for debugging...

            //RDK.SetInteractiveMode(RoboDK.SELECT_MOVE, RoboDK.DISPLAY_REF_TX | RoboDK.DISPLAY_REF_TY | RoboDK.DISPLAY_REF_PXY | RoboDK.DISPLAY_REF_RZ, new List<RoboDK.Item>() { ROBOT }, new List<int>() { RoboDK.DISPLAY_REF_ALL });
            //return;


            RoboDK.Item[] references = RDK.getItemList(RoboDK.ITEM_TYPE_FRAME);
            UInt64[] cam_list = new UInt64[references.Length];
            for (int i = 0; i < references.Length; i++)
            {
                cam_list[i] = RDK.Cam2D_Add(references[i], "FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480");
            }

            System.Threading.Thread.Sleep(2000);

            for (int i = 0; i < references.Length; i++)
            {
                RDK.Cam2D_SetParams(references[i].Name(), cam_list[i]);
            }

            System.Threading.Thread.Sleep(2000);

            // close all cameras
            RDK.Cam2D_Close();

            return;

            // Example to change the robot parameters (DHM parameters as defined by Craig 1986)
            // for joints 1 to 6, index i changes from 0 to 5:
            // dhm[i][] = [alpha, a, theta, d];


            // first point
            double[] p1 = { 0, 0, 0 };
            double[] p2 = { 1000, 0, 0 };
            Mat reference = Mat.transl(0, 0, 100);
            double[] p_collision = new double[3]; // this can be null if we don't need the collision point

            RoboDK.Item item = RDK.Collision_Line(p1, p2, reference, p_collision);

            string name;
            if (item.Valid())
            {
                name = item.Name();
            }
            else
            {
                // item not valid
            }

            return;



            double[][] dhm;
            Mat pose_base;
            Mat pose_tool;
            // get the current robot parameters:
           /* RDK.getRobotParams(ROBOT, out dhm, out pose_base, out pose_tool);

            // change the mastering values:
            for (int i = 0; i < 6; i++)
            {
                dhm[i][2] = dhm[i][2] + 1 * Math.PI / 180.0; // change theta i (mastering value, add 1 degree)
            }

            // change the base and tool distances:
            dhm[0][3] = dhm[0][3] + 5; // add 5 mm to d1
            dhm[5][3] = dhm[5][3] + 5; // add 5 mm to d6

            // update the robot parameters back:
            RDK.setRobotParams(ROBOT, dhm, pose_base, pose_tool);*/

            return;

            // Example to rotate the view around the Z axis
            /*RoboDK.Item item_robot = RDK.ItemUserPick("Select the robot you want", RoboDK.ITEM_TYPE_ROBOT);
            item_robot.MoveL(item_robot.Pose() * Mat.transl(0, 0, 50));
            return;*/


            RDK.setViewPose(RDK.ViewPose() * Mat.rotx(10 * 3.141592 / 180));
            return;

            //---------------------------------------------------------
            // Sample to generate a program using a C# script
            if (ROBOT != null && ROBOT.Valid())
            {
                //ROBOT.Finish();
                //RDK.Finish();
                // RDK.Connect(); // redundant
                RDK.Finish(); // ignores any previous activity to generate the program
                RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG); // Very important to set first
                RDK.ProgramStart("TestProg1", "C:\\Users\\Albert\\Desktop\\", "KAIRO.py", ROBOT);
                double[] joints1 = new double[6] { 1, 2, -50, 4, 5, 6 };
                double[] joints2 = new double[6] { -1, -2, -50, 4, 5, 6 };

                ROBOT.MoveJ(joints1);
                ROBOT.MoveJ(joints2);
                ROBOT.Finish(); // provoke program generation



                RDK.Finish(); // ignores any previous activity to generate the program
                RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG); // Very important to set first
                RDK.ProgramStart("TestProg2_no_robot", "C:\\Users\\Albert\\Desktop\\", "Fanuc_RJ3.py");
                RDK.RunProgram("Program1");
                RDK.RunCode("Output Raw code");
                RDK.Finish(); // provoke program generation



                ROBOT.Finish(); // ignores any previous activity to generate the program
                RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG); // Very important to set first
                RDK.ProgramStart("TestProg3", "C:\\Users\\Albert\\Desktop\\", "GSK.py", ROBOT);
                double[] joints3 = new double[6] { 10, 20, 30, 40, 50, 60 };
                double[] joints4 = new double[6] { -10, -20, -30, 40, 50, 60 };

                ROBOT.MoveJ(joints3);
                ROBOT.MoveJ(joints4);
                ROBOT.Finish(); // provoke program generation
                
            }
            else
            {
                Console.WriteLine("No robot selected");
            }
            return;

            //---------------------------------------------------------
            RoboDK.Item prog = RDK.getItem("", RoboDK.ITEM_TYPE_PROGRAM);
            string err_msg;
            Mat jnt_list;
            //prog.InstructionListJoints(out err_msg, out jnt_list, 0.5, 0.5);
            prog.InstructionListJoints(out err_msg, out jnt_list, 5, 5);
            for (int j = 0; j < jnt_list.cols; j++)
            {
                for (int i = 0; i < jnt_list.rows; i++)
                {
                    Console.Write(jnt_list[i, j]);
                    Console.Write("    ");
                }
                Console.WriteLine("");
            }

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
            NotifyIcon ProcessTaskBar = new System.Windows.Forms.NotifyIcon();

            // setup context menu
            Container components = new System.ComponentModel.Container();
            ContextMenu contextMenu = new System.Windows.Forms.ContextMenu();
            MenuItem option_Lock = new System.Windows.Forms.MenuItem();
            MenuItem option_Unlock = new System.Windows.Forms.MenuItem();

            // Initialize contextMenu
            contextMenu.MenuItems.AddRange(new System.Windows.Forms.MenuItem[] { option_Lock, option_Unlock });

            // Initialize option_Lock
            option_Lock.Index = 0;
            option_Lock.Text = "Lock RoboDK Station";
            option_Lock.Click += new System.EventHandler(this.RoboDK_Lock);
            // Initialize option_Unlock
            option_Unlock.Index = 1;
            option_Unlock.Text = "Unlock RoboDK Station";
            option_Unlock.Click += new System.EventHandler(this.RoboDK_Unlock);
            //
            ProcessTaskBar.ContextMenu = contextMenu;

            // The Text property sets the text that will be displayed,
            // in a tooltip, when the mouse hovers over the systray icon.
            ProcessTaskBar.Icon = SamplePanelRoboDK.Properties.Resources.IconRoboDK;
            ProcessTaskBar.Text = "RoboDK";
            ProcessTaskBar.Visible = true;

            // Handle the DoubleClick event to activate the form.
            ProcessTaskBar.DoubleClick += new System.EventHandler(this.Show_RoboDK);
        }
        private void Show_RoboDK(Object sender, System.EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) { return; }
            RDK.ShowRoboDK();
        }

        private void RoboDK_Lock(Object sender, System.EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) { return; }

            //RDK.setFlagsRoboDK(RoboDK.FLAG_ROBODK_MENUEDIT_ACTIVE | RoboDK.FLAG_ROBODK_MENUEDIT_ACTIVE);
            RDK.setFlagsRoboDK(RoboDK.FLAG_ROBODK_NONE);
            RDK.setFlagsItem(null, RoboDK.FLAG_ITEM_NONE);
            if (ROBOT.Valid())
            {
                RDK.setFlagsItem(ROBOT, RoboDK.FLAG_ITEM_ALL);
            }
        }

        // Called when the user selects to unlock a feature
        private void RoboDK_Unlock(Object sender, System.EventArgs e)
        {
            // Check RoboDK connection
            if (!Check_RDK()) { return; }

            string code = "1234";
            if (ShowInputDialog(ref code, "Default admin: 1234 or 0000") == DialogResult.OK)
            {
                if (code == "1234")
                {
                    RDK.setFlagsRoboDK(RoboDK.FLAG_ROBODK_ALL);
                    RDK.setFlagsItem(null, RoboDK.FLAG_ITEM_ALL);
                    RDK.ShowRoboDK();
                }
                else if (code == "0000")
                {
                    RDK.setFlagsRoboDK(RoboDK.FLAG_ROBODK_DOUBLE_CLICK | RoboDK.FLAG_ROBODK_MENU_ACTIVE | RoboDK.FLAG_ROBODK_MENUEDIT_ACTIVE | RoboDK.FLAG_ROBODK_MENUTOOLS_ACTIVE);
                    RDK.setFlagsItem(null, RoboDK.FLAG_ITEM_EDITABLE);
                    RDK.ShowRoboDK();
                }
                else
                {
                    MessageBox.Show("Invalid code!");
                }
            }
        }

        // ShowInputDialog will create a dialog box on the fly to provide an access code
        private static DialogResult ShowInputDialog(ref string input, string message)
        {
            System.Drawing.Size size = new System.Drawing.Size(250, 70 + 23);
            Form inputBox = new Form();

            inputBox.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            inputBox.ClientSize = size;
            inputBox.Text = "Enter Code";// (default admin: 1234, or 0000)";

            System.Windows.Forms.Label label = new Label();
            label.Size = new System.Drawing.Size(size.Width - 10, 23);
            label.Location = new System.Drawing.Point(5, 5);
            label.Text = message;
            inputBox.Controls.Add(label);

            System.Windows.Forms.TextBox textBox = new TextBox();
            textBox.Size = new System.Drawing.Size(size.Width - 10, 23);
            textBox.Location = new System.Drawing.Point(5, 5 + 23);
            textBox.Text = input;
            inputBox.Controls.Add(textBox);

            Button okButton = new Button();
            okButton.DialogResult = System.Windows.Forms.DialogResult.OK;
            okButton.Name = "okButton";
            okButton.Size = new System.Drawing.Size(75, 23);
            okButton.Text = "&OK";
            okButton.Location = new System.Drawing.Point(size.Width - 80 - 80, 39 + 23);
            inputBox.Controls.Add(okButton);

            Button cancelButton = new Button();
            cancelButton.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            cancelButton.Name = "cancelButton";
            cancelButton.Size = new System.Drawing.Size(75, 23);
            cancelButton.Text = "&Cancel";
            cancelButton.Location = new System.Drawing.Point(size.Width - 80, 39 + 23);
            inputBox.Controls.Add(cancelButton);

            inputBox.AcceptButton = okButton;
            inputBox.CancelButton = cancelButton;

            DialogResult result = inputBox.ShowDialog();
            input = textBox.Text;
            return result;
        }


    }
}


