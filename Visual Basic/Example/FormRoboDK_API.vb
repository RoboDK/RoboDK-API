Option Strict On
Option Explicit On

Imports System.Runtime.InteropServices

Public Class FormRoboDK_API
    Private RDK As RoboDK = Nothing
    Private ROBOT As RoboDK.Item = Nothing
    Const MOVE_BLOCKING As Boolean = False

    Public Sub New()
        InitializeComponent()
    End Sub

    Private Sub FormRobot_Load(sender As Object, e As EventArgs) Handles Me.Load
        ' Start RoboDK here if we want to start it before the Form is displayed
        If Not Check_RDK() Then
            RDK = New RoboDK("localhost", True)

            ' Check if RoboDK started properly
            If Check_RDK() Then
                notifybar.Text = "RoboDK is Running..."

                ' attempt to auto select the robot:
                'SelectRobot()
            End If

            ' set default movement on the simulator only:
            rad_RunMode_Simulation.PerformClick()

            ' display RoboDK integrated by default:
            rad_RoboDK_Integrated.PerformClick()

            ' Set incremental moves in cartesian space with respect to the robot reference frame
            rad_Move_wrt_Reference.PerformClick()

            ' set movement steps of 50 mm or 50 deg by default
            numStep.Value = 50

            ' other ways to Start RoboDK
            'bool START_HIDDEN = false;
            'RDK = new RoboDK("", START_HIDDEN); // default connection, starts RoboDK visible if it has not been started
            'RDK = new RoboDK("localhost", false, 20599); //start visible, use specific communication port to not interfere with other applications
            'RDK = new RoboDK("localhost", true, 20599); //start hidden,  use specific communication port to not interfere with other applications


        End If
    End Sub

    Private Sub FormRobot_Shown(sender As Object, e As EventArgs) Handles Me.Shown
        ' Start RoboDK here if we want to start it after the form is displayed
    End Sub

    ''' <summary>
    ''' Stop running RoboDK when the Form is closed
    ''' </summary>
    ''' <param name="sender"></param>
    ''' <param name="e"></param>
    Private Sub FormRobot_FormClosed(sender As Object, e As FormClosedEventArgs) Handles Me.FormClosed
        ' Force to stop and close RoboDK (optional)
        ' RDK.CloseAllStations(); // close all stations
        ' RDK.Save("path_to_save.rdk"); // save the project if desired
        RDK.CloseRoboDK()
        RDK = Nothing
    End Sub

    ''' <summary>
    ''' Check if the RDK object is ready.
    ''' Returns True if the RoboDK API is available or False if the RoboDK API is not available.
    ''' </summary>
    ''' <returns></returns>
    Public Function Check_RDK() As Boolean
        ' check if the RDK object has been initialised:
        If RDK Is Nothing Then
            notifybar.Text = "RoboDK has not been started"
            Return False
        End If

        ' Check if the RDK API is connected
        If Not RDK.Connected() Then
            notifybar.Text = "Connecting to RoboDK..."
            ' Attempt to connect to the RDK API
            If Not RDK.Connect() Then
                notifybar.Text = "Problems using the RoboDK API. The RoboDK API is not available..."
                Return False
            End If
        End If
        Return True
    End Function

    Private Sub btnSelectStation_Click(sender As Object, e As EventArgs) Handles btnSelectStation.Click
        LoadFile("Station files (*.rdk)|*.rdk")
    End Sub

    ''' <summary>
    ''' Update the ROBOT variable by choosing the robot available in the currently open station
    ''' If more than one robot is available, a popup will be displayed
    ''' </summary>
    ''' <param name="sender"></param>
    ''' <param name="e"></param>
    Private Sub btnLoadFile_Click(sender As Object, e As EventArgs) Handles btnLoadAPT.Click
        If ComboBoxMillingSetups.SelectedIndex >= 0 Then
            Dim machining As RoboDK.Item = RDK.getItem(ComboBoxMillingSetups.Items(ComboBoxMillingSetups.SelectedIndex).ToString, RoboDK.ITEM_TYPE_MACHINING)
            If machining.Valid Then
                Using select_file As New OpenFileDialog()
                    select_file.Title = "Select an APT file"
                    select_file.InitialDirectory = RDK.getParam("PATH_LIBRARY").Replace("/", "\")
                    select_file.Filter = "APT files (*.APT)|*.APT"
                    If select_file.ShowDialog() = DialogResult.OK Then
                        Dim actualCursor As Cursor = Me.Cursor
                        Me.Cursor = Cursors.WaitCursor

                        Dim status As Integer
                        Dim ncFile As String = select_file.FileName

                        UnHook(panel_rdk)
                        'load NC program
                        Dim receivedItem As RoboDK.Item = machining.setMillingParameters(ncFile, status)
                        ReHook(panel_rdk)

                        Dim prog As String = receivedItem.Name

                        Me.Cursor = actualCursor
                        Select Case status
                            Case RoboDK.NC_POSITIONS_NOT_REACHABLE
                                notifybar.Text = "Program " & prog & " error: Some positions are not reachable"
                            Case RoboDK.NC_OK
                                notifybar.Text = "Program " & prog & " successfully loaded"
                            Case Else
                                notifybar.Text = "Program " & prog & " status unknown=" & status
                        End Select
                    End If
                End Using
            End If
        End If
        'LoadFile()
    End Sub

    Private Sub LoadFile(Optional extension As String = "")
        ' Make sure the RoboDK API is running:
        If Not Check_RDK() Then
            Return
        End If

        ' Show the File dialog to select a file:
        Dim select_file As New OpenFileDialog()
        select_file.Title = "Select a file to open with RoboDK"
        select_file.InitialDirectory = RDK.getParam("PATH_LIBRARY").Replace("/", "\")
        If extension <> "" Then
            select_file.Filter = extension
        End If

        ' open the RoboDK library by default
        If select_file.ShowDialog() = DialogResult.OK Then
            Dim isStation As Boolean = False
            ' show the dialog
            Dim filename As String = select_file.FileName
            ' Check if it is a RoboDK station file (.rdk extension)
            ' If desired, close any other stations that have previously been open
            If (filename.EndsWith(".rdk", StringComparison.InvariantCultureIgnoreCase)) Then
                isStation = True
                CloseAllStations()
            End If

            ' retrieve the newly added item
            Dim item As RoboDK.Item = RDK.AddFile(select_file.FileName)
            If item.Valid() Then
                notifybar.Text = "Loaded: " + item.Name()
                ' attempt to retrieve the ROBOT variable (a robot available in the station) & more...
                If isStation Then
                    SelectRobot()
                    SelectMachining()
                    SelectProgram()
                End If
            Else
                notifybar.Text = Convert.ToString("Could not load: ") & filename
            End If
        End If
    End Sub




    ''' <summary>
    ''' Update the ROBOT variable by choosing the robot available in the currently open station
    ''' If more than one robot is available, a popup will be displayed
    ''' </summary>
    Public Sub SelectRobot()
        notifybar.Text = "Selecting robot..."
        If Not Check_RDK() Then
            ROBOT = Nothing
            Return
        End If

        Dim listRobots As List(Of String) = RDK.getItemListNames(RoboDK.ITEM_TYPE_ROBOT).ToList()
        For Each robotName As String In listRobots
            If robotName.ToLower.Contains("robot") Then
                ROBOT = RDK.getItem(robotName, RoboDK.ITEM_TYPE_ROBOT)
                Exit For
            End If
        Next

        If IsNothing(ROBOT) Then
            ROBOT = RDK.ItemUserPick("Select a robot", RoboDK.ITEM_TYPE_ROBOT)
        End If

        ' select robot among available robots
        'ROBOT = RL.getItem("ABB IRB120", ITEM_TYPE_ROBOT); // select by name
        'ITEM = RL.ItemUserPick("Select an item"); // Select any item in the station
        If ROBOT.Valid() Then
            notifybar.Text = "Using robot: " + ROBOT.Name()
        Else
            notifybar.Text = "Robot not available. Load a file first"
        End If
    End Sub

    Public Sub SelectProgram()
        notifybar.Text = "Selecting program..."
        If Not Check_RDK() Then
            Return
        End If

        Dim prog As RoboDK.Item = RDK.ItemUserPick("Select a program", RoboDK.ITEM_TYPE_PROGRAM)
        If prog.Valid Then
            txtRunProgram.Text = prog.Name
        End If
    End Sub

    Public Sub SelectMachining()
        notifybar.Text = "Selecting machining setup..."
        If Not Check_RDK() Then
            Return
        End If

        ComboBoxMillingSetups.Items.Clear()
        Dim machining As RoboDK.Item = RDK.ItemUserPick("Select a machining setup", RoboDK.ITEM_TYPE_MACHINING)
        If machining.Valid Then
            ComboBoxMillingSetups.Items.Add(machining.Name)
            ComboBoxMillingSetups.SelectedIndex = 0
        End If
    End Sub


    ''' <summary>
    ''' Check if the ROBOT object is available and valid. It will make sure that we can operate with the ROBOT object.
    ''' </summary>
    ''' <returns></returns>
    Public Function Check_ROBOT() As Boolean
        If Not Check_RDK() Then
            Return False
        End If
        If ROBOT Is Nothing OrElse Not ROBOT.Valid() Then
            notifybar.Text = "A robot has not been selected. Load a station or a robot file first."
            Return False
        End If
        Try
            notifybar.Text = "Using robot: " + ROBOT.Name()
        Catch rdkex As RoboDK.RDKException
            notifybar.Text = "The robot has been deleted: " + rdkex.Message
            Return False
        End Try

        ' Safe check: If we are doing non blocking movements, we can check if the robot is doing other movements with the Busy command
        If Not MOVE_BLOCKING AndAlso ROBOT.Busy() Then
            notifybar.Text = "The robot is busy!! Try later..."
            Return False
        End If
        Return True
    End Function

    ''' <summary>
    ''' Close all the stations available in RoboDK (top level items)
    ''' </summary>
    Public Sub CloseAllStations()
        ' Get all the RoboDK stations available
        Dim all_stations As RoboDK.Item() = RDK.getItemList(RoboDK.ITEM_TYPE_STATION)
        For Each station As RoboDK.Item In all_stations
            notifybar.Text = "Closing " + station.Name()
            ' this will close a station without asking to save:
            station.Delete()
        Next
    End Sub

    Private Sub ComboBoxMillingSetups_SelectedIndexChanged(sender As Object, e As System.EventArgs) Handles ComboBoxMillingSetups.SelectedIndexChanged
        Dim combo_sender As ComboBox = DirectCast(sender, ComboBox)
        btnLoadAPT.Enabled = (combo_sender.SelectedIndex >= 0)
    End Sub

#Region "Example to get/set robot position"

    Private Sub btnMoveRobotHome_Click(sender As Object, e As EventArgs) Handles btnMoveRobotHome.Click
        If Not Check_ROBOT() Then
            Return
        End If

        Dim joints_home As Double() = ROBOT.JointsHome()

        ROBOT.MoveJ(joints_home)
    End Sub

    Private Sub btnGetJoints_Click(sender As Object, e As EventArgs) Handles btnGetJoints.Click
        If Not Check_ROBOT() Then
            Return
        End If

        Dim joints As Double() = ROBOT.Joints()
        Dim pose As Mat = ROBOT.Pose()

        ' update the joints
        Dim strjoints As String = Values_2_String(joints)
        txtJoints.Text = strjoints

        ' update the pose as xyzwpr
        Dim xyzwpr As Double() = pose.ToTxyzRxyz()
        Dim strpose As String = Values_2_String(xyzwpr)
        txtPosition.Text = strpose
    End Sub

    Private Sub btnMoveJoints_Click(sender As Object, e As EventArgs) Handles btnMoveJoints.Click
        ' retrieve the robot joints from the text and validate input
        Dim joints As Double() = String_2_Values(txtJoints.Text)

        ' make sure RDK is running and we have a valid input
        If Not Check_ROBOT() OrElse joints Is Nothing Then
            Return
        End If

        Try
            ROBOT.MoveJ(joints, MOVE_BLOCKING)
        Catch rdkex As RoboDK.RDKException
            'MessageBox.Show("The robot can't move to " + new_pose.ToString());
            notifybar.Text = "Problems moving the robot: " + rdkex.Message
        End Try
    End Sub

    Private Sub btnMovePose_Click(sender As Object, e As EventArgs) Handles btnMovePose.Click
        ' retrieve the robot position from the text and validate input
        Dim xyzwpr As Double() = String_2_Values(txtPosition.Text)

        ' make sure RDK is running and we have a valid input
        If Not Check_ROBOT() OrElse xyzwpr Is Nothing Then
            Return
        End If

        'Mat pose = Mat.FromXYZRPW(xyzwpr);
        Dim pose As Mat = Mat.FromTxyzRxyz(xyzwpr)
        Try
            ROBOT.MoveJ(pose, MOVE_BLOCKING)
        Catch rdkex As RoboDK.RDKException
            'MessageBox.Show("The robot can't move to " + new_pose.ToString());
            notifybar.Text = "Problems moving the robot: " + rdkex.Message
        End Try
    End Sub



    ''' <summary>
    ''' Convert a list of numbers provided as a string to an array of values
    ''' </summary>
    ''' <param name="strvalues"></param>
    ''' <returns></returns>
    Public Function String_2_Values(strvalues As String) As Double()
        Dim dvalues As Double() = Nothing
        Try
            dvalues = Array.ConvertAll(strvalues.Split(","c), New Converter(Of String, Double)(AddressOf Double.Parse))
        Catch ex As System.FormatException
            notifybar.Text = Convert.ToString("Invalid input: ") & strvalues
        End Try
        Return dvalues
    End Function

    ''' <summary>
    ''' Convert an array of values as a string
    ''' </summary>
    ''' <param name="dvalues"></param>
    ''' <returns></returns>
    Public Function Values_2_String(dvalues As Double()) As String
        If dvalues Is Nothing Then
            Return "Invalid values"
        End If
        Dim strvalues As String = [String].Join(" , ", dvalues.[Select](Function(p) p.ToString("0.0")).ToArray())
        Return strvalues
    End Function
#End Region

#Region "Run mode types"
    '''////// 1- Simulation (default): RUNMODE_SIMULATE
    '''////// 2- Offline programming (default): RUNMODE_MAKE_ROBOTPROG
    '''////// 3- Online programming: RUNMODE_RUN_ROBOT. It moves the real robot
    Private Sub rad_RunMode_Simulation_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RunMode_Simulation.CheckedChanged
        btnStop_Simulation.Visible = False

        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        ' Check that there is a link with RoboDK:
        If Not Check_ROBOT() Then
            Return
        End If

        ' Important: stop any previous program generation (if we selected offline programming mode)
        RDK.Finish()

        ' Set to simulation mode:
        RDK.setRunMode(RoboDK.RUNMODE_SIMULATE)

        btnRun_Program.Text = "3/ Simulate program"
    End Sub

    Private Sub rad_RunMode_Program_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RunMode_Program.CheckedChanged
        btnStop_Simulation.Visible = False

        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        If Not Check_ROBOT() Then
            Return
        End If

        ' Important: Disconnect from the robot for safety
        ROBOT.Disconnect()

        ' Set to simulation mode:
        RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)

        btnRun_Program.Text = "3/ Generate program"
        ' specify a program name, a folder to save the program and a post processor if desired
        'RDK.ProgramStart("aProgram", defaultfolder:="C:\temp")
    End Sub

    Private Sub rad_RunMode_Online_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RunMode_Online.CheckedChanged
        btnStop_Simulation.Visible = False

        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        ' Check that there is a link with RoboDK:
        If Not Check_ROBOT() Then
            Return
        End If

        ' Important: stop any previous program generation (if we selected offline programming mode)
        RDK.Finish()

        ' Connect to real robot
        If ROBOT.Connect() Then
            ' Set to Run on Robot robot mode:
            RDK.setRunMode(RoboDK.RUNMODE_RUN_ROBOT)
        Else
            notifybar.Text = "Can't connect to the robot. Check connection and parameters."

            rad_RunMode_Simulation.AutoCheck = True
        End If
    End Sub
#End Region

    '''////////////////////////////////////////////////////////////
    '''////////////////////////////////////////////////////////////
    '''/////////// Example to run a program //////////////

    Private Sub btnRun_Program_Click(sender As Object, e As EventArgs) Handles btnRun_Program.Click
        ' Check that there is a link with RoboDK:
        If Not Check_RDK() Then
            Return
        End If

        Dim progname As String = txtRunProgram.Text
        Dim valid_instructions_number As Integer
        Dim program_distance_mm, program_time_seconds As Double
        Dim valid_program As Boolean
        ' Retrieve the program item program
        Dim prog As RoboDK.Item = RDK.getItem(progname, RoboDK.ITEM_TYPE_PROGRAM)
        If prog.Valid() Then
            If rad_RunMode_Program.Checked Then
                ' generate a program call to another program
                'ROBOT.RunCodeCustom(progname)

                If Not Check_ROBOT() Then
                    Return
                End If

                Dim actualCursor As Cursor = Me.Cursor
                Me.Cursor = Cursors.WaitCursor
                notifybar.Text = "Updating program: " + progname
                prog.Update(valid_instructions_number, program_time_seconds, program_distance_mm, valid_program)
                Me.Cursor = actualCursor

                If valid_program Then
                    Dim programTimeSpan As TimeSpan = TimeSpan.FromSeconds(program_time_seconds)
                    Dim programTimeSpanText As String = programTimeSpan.Minutes.ToString.PadLeft(2, "0"c) & "m" &
                                                        programTimeSpan.Seconds.ToString.PadLeft(2, "0"c) & "s"
                    If programTimeSpan.Hours > 0 Then
                        programTimeSpanText = programTimeSpan.Hours.ToString.PadLeft(2, "0"c) & "h" & programTimeSpanText
                    End If

                    notifybar.Text = "Creating program: " + progname & " / " & valid_instructions_number & " instructions / " & programTimeSpanText
                    Me.Refresh()

                    'program_distance_mm & "mm in " & programTimeSpanText
                    Using folderBrowser As New FolderBrowserDialog
                        If folderBrowser.ShowDialog = Windows.Forms.DialogResult.OK Then

                            UnHook(panel_rdk)
                            prog.MakeProgram(folderBrowser.SelectedPath)
                            ReHook(panel_rdk)

                            ' this will trigger program generation
                            RDK.Finish()

                        End If
                    End Using

                Else
                    notifybar.Text = "Program  " + progname & " failed updating"
                End If
            Else
                If rad_RunMode_Online.Checked Then
                    ' force to run on robot
                    prog.setRunType(RoboDK.PROGRAM_RUN_ON_ROBOT)
                Else
                    ' force to run in simulation mode
                    prog.setRunType(RoboDK.PROGRAM_RUN_ON_SIMULATOR)
                    btnStop_Simulation.Visible = True
                End If
                'prog.setRunType(RoboDK.PROGRAM_RUN_ON_SIMULATOR);  // if RunMode == RUNMODE_RUN_ON_ROBOT it will start the program on the robot controller
                prog.RunProgram()
                notifybar.Text = "Running program: " + progname
            End If
        Else
            'MessageBox.Show("The program does not exist.");
            notifybar.Text = "The program " + progname + " does not exist."
        End If
    End Sub


    Private Sub btnStop_Simulation_Click(sender As System.Object, e As System.EventArgs) Handles btnStop_Simulation.Click
        ' Check that there is a link with RoboDK:
        If Not Check_RDK() Then
            Return
        End If
        If ROBOT Is Nothing OrElse Not ROBOT.Valid() Then
            Return
        End If

        ROBOT.Stop()
        notifybar.Text = "Robot stopped"

        btnStop_Simulation.Visible = False
    End Sub

#Region "GROUP DISPLAY MODE"
    ' Import SetParent/GetParent command from user32 dll to identify if the main window is a subprocess
    <DllImport("user32.dll")> _
    Private Shared Function SetParent(hWndChild As IntPtr, hWndNewParent As IntPtr) As IntPtr
    End Function
    <DllImport("user32.dll")> _
    Private Shared Function GetParent(hWnd As IntPtr) As IntPtr
    End Function

    Private Sub rad_RoboDK_show_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RoboDK_show.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        ' Check RoboDK connection
        If Not Check_RDK() Then
            Return
        End If

        ' unhook from the integrated panel it is inside the main panel
        If RDK.PROCESS IsNot Nothing Then
            SetParent(RDK.PROCESS.MainWindowHandle, IntPtr.Zero)
        End If

        RDK.setWindowState(RoboDK.WINDOWSTATE_NORMAL) ' removes Cinema mode and shows the screen
        RDK.setWindowState(RoboDK.WINDOWSTATE_MAXIMIZED) ' shows maximized
        ' set the form to the minimum size
        Me.Height = Me.MinimumSize.Height
        Me.Width = Me.MinimumSize.Width


        'Alternatively: RDK.ShowRoboDK();
        Me.BringToFront() ' show on top of RoboDK
    End Sub

    Private Sub rad_RoboDK_hide_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RoboDK_hide.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        If Not Check_RDK() Then
            Return
        End If

        RDK.setWindowState(RoboDK.WINDOWSTATE_HIDDEN)
        'Alternatively: RDK.HideRoboDK();

        ' set the form to the minimum size
        Me.Size = Me.MinimumSize
        Me.Width = Me.MinimumSize.Width
    End Sub

    Private Sub rad_RoboDK_Integrated_CheckedChanged(sender As Object, e As EventArgs) Handles rad_RoboDK_Integrated.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        If Not Check_RDK() Then
            Return
        End If

        If RDK.PROCESS Is Nothing Then
            notifybar.Text = "Invalid handle. Close RoboDK and open RoboDK with this application"
            rad_RoboDK_show.PerformClick()
            Return
        End If

        RDK.setWindowState(RoboDK.WINDOWSTATE_NORMAL) ' removes Cinema mode and shows the screen
        'RDK.setWindowState(RoboDK.WINDOWSTATE_SHOW) ' shows if it was hidden
        RDK.setWindowState(RoboDK.WINDOWSTATE_CINEMA) ' sets cinema mode (no toolbar, no title bar)
        RDK.setWindowState(RoboDK.WINDOWSTATE_MAXIMIZED) ' maximizes the screen

        ' hook window pointer to the integrated panel
        SetParent(RDK.PROCESS.MainWindowHandle, panel_rdk.Handle)


        Me.Size = New Size(Me.Size.Width, 700) ' make form height larger

        ' Alternatively: 
        'RDK.setWindowState(RoboDK.WINDOWSTATE_SHOW)
    End Sub

    <DllImport("user32.dll", SetLastError:=True)> _
    Public Shared Function MoveWindow(hWnd As IntPtr, X As Integer, Y As Integer, nWidth As Integer, nHeight As Integer, bRepaint As Boolean) As Boolean
    End Function

    Private Sub panel_Resized(sender As Object, e As EventArgs) Handles panel_rdk.SizeChanged
        If IsNothing(RDK) OrElse Not rad_RoboDK_Integrated.Checked Then
            Return
        End If

        ' resize the content of the panel_rdk when it is resized
        MoveWindow(RDK.PROCESS.MainWindowHandle, 0, 0, panel_rdk.Width, panel_rdk.Height, True)
    End Sub


    ''' <summary>
    ''' Unset the Robodk Window to the application and moves it to same screen location (to keep same layout)
    ''' Solves RoboDK hanging when internal MessageBoxes are displayed by RoboDK (loading NC file / generating program)
    ''' </summary>
    ''' <remarks></remarks>
    Private Sub UnHook(parentPanel As Panel)
        If rad_RoboDK_Integrated.Checked Then
            Dim screenPanelPosition = Me.PointToScreen(parentPanel.Location)
            SetParent(RDK.PROCESS.MainWindowHandle, IntPtr.Zero)
            MoveWindow(RDK.PROCESS.MainWindowHandle, screenPanelPosition.X, screenPanelPosition.Y, parentPanel.Width, parentPanel.Height, True)
        End If
    End Sub

    ''' <summary>
    ''' Sets the Robodk Window to the dedicated panel of the application
    ''' Solves RoboDK hanging when internal MessageBoxes are displayed by RoboDK (loading NC file / generating program)
    ''' </summary>
    ''' <remarks></remarks>
    Private Sub ReHook(parentPanel As Panel)
        If rad_RoboDK_Integrated.Checked Then
            SetParent(RDK.PROCESS.MainWindowHandle, parentPanel.Handle)
            MoveWindow(RDK.PROCESS.MainWindowHandle, 0, 0, parentPanel.Width, parentPanel.Height, True)
        End If
    End Sub

#End Region

#Region "FOR INCREMENTAL MOVEMENT"


    Private Sub rad_Move_wrt_Reference_CheckedChanged(sender As Object, e As EventArgs) Handles rad_Move_wrt_Reference.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        Set_Incremental_Buttons_Cartesian()
    End Sub

    Private Sub rad_Move_wrt_Tool_CheckedChanged(sender As Object, e As EventArgs) Handles rad_Move_wrt_Tool.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        Set_Incremental_Buttons_Cartesian()
    End Sub

    Private Sub rad_Move_Joints_CheckedChanged(sender As Object, e As EventArgs) Handles rad_Move_Joints.CheckedChanged
        ' skip if the radio button became unchecked
        Dim rad_sender As RadioButton = DirectCast(sender, RadioButton)
        If Not rad_sender.Checked Then
            Return
        End If

        Set_Incremental_Buttons_Joints()
    End Sub

    Private Sub Set_Incremental_Buttons_Cartesian()
        ' update label units for the step:
        lblstepIncrement.Text = "Step (mm):"

        ' Text to display on the positive motion buttons for incremental Cartesian movements:
        btnTXpos.Text = "+Tx"
        btnTYpos.Text = "+Ty"
        btnTZpos.Text = "+Tz"
        btnRXpos.Text = "+Rx"
        btnRYpos.Text = "+Ry"
        btnRZpos.Text = "+Rz"

        ' Text to display on the negative motion buttons for incremental Cartesian movements:
        btnTXneg.Text = "-Tx"
        btnTYneg.Text = "-Ty"
        btnTZneg.Text = "-Tz"
        btnRXneg.Text = "-Rx"
        btnRYneg.Text = "-Ry"
        btnRZneg.Text = "-Rz"
    End Sub

    Private Sub Set_Incremental_Buttons_Joints()
        ' update label units for the step:
        lblstepIncrement.Text = "Step (deg):"

        ' Text to display on the positive motion buttons for Incremental Joint movement:
        btnTXpos.Text = "+J1"
        btnTYpos.Text = "+J2"
        btnTZpos.Text = "+J3"
        btnRXpos.Text = "+J4"
        btnRYpos.Text = "+J5"
        btnRZpos.Text = "+J6"

        ' Text to display on the positive motion buttons for Incremental Joint movement:
        btnTXneg.Text = "-J1"
        btnTYneg.Text = "-J2"
        btnTZneg.Text = "-J3"
        btnRXneg.Text = "-J4"
        btnRYneg.Text = "-J5"
        btnRZneg.Text = "-J6"
    End Sub


    ''' <summary>
    ''' Move the the robot relative to the TCP
    ''' </summary>
    ''' <param name="button_name"></param>
    Private Sub Incremental_Move(button_name As String)
        If Not Check_ROBOT() Then
            Return
        End If

        notifybar.Text = Convert.ToString("Button selected: ") & button_name

        If button_name.Length < 3 Then
            notifybar.Text = "Internal problem! Button name should be like +J1, -Tx, +Rz or similar"
            Return
        End If

        ' get the the sense of motion the first character as '+' or '-'
        Dim move_step As Double = 0.0
        If button_name(0) = "+"c Then
            move_step = +Convert.ToDouble(numStep.Value)
        ElseIf button_name(0) = "-"c Then
            move_step = -Convert.ToDouble(numStep.Value)
        Else
            notifybar.Text = "Internal problem! Unexpected button name"
            Return
        End If

        '///////////////////////////////////////////
        '///// if we are moving in the joint space:
        If rad_Move_Joints.Checked Then
            Dim joints As Double() = ROBOT.Joints()

            ' get the moving axis (1, 2, 3, 4, 5 or 6)
            Dim joint_id As Integer = Convert.ToInt32(button_name(2).ToString()) - 1
            ' important, double array starts at 0
            joints(joint_id) = joints(joint_id) + move_step

            Try
                'ROBOT.MoveL(joints, MOVE_BLOCKING);
                ROBOT.MoveJ(joints, MOVE_BLOCKING)
            Catch rdkex As RoboDK.RDKException
                'MessageBox.Show("The robot can't move to " + new_pose.ToString());
                notifybar.Text = "The robot can't move to the target joints: " + rdkex.Message
            End Try
        Else
            '///////////////////////////////////////////
            '///// if we are moving in the cartesian space
            ' Button name examples: +Tx, -Tz, +Rx, +Ry, +Rz

            Dim move_id As Integer = 0

            Dim move_types As String() = New String(5) {"Tx", "Ty", "Tz", "Rx", "Ry", "Rz"}

            For i As Integer = 0 To 5
                If button_name.EndsWith(move_types(i)) Then
                    move_id = i
                    Exit For
                End If
            Next
            Dim move_xyzwpr As Double() = New Double(5) {0, 0, 0, 0, 0, 0}
            move_xyzwpr(move_id) = move_step
            Dim movement_pose As Mat = Mat.FromTxyzRxyz(move_xyzwpr)

            ' the the current position of the robot (as a 4x4 matrix)
            Dim robot_pose As Mat = ROBOT.Pose()

            ' Calculate the new position of the robot
            Dim new_robot_pose As Mat
            Dim is_TCP_relative_move As Boolean = rad_Move_wrt_Tool.Checked
            If is_TCP_relative_move Then
                ' if the movement is relative to the TCP we must POST MULTIPLY the movement
                new_robot_pose = robot_pose * movement_pose
            Else
                ' if the movement is relative to the reference frame we must PRE MULTIPLY the XYZ translation:
                ' new_robot_pose = movement_pose * robot_pose;
                ' Note: Rotation applies from the robot axes.


                Dim transformation_axes As New Mat(robot_pose)
                transformation_axes.setPos(0, 0, 0)
                Dim movement_pose_aligned As Mat = transformation_axes.inv() * movement_pose * transformation_axes


                '
                '                    void NodeRobot::Set_HX_Delta(const Matrix4x4 deltaHX, const Matrix4x4 axesHwrtHB){
                '                        Matrix4x4 ROTadapt, invROTadapt, deltaHX_aligned;
                '                        Matrix4x4 invHX, newHX;
                '                        INV_4x4(invHX, HX);
                '                        MULT_4x4(ROTadapt, axesHwrtHB, invHX);//not sure if it is te right sense
                '                        H_SET_P(ROTadapt, 0,0,0);
                '                        INV_4x4(invROTadapt,ROTadapt);
                '                        MULT_4x4_3(deltaHX_aligned, ROTadapt, deltaHX, invROTadapt);
                '                        MULT_4x4(newHX, HX, deltaHX_aligned);
                '                        this->Set_HX_if_close(newHX);
                '                    }
                '                    

                new_robot_pose = robot_pose * movement_pose_aligned
            End If

            ' Then, we can do the movement:
            Try
                ROBOT.MoveJ(new_robot_pose, MOVE_BLOCKING)
            Catch rdkex As RoboDK.RDKException
                'MessageBox.Show("The robot can't move to " + new_pose.ToString());
                notifybar.Text = "The robot can't move to " + new_robot_pose.ToString()


                ' Some tips:
                ' retrieve the current pose of the robot: the active TCP with respect to the current reference frame
                ' Tip 1: use
                ' ROBOT.setFrame()
                ' to set a reference frame (object link or pose)
                '
                ' Tip 2: use
                ' ROBOT.setTool()
                ' to set a tool frame (object link or pose)
                '
                ' Tip 3: use
                ' ROBOT.MoveL_Collision(j1, new_move)
                ' to test if a movement is feasible by the robot before doing the movement
                '
            End Try
        End If

    End Sub



    Private Sub btnTXpos_Click(sender As Object, e As EventArgs) Handles btnTXpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnTXneg_Click(sender As Object, e As EventArgs) Handles btnTXneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnTYpos_Click(sender As Object, e As EventArgs) Handles btnTYpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnTYneg_Click(sender As Object, e As EventArgs) Handles btnTYneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnTZpos_Click(sender As Object, e As EventArgs) Handles btnTZpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnTZneg_Click(sender As Object, e As EventArgs) Handles btnTZneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRXpos_Click(sender As Object, e As EventArgs) Handles btnRXpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRXneg_Click(sender As Object, e As EventArgs) Handles btnRXneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRYpos_Click(sender As Object, e As EventArgs) Handles btnRYpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRYneg_Click(sender As Object, e As EventArgs) Handles btnRYneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRZpos_Click(sender As Object, e As EventArgs) Handles btnRZpos.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub

    Private Sub btnRZneg_Click(sender As Object, e As EventArgs) Handles btnRZneg.Click
        Dim btn As Button = DirectCast(sender, Button)
        Incremental_Move(btn.Text)
        ' send the text of the button as parameter
    End Sub



    '
    '        /// <summary>
    '        /// Move the the robot relative to the TCP
    '        /// </summary>
    '        /// <param name="movement"></param>
    '        private void Robot_Move_Cartesian(Mat add_move, bool is_relative_TCP = false)
    '        {
    '            if (!Check_ROBOT()) { return; }
    '
    '            // retrieve the current pose of the robot: the active TCP with respect to the current reference frame
    '            // Tip 1: use
    '            // ROBOT.setPoseFrame()
    '            // to set a reference frame (object link or pose)
    '            //
    '            // Tip 2: use
    '            // ROBOT.setPoseTool()
    '            // to set a tool frame (object link or pose)
    '            //
    '            // Tip 3: use
    '            // ROBOT.MoveL_Collision(j1, new_move)
    '            // to test if a movement is feasible by the robot before doing the movement
    '            // Collisions are not detected if collision detection is turned off.
    '            Mat robot_pose = ROBOT.Pose();
    '
    '            // calculate the new pose of the robot (post multiply)
    '            Mat new_pose = robot_pose * add_move;
    '            try
    '            {
    '                ROBOT.MoveJ(new_pose, MOVE_BLOCKING);
    '            }
    '            catch (RoboDK.RDKException rdkex)
    '            {
    '                notifybar.Text = "The robot can't move to " + new_pose.ToString();
    '                //MessageBox.Show("The robot can't move to " + new_pose.ToString());
    '            }
    '        }
    '
    '
    '
    '        /// <summary>
    '        /// This shows an example that moves the robot to a relative position given joint coordinates. The forward kinematics is calculated.
    '        /// </summary>
    '        /// <param name="joints"></param>
    '        private void Move_2_Approach(double[] joints)
    '        {
    '            if (!Check_ROBOT()) { return; }
    '            double approach_dist = 100; // Double.Parse(txtApproach.Text);
    '            Mat approach_mat = Mat.transl(0, 0, -approach_dist);
    '
    '            // calculate the position of the robot * tool            
    '            Mat tool_pose = ROBOT.PoseTool();                       // get the tool pose of the robot
    '            Mat robot_tool_pose = ROBOT.SolveFK(joints) * tool_pose * approach_mat; // get the new position (approach) of the robot*tool
    '            Mat robot_pose = robot_tool_pose * tool_pose.inv();  // get the position of the robot (from the base frame to the tool flange)
    '            double[] joints_app = ROBOT.SolveIK(robot_pose);           // calculate inverse kinematics to get the robot joints for the approach position
    '            if (joints_app == null)
    '            {
    '                MessageBox.Show("Position not reachable");
    '                return;
    '            }
    '            ROBOT.MoveJ(joints_app, MOVE_BLOCKING);
    '        }
    '        
#End Region

    '#Region "button for general purpose tests"
    '    Private Sub btnRunTestProgram_Click(sender As Object, e As EventArgs) Handles btnRunTestProgram.Click
    '        If Not Check_ROBOT() Then
    '            Return
    '        End If
    '        ' if (RDK.Connected())
    '        '             {
    '        '                 RDK.CloseRoboDK();
    '        '             }


    '        Dim n_sides As Integer = 6

    '        Dim pose_ref As Mat = ROBOT.Pose()

    '        ' Set the simulation speed (ratio = real time / simulated time)
    '        RDK.setSimulationSpeed(5)
    '        ' 1 second of the simulator equals 1 second in real time
    '        Try

    '            ' retrieve the reference frame and the tool frame (TCP)
    '            Dim frame As Mat = ROBOT.PoseFrame()
    '            Dim tool As Mat = ROBOT.PoseTool()
    '            Dim runmode As Integer = RDK.RunMode()
    '            ' retrieve the run mode 
    '            ' Program start
    '            ROBOT.MoveJ(pose_ref)
    '            ROBOT.setPoseFrame(frame)
    '            ' set the reference frame
    '            ROBOT.setPoseTool(tool)
    '            ' set the tool frame: important for Online Programming
    '            ROBOT.setSpeed(100)
    '            ' Set Speed to 100 mm/s
    '            ROBOT.setZoneData(5)
    '            ' set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
    '            ROBOT.RunCodeCustom("CallOnStart")
    '            For i As Integer = 0 To n_sides
    '                Dim angle As Double = (CDbl(i) / n_sides) * 2.0 * Math.PI
    '                Dim pose_i As Mat = pose_ref * Mat.rotz(angle) * Mat.transl(100, 0, 0) * Mat.rotz(-angle)
    '                ROBOT.RunCodeCustom("Moving to point " + i.ToString(), RoboDK.INSTRUCTION_COMMENT)
    '                Dim xyzwpr As Double() = pose_i.ToXYZRPW()
    '                ROBOT.MoveL(pose_i)
    '            Next
    '            ROBOT.RunCodeCustom("CallOnFinish")
    '            ROBOT.MoveL(pose_ref)
    '        Catch rdkex As RoboDK.RDKException
    '            notifybar.Text = "Failed to complete the movement: " + rdkex.Message
    '        End Try

    '        Return


    '        ' Example to rotate the view around the Z axis
    '        'RoboDK.Item item_robot = RDK.ItemUserPick("Select the robot you want", RoboDK.ITEM_TYPE_ROBOT);
    '        '            item_robot.MoveL(item_robot.Pose() * Mat.transl(0, 0, 50));
    '        '            return;



    '        RDK.setViewPose(RDK.ViewPose() * Mat.rotx(10 * 3.141592 / 180))
    '        Return

    '        '---------------------------------------------------------
    '        ' Sample to generate a program using a C# script
    '        If ROBOT IsNot Nothing AndAlso ROBOT.Valid() Then
    '            'ROBOT.Finish();
    '            'RDK.Finish();
    '            ' RDK.Connect(); // redundant
    '            RDK.Finish()
    '            ' ignores any previous activity to generate the program
    '            RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)
    '            ' Very important to set first
    '            RDK.ProgramStart("TestProg1", "C:\Users\Albert\Desktop\", "KAIRO.py", ROBOT)
    '            Dim joints1 As Double() = New Double(5) {1, 2, -50, 4, 5, 6}
    '            Dim joints2 As Double() = New Double(5) {-1, -2, -50, 4, 5, 6}

    '            ROBOT.MoveJ(joints1)
    '            ROBOT.MoveJ(joints2)
    '            ROBOT.Finish()
    '            ' provoke program generation


    '            RDK.Finish()
    '            ' ignores any previous activity to generate the program
    '            RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)
    '            ' Very important to set first
    '            RDK.ProgramStart("TestProg2_no_robot", "C:\Users\Albert\Desktop\", "Fanuc_RJ3.py")
    '            RDK.RunProgram("Program1")
    '            RDK.RunCode("Output Raw code")
    '            RDK.Finish()
    '            ' provoke program generation


    '            ROBOT.Finish()
    '            ' ignores any previous activity to generate the program
    '            RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)
    '            ' Very important to set first
    '            RDK.ProgramStart("TestProg3", "C:\Users\Albert\Desktop\", "GSK.py", ROBOT)
    '            Dim joints3 As Double() = New Double(5) {10, 20, 30, 40, 50, 60}
    '            Dim joints4 As Double() = New Double(5) {-10, -20, -30, 40, 50, 60}

    '            ROBOT.MoveJ(joints3)
    '            ROBOT.MoveJ(joints4)
    '            ' provoke program generation



    '            ROBOT.Finish()
    '        Else
    '            Console.WriteLine("No robot selected")
    '        End If
    '        Return

    '        '---------------------------------------------------------
    '        Dim prog As RoboDK.Item = RDK.getItem("", RoboDK.ITEM_TYPE_PROGRAM)
    '        Dim err_msg As String
    '        Dim jnt_list As Mat
    '        'prog.InstructionListJoints(out err_msg, out jnt_list, 0.5, 0.5);
    '        prog.InstructionListJoints(err_msg, jnt_list, 5, 5)
    '        For j As Integer = 0 To jnt_list.cols - 1
    '            For i As Integer = 0 To jnt_list.rows - 1
    '                Console.Write(jnt_list(i, j))
    '                Console.Write("    ")
    '            Next
    '            Console.WriteLine("")
    '        Next

    '        'RoboDK.Item frame = RDK.getItem("FrameTest");
    '        '            double[] xyzwpr = { 1000.0, 2000.0, 3000.0, 12.0 * Math.PI / 180.0, 84.98 * Math.PI / 180.0, 90.0 * Math.PI / 180.0 };
    '        '            Mat pose;
    '        '            pose = Mat.FromUR(xyzwpr);
    '        '            double[] xyzwpr_a = pose.ToUR();
    '        '            double[] xyzwpr_b = pose.ToUR_Alternative();
    '        '
    '        '            Console.WriteLine("Option one:");
    '        '            Console.Write(Mat.FromUR(xyzwpr_a).ToString());
    '        '            Console.Write(xyzwpr_a[0]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_a[1]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_a[2]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_a[3] * 180.0 / Math.PI); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_a[4] * 180.0 / Math.PI); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_a[5] * 180.0 / Math.PI); Console.WriteLine("");
    '        '
    '        '            Console.WriteLine("Option Two:");
    '        '            Console.Write(Mat.FromUR(xyzwpr_b).ToString());
    '        '            Console.Write(xyzwpr_b[0]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_b[1]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_b[2]); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_b[3] * 180.0 / Math.PI); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_b[4] * 180.0 / Math.PI); Console.WriteLine("");
    '        '            Console.Write(xyzwpr_b[5] * 180.0 / Math.PI); Console.WriteLine("");


    '    End Sub
    '#End Region



End Class
