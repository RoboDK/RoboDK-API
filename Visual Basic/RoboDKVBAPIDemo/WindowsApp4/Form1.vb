Imports RoboDk
Imports RoboDk.API.Model
Imports System.Threading

Public Class Form1
	Declare Auto Function SetParent Lib "user32.dll" (ByVal hWndChild As IntPtr, ByVal hWndNewParent As IntPtr) As Integer
	'Global Variables for the api class and interface
	Dim RDK As RoboDk.API.RoboDK
	Dim iRDK As RoboDk.API.IRoboDK
	' Variable to store currently selected robot
	Dim ROBOT As RoboDk.API.IItem

	Dim debug As New Integer


	Private Sub Form1_Load(sender As System.Object, e As System.EventArgs) Handles MyBase.Load
		' Create an instance of the RoboDK class
		RDK = New RoboDk.API.RoboDK With {
			.SafeMode = False
		}
		'iRDK = New 
		' Initialise to a local copy of the roboDK class
		' Specify an IP here to connect to a remote instance of RoboDK
		RDK.Connect()
		notifybar.Text = "RoboDK Started"
	End Sub


	Private Sub btnLoadFile_Click(sender As Object, e As EventArgs) Handles btnLoadFile.Click
		Dim select_file = New OpenFileDialog()
		select_file.Title = "Select a file to open with RoboDK"
		' Grab file from the roboDK library path
		select_file.InitialDirectory = RDK.GetParameter("PATH_LIBRARY").Replace("/", "\")
		If select_file.ShowDialog() = DialogResult.OK Then
			Dim sFileName = select_file.FileName
			Dim newItem As RoboDk.API.IItem
			newItem = RDK.AddFile(sFileName)

			If newItem.Valid Then
				' Set text
				notifybar.Text = "Loaded: " + newItem.Name
			Else
				notifybar.Text = "Could not load: " + newItem.Name
			End If
		End If
	End Sub


	Private Sub btnSelectRobot_Click(sender As Object, e As EventArgs) Handles btnSelectRobot.Click
		SelectRobot()
	End Sub

	Private Sub btnMoveRobotHome_Click(sender As Object, e As EventArgs) Handles btnMoveRobotHome.Click
		If Check_ROBOT() = False Then
			Return
		End If

		' Get Home Joints
		Dim joints_home() = ROBOT.JointsHome()
		' Move to home
		ROBOT.MoveJ(joints_home)

	End Sub

	Private Sub btnRunTestProgram_Click(sender As Object, e As EventArgs) Handles btnRunTestProgram.Click
		'Dim n_sides As Integer = 6

		'Dim pose_ref = ROBOT.Pose()

		'' Set the simulation speed (ratio = real time / simulated time)
		'' 1 second of the simulator equals 5 second in real time
		'RDK.SetSimulationSpeed(5)


		'Try
		'	Dim frame As RoboDk.API.Mat = ROBOT.PoseFrame()
		'	Dim tool As RoboDk.API.Mat = ROBOT.PoseTool()
		'	Dim runmode As Integer = RDK.GetRunMode()



		'	' Program start
		'	ROBOT.MoveJ(pose_ref)
		'	ROBOT.SetPoseFrame(frame)  ' Set the reference frame
		'	ROBOT.SetPoseTool(tool)    ' Set the tool frame: important for Online Programming
		'	ROBOT.SetSpeed(100)        ' Set Speed To 100 mm/s
		'	ROBOT.SetZoneData(5)       ' Set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)

		'	For i As Integer = 0 To n_sides
		'		Dim angle As Double = (CDbl(i) / n_sides) * 2.0 * Math.PI
		'		Dim pose_i As RoboDk.API.Mat = pose_ref * RoboDk.API.Mat.rotz(angle) * RoboDk.API.Mat.transl(100, 0, 0) * RoboDk.API.Mat.rotz(-angle)
		'		Dim xyzwpr As Double() = pose_i.ToXYZRPW()
		'		ROBOT.MoveL(xyzwpr)
		'	Next

		'	ROBOT.MoveL(pose_ref)

		'Catch ex As Exception
		'	notifybar.Text = "The robot has been deleted: " + ex.Message
		'End Try
		'Dim tempPtr As New IntPtr
		'tempPtr = RDK.GetWindowHandle()
		'tempPtr = RDK.GetWindowHandle()
		'tempPtr = RDK.GetWindowHandle()

		'SetParent(RDK.GetWindowHandle(), RoboDkPanel.Handle)
		'RDK.SetWindowState(WindowState.Normal)
		'RDK.SetWindowState(WindowState.Maximized)
		'RDK.ShowRoboDK()


	End Sub

	Public Sub SelectRobot()
		notifybar.Text = "Selecting robot..."
		ROBOT = RDK.ItemUserPick("Select a robot", RoboDk.API.Model.ItemType.Robot)
		' You can also select a robot by name
		'ROBOT = RDK.ItemUserPick("Fanuc M - 10IA/10S", RoboDk.API.Model.ItemType.Robot)

		' You can also select any object in the simulation
		'ROBOT = RDK.ItemUserPick("Select a robot (Work around)", RoboDk.API.Model.ItemType.Any)

		If ROBOT.Valid Then
			' This will create a new communication link (another instance of the RoboDK API),
			' this Is useful if we are moving 2 robots at the same time.
			ROBOT.NewLink()
			notifybar.Text = "Using robot: " + ROBOT.Name()
		Else
			notifybar.Text = "Robot not available. Load a file first"
		End If
	End Sub

	Public Function Check_ROBOT() As Boolean

		If (ROBOT Is Nothing) Or (ROBOT.Valid() = False) Then
			notifybar.Text = "A robot has not been selected. Load a station or a robot file first."
			Return False
		End If

		Try
			notifybar.Text = "Using robot: " + ROBOT.Name()
		Catch ex As Exception
			notifybar.Text = "The robot has been deleted: " + ex.Message
			Return False
		End Try

		Return True
	End Function

End Class
