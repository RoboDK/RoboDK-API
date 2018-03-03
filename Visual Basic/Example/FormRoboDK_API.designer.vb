<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class FormRoboDK_API
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.btnTXpos = New System.Windows.Forms.Button()
        Me.lblJ1 = New System.Windows.Forms.Label()
        Me.btnTYneg = New System.Windows.Forms.Button()
        Me.btnTYpos = New System.Windows.Forms.Button()
        Me.rad_RoboDK_Integrated = New System.Windows.Forms.RadioButton()
        Me.btnTZneg = New System.Windows.Forms.Button()
        Me.btnTZpos = New System.Windows.Forms.Button()
        Me.rad_RoboDK_hide = New System.Windows.Forms.RadioButton()
        Me.btnRZpos = New System.Windows.Forms.Button()
        Me.btnRZneg = New System.Windows.Forms.Button()
        Me.notifybar = New System.Windows.Forms.ToolStripStatusLabel()
        Me.groupRoboDKwindow = New System.Windows.Forms.GroupBox()
        Me.rad_RoboDK_show = New System.Windows.Forms.RadioButton()
        Me.btnTXneg = New System.Windows.Forms.Button()
        Me.groupRunMode = New System.Windows.Forms.GroupBox()
        Me.btnStop_Simulation = New System.Windows.Forms.Button()
        Me.rad_RunMode_Simulation = New System.Windows.Forms.RadioButton()
        Me.rad_RunMode_Online = New System.Windows.Forms.RadioButton()
        Me.rad_RunMode_Program = New System.Windows.Forms.RadioButton()
        Me.label3 = New System.Windows.Forms.Label()
        Me.txtRunProgram = New System.Windows.Forms.TextBox()
        Me.btnRun_Program = New System.Windows.Forms.Button()
        Me.numStep = New System.Windows.Forms.NumericUpDown()
        Me.lblstepIncrement = New System.Windows.Forms.Label()
        Me.btnMoveRobotHome = New System.Windows.Forms.Button()
        Me.rad_Move_Joints = New System.Windows.Forms.RadioButton()
        Me.rad_Move_wrt_Tool = New System.Windows.Forms.RadioButton()
        Me.groupIncrementalMove = New System.Windows.Forms.GroupBox()
        Me.rad_Move_wrt_Reference = New System.Windows.Forms.RadioButton()
        Me.btnRYpos = New System.Windows.Forms.Button()
        Me.btnRXneg = New System.Windows.Forms.Button()
        Me.btnRYneg = New System.Windows.Forms.Button()
        Me.btnRXpos = New System.Windows.Forms.Button()
        Me.statusStrip1 = New System.Windows.Forms.StatusStrip()
        Me.btnSelectStation = New System.Windows.Forms.Button()
        Me.btnLoadAPT = New System.Windows.Forms.Button()
        Me.btnMoveJoints = New System.Windows.Forms.Button()
        Me.txtJoints = New System.Windows.Forms.TextBox()
        Me.btnMovePose = New System.Windows.Forms.Button()
        Me.label1 = New System.Windows.Forms.Label()
        Me.btnGetJoints = New System.Windows.Forms.Button()
        Me.txtPosition = New System.Windows.Forms.TextBox()
        Me.panel_rdk = New System.Windows.Forms.Panel()
        Me.groupAbsoluteMove = New System.Windows.Forms.GroupBox()
        Me.ComboBoxMillingSetups = New System.Windows.Forms.ComboBox()
        Me.GroupBoxMachining = New System.Windows.Forms.GroupBox()
        Me.groupRoboDKwindow.SuspendLayout()
        Me.groupRunMode.SuspendLayout()
        CType(Me.numStep, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.groupIncrementalMove.SuspendLayout()
        Me.statusStrip1.SuspendLayout()
        Me.groupAbsoluteMove.SuspendLayout()
        Me.GroupBoxMachining.SuspendLayout()
        Me.SuspendLayout()
        '
        'btnTXpos
        '
        Me.btnTXpos.Location = New System.Drawing.Point(90, 104)
        Me.btnTXpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTXpos.Name = "btnTXpos"
        Me.btnTXpos.Size = New System.Drawing.Size(60, 25)
        Me.btnTXpos.TabIndex = 28
        Me.btnTXpos.Text = "X+"
        Me.btnTXpos.UseVisualStyleBackColor = True
        '
        'lblJ1
        '
        Me.lblJ1.AutoSize = True
        Me.lblJ1.Location = New System.Drawing.Point(84, 72)
        Me.lblJ1.Margin = New System.Windows.Forms.Padding(1, 0, 1, 0)
        Me.lblJ1.Name = "lblJ1"
        Me.lblJ1.Size = New System.Drawing.Size(100, 13)
        Me.lblJ1.TabIndex = 53
        Me.lblJ1.Text = "Cartesian Position"
        '
        'btnTYneg
        '
        Me.btnTYneg.Location = New System.Drawing.Point(10, 129)
        Me.btnTYneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTYneg.Name = "btnTYneg"
        Me.btnTYneg.Size = New System.Drawing.Size(60, 25)
        Me.btnTYneg.TabIndex = 29
        Me.btnTYneg.Text = "Y-"
        Me.btnTYneg.UseVisualStyleBackColor = True
        '
        'btnTYpos
        '
        Me.btnTYpos.Location = New System.Drawing.Point(90, 129)
        Me.btnTYpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTYpos.Name = "btnTYpos"
        Me.btnTYpos.Size = New System.Drawing.Size(60, 25)
        Me.btnTYpos.TabIndex = 30
        Me.btnTYpos.Text = "Y+"
        Me.btnTYpos.UseVisualStyleBackColor = True
        '
        'rad_RoboDK_Integrated
        '
        Me.rad_RoboDK_Integrated.AutoSize = True
        Me.rad_RoboDK_Integrated.Location = New System.Drawing.Point(10, 70)
        Me.rad_RoboDK_Integrated.Name = "rad_RoboDK_Integrated"
        Me.rad_RoboDK_Integrated.Size = New System.Drawing.Size(164, 17)
        Me.rad_RoboDK_Integrated.TabIndex = 2
        Me.rad_RoboDK_Integrated.Text = "Integrate RoboDK Window"
        Me.rad_RoboDK_Integrated.UseVisualStyleBackColor = True
        '
        'btnTZneg
        '
        Me.btnTZneg.Location = New System.Drawing.Point(10, 154)
        Me.btnTZneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTZneg.Name = "btnTZneg"
        Me.btnTZneg.Size = New System.Drawing.Size(60, 25)
        Me.btnTZneg.TabIndex = 31
        Me.btnTZneg.Text = "Z-"
        Me.btnTZneg.UseVisualStyleBackColor = True
        '
        'btnTZpos
        '
        Me.btnTZpos.Location = New System.Drawing.Point(90, 154)
        Me.btnTZpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTZpos.Name = "btnTZpos"
        Me.btnTZpos.Size = New System.Drawing.Size(60, 25)
        Me.btnTZpos.TabIndex = 32
        Me.btnTZpos.Text = "Z+"
        Me.btnTZpos.UseVisualStyleBackColor = True
        '
        'rad_RoboDK_hide
        '
        Me.rad_RoboDK_hide.AutoSize = True
        Me.rad_RoboDK_hide.Location = New System.Drawing.Point(10, 44)
        Me.rad_RoboDK_hide.Name = "rad_RoboDK_hide"
        Me.rad_RoboDK_hide.Size = New System.Drawing.Size(94, 17)
        Me.rad_RoboDK_hide.TabIndex = 1
        Me.rad_RoboDK_hide.Text = "Hide RoboDK"
        Me.rad_RoboDK_hide.UseVisualStyleBackColor = True
        '
        'btnRZpos
        '
        Me.btnRZpos.Location = New System.Drawing.Point(90, 229)
        Me.btnRZpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRZpos.Name = "btnRZpos"
        Me.btnRZpos.Size = New System.Drawing.Size(60, 25)
        Me.btnRZpos.TabIndex = 38
        Me.btnRZpos.Text = "rZ+"
        Me.btnRZpos.UseVisualStyleBackColor = True
        '
        'btnRZneg
        '
        Me.btnRZneg.Location = New System.Drawing.Point(10, 229)
        Me.btnRZneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRZneg.Name = "btnRZneg"
        Me.btnRZneg.Size = New System.Drawing.Size(60, 25)
        Me.btnRZneg.TabIndex = 37
        Me.btnRZneg.Text = "rZ-"
        Me.btnRZneg.UseVisualStyleBackColor = True
        '
        'notifybar
        '
        Me.notifybar.Name = "notifybar"
        Me.notifybar.Size = New System.Drawing.Size(95, 17)
        Me.notifybar.Text = "Notification area"
        '
        'groupRoboDKwindow
        '
        Me.groupRoboDKwindow.Controls.Add(Me.rad_RoboDK_Integrated)
        Me.groupRoboDKwindow.Controls.Add(Me.rad_RoboDK_hide)
        Me.groupRoboDKwindow.Controls.Add(Me.rad_RoboDK_show)
        Me.groupRoboDKwindow.Location = New System.Drawing.Point(10, 179)
        Me.groupRoboDKwindow.Name = "groupRoboDKwindow"
        Me.groupRoboDKwindow.Size = New System.Drawing.Size(175, 97)
        Me.groupRoboDKwindow.TabIndex = 67
        Me.groupRoboDKwindow.TabStop = False
        Me.groupRoboDKwindow.Text = "Display Mode"
        '
        'rad_RoboDK_show
        '
        Me.rad_RoboDK_show.AutoSize = True
        Me.rad_RoboDK_show.Location = New System.Drawing.Point(10, 18)
        Me.rad_RoboDK_show.Name = "rad_RoboDK_show"
        Me.rad_RoboDK_show.Size = New System.Drawing.Size(99, 17)
        Me.rad_RoboDK_show.TabIndex = 0
        Me.rad_RoboDK_show.Text = "Show RoboDK"
        Me.rad_RoboDK_show.UseVisualStyleBackColor = True
        '
        'btnTXneg
        '
        Me.btnTXneg.Location = New System.Drawing.Point(10, 104)
        Me.btnTXneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnTXneg.Name = "btnTXneg"
        Me.btnTXneg.Size = New System.Drawing.Size(60, 25)
        Me.btnTXneg.TabIndex = 27
        Me.btnTXneg.Text = "X-"
        Me.btnTXneg.UseVisualStyleBackColor = True
        '
        'groupRunMode
        '
        Me.groupRunMode.Controls.Add(Me.btnStop_Simulation)
        Me.groupRunMode.Controls.Add(Me.rad_RunMode_Simulation)
        Me.groupRunMode.Controls.Add(Me.rad_RunMode_Online)
        Me.groupRunMode.Controls.Add(Me.rad_RunMode_Program)
        Me.groupRunMode.Controls.Add(Me.label3)
        Me.groupRunMode.Controls.Add(Me.txtRunProgram)
        Me.groupRunMode.Controls.Add(Me.btnRun_Program)
        Me.groupRunMode.Location = New System.Drawing.Point(191, 11)
        Me.groupRunMode.Name = "groupRunMode"
        Me.groupRunMode.Size = New System.Drawing.Size(302, 115)
        Me.groupRunMode.TabIndex = 69
        Me.groupRunMode.TabStop = False
        Me.groupRunMode.Text = "Run Mode"
        '
        'btnStop_Simulation
        '
        Me.btnStop_Simulation.Location = New System.Drawing.Point(7, 89)
        Me.btnStop_Simulation.Margin = New System.Windows.Forms.Padding(1)
        Me.btnStop_Simulation.Name = "btnStop_Simulation"
        Me.btnStop_Simulation.Size = New System.Drawing.Size(68, 22)
        Me.btnStop_Simulation.TabIndex = 64
        Me.btnStop_Simulation.Text = "Stop"
        Me.btnStop_Simulation.UseVisualStyleBackColor = True
        Me.btnStop_Simulation.Visible = False
        '
        'rad_RunMode_Simulation
        '
        Me.rad_RunMode_Simulation.AutoSize = True
        Me.rad_RunMode_Simulation.Location = New System.Drawing.Point(7, 15)
        Me.rad_RunMode_Simulation.Name = "rad_RunMode_Simulation"
        Me.rad_RunMode_Simulation.Size = New System.Drawing.Size(80, 17)
        Me.rad_RunMode_Simulation.TabIndex = 49
        Me.rad_RunMode_Simulation.TabStop = True
        Me.rad_RunMode_Simulation.Text = "Simulation"
        Me.rad_RunMode_Simulation.UseVisualStyleBackColor = True
        '
        'rad_RunMode_Online
        '
        Me.rad_RunMode_Online.AutoSize = True
        Me.rad_RunMode_Online.Location = New System.Drawing.Point(194, 15)
        Me.rad_RunMode_Online.Name = "rad_RunMode_Online"
        Me.rad_RunMode_Online.Size = New System.Drawing.Size(100, 17)
        Me.rad_RunMode_Online.TabIndex = 47
        Me.rad_RunMode_Online.TabStop = True
        Me.rad_RunMode_Online.Text = "Run On Robot"
        Me.rad_RunMode_Online.UseVisualStyleBackColor = True
        Me.rad_RunMode_Online.Visible = False
        '
        'rad_RunMode_Program
        '
        Me.rad_RunMode_Program.AutoSize = True
        Me.rad_RunMode_Program.Location = New System.Drawing.Point(7, 41)
        Me.rad_RunMode_Program.Name = "rad_RunMode_Program"
        Me.rad_RunMode_Program.Size = New System.Drawing.Size(133, 17)
        Me.rad_RunMode_Program.TabIndex = 48
        Me.rad_RunMode_Program.TabStop = True
        Me.rad_RunMode_Program.Text = "Offline Programming"
        Me.rad_RunMode_Program.UseVisualStyleBackColor = True
        '
        'label3
        '
        Me.label3.AutoSize = True
        Me.label3.Location = New System.Drawing.Point(4, 69)
        Me.label3.Margin = New System.Windows.Forms.Padding(1, 0, 1, 0)
        Me.label3.Name = "label3"
        Me.label3.Size = New System.Drawing.Size(84, 13)
        Me.label3.TabIndex = 61
        Me.label3.Text = "Program name:"
        '
        'txtRunProgram
        '
        Me.txtRunProgram.Location = New System.Drawing.Point(87, 66)
        Me.txtRunProgram.Margin = New System.Windows.Forms.Padding(1)
        Me.txtRunProgram.Name = "txtRunProgram"
        Me.txtRunProgram.Size = New System.Drawing.Size(207, 22)
        Me.txtRunProgram.TabIndex = 62
        '
        'btnRun_Program
        '
        Me.btnRun_Program.Location = New System.Drawing.Point(87, 89)
        Me.btnRun_Program.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRun_Program.Name = "btnRun_Program"
        Me.btnRun_Program.Size = New System.Drawing.Size(207, 22)
        Me.btnRun_Program.TabIndex = 63
        Me.btnRun_Program.Text = "3/ Simulate program"
        Me.btnRun_Program.UseVisualStyleBackColor = True
        '
        'numStep
        '
        Me.numStep.DecimalPlaces = 1
        Me.numStep.Increment = New Decimal(New Integer() {5, 0, 0, 0})
        Me.numStep.Location = New System.Drawing.Point(73, 77)
        Me.numStep.Maximum = New Decimal(New Integer() {2000, 0, 0, 0})
        Me.numStep.Name = "numStep"
        Me.numStep.Size = New System.Drawing.Size(70, 22)
        Me.numStep.TabIndex = 48
        '
        'lblstepIncrement
        '
        Me.lblstepIncrement.AutoSize = True
        Me.lblstepIncrement.Location = New System.Drawing.Point(6, 81)
        Me.lblstepIncrement.Name = "lblstepIncrement"
        Me.lblstepIncrement.Size = New System.Drawing.Size(60, 13)
        Me.lblstepIncrement.TabIndex = 47
        Me.lblstepIncrement.Text = "Step (mm):"
        '
        'btnMoveRobotHome
        '
        Me.btnMoveRobotHome.Location = New System.Drawing.Point(182, 117)
        Me.btnMoveRobotHome.Name = "btnMoveRobotHome"
        Me.btnMoveRobotHome.Size = New System.Drawing.Size(112, 22)
        Me.btnMoveRobotHome.TabIndex = 70
        Me.btnMoveRobotHome.Text = "Move Robot Home"
        Me.btnMoveRobotHome.UseVisualStyleBackColor = True
        '
        'rad_Move_Joints
        '
        Me.rad_Move_Joints.AutoSize = True
        Me.rad_Move_Joints.Location = New System.Drawing.Point(11, 57)
        Me.rad_Move_Joints.Name = "rad_Move_Joints"
        Me.rad_Move_Joints.Size = New System.Drawing.Size(81, 17)
        Me.rad_Move_Joints.TabIndex = 2
        Me.rad_Move_Joints.TabStop = True
        Me.rad_Move_Joints.Text = "Joint Move"
        Me.rad_Move_Joints.UseVisualStyleBackColor = True
        '
        'rad_Move_wrt_Tool
        '
        Me.rad_Move_wrt_Tool.AutoSize = True
        Me.rad_Move_wrt_Tool.Location = New System.Drawing.Point(11, 37)
        Me.rad_Move_wrt_Tool.Name = "rad_Move_wrt_Tool"
        Me.rad_Move_wrt_Tool.Size = New System.Drawing.Size(47, 17)
        Me.rad_Move_wrt_Tool.TabIndex = 1
        Me.rad_Move_wrt_Tool.TabStop = True
        Me.rad_Move_wrt_Tool.Text = "Tool"
        Me.rad_Move_wrt_Tool.UseVisualStyleBackColor = True
        '
        'groupIncrementalMove
        '
        Me.groupIncrementalMove.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.groupIncrementalMove.Controls.Add(Me.numStep)
        Me.groupIncrementalMove.Controls.Add(Me.lblstepIncrement)
        Me.groupIncrementalMove.Controls.Add(Me.rad_Move_Joints)
        Me.groupIncrementalMove.Controls.Add(Me.rad_Move_wrt_Tool)
        Me.groupIncrementalMove.Controls.Add(Me.rad_Move_wrt_Reference)
        Me.groupIncrementalMove.Controls.Add(Me.btnTXneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnTXpos)
        Me.groupIncrementalMove.Controls.Add(Me.btnTYneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnTYpos)
        Me.groupIncrementalMove.Controls.Add(Me.btnRZpos)
        Me.groupIncrementalMove.Controls.Add(Me.btnTZneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnRZneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnTZpos)
        Me.groupIncrementalMove.Controls.Add(Me.btnRYpos)
        Me.groupIncrementalMove.Controls.Add(Me.btnRXneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnRYneg)
        Me.groupIncrementalMove.Controls.Add(Me.btnRXpos)
        Me.groupIncrementalMove.Location = New System.Drawing.Point(606, 11)
        Me.groupIncrementalMove.Name = "groupIncrementalMove"
        Me.groupIncrementalMove.Size = New System.Drawing.Size(161, 260)
        Me.groupIncrementalMove.TabIndex = 68
        Me.groupIncrementalMove.TabStop = False
        Me.groupIncrementalMove.Text = "Incremental Move"
        '
        'rad_Move_wrt_Reference
        '
        Me.rad_Move_wrt_Reference.AutoSize = True
        Me.rad_Move_wrt_Reference.Location = New System.Drawing.Point(11, 17)
        Me.rad_Move_wrt_Reference.Name = "rad_Move_wrt_Reference"
        Me.rad_Move_wrt_Reference.Size = New System.Drawing.Size(76, 17)
        Me.rad_Move_wrt_Reference.TabIndex = 0
        Me.rad_Move_wrt_Reference.TabStop = True
        Me.rad_Move_wrt_Reference.Text = "Reference"
        Me.rad_Move_wrt_Reference.UseVisualStyleBackColor = True
        '
        'btnRYpos
        '
        Me.btnRYpos.Location = New System.Drawing.Point(90, 204)
        Me.btnRYpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRYpos.Name = "btnRYpos"
        Me.btnRYpos.Size = New System.Drawing.Size(60, 25)
        Me.btnRYpos.TabIndex = 36
        Me.btnRYpos.Text = "rY+"
        Me.btnRYpos.UseVisualStyleBackColor = True
        '
        'btnRXneg
        '
        Me.btnRXneg.Location = New System.Drawing.Point(10, 179)
        Me.btnRXneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRXneg.Name = "btnRXneg"
        Me.btnRXneg.Size = New System.Drawing.Size(60, 25)
        Me.btnRXneg.TabIndex = 33
        Me.btnRXneg.Text = "rX-"
        Me.btnRXneg.UseVisualStyleBackColor = True
        '
        'btnRYneg
        '
        Me.btnRYneg.Location = New System.Drawing.Point(10, 204)
        Me.btnRYneg.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRYneg.Name = "btnRYneg"
        Me.btnRYneg.Size = New System.Drawing.Size(60, 25)
        Me.btnRYneg.TabIndex = 35
        Me.btnRYneg.Text = "rY-"
        Me.btnRYneg.UseVisualStyleBackColor = True
        '
        'btnRXpos
        '
        Me.btnRXpos.Location = New System.Drawing.Point(90, 179)
        Me.btnRXpos.Margin = New System.Windows.Forms.Padding(1)
        Me.btnRXpos.Name = "btnRXpos"
        Me.btnRXpos.Size = New System.Drawing.Size(60, 25)
        Me.btnRXpos.TabIndex = 34
        Me.btnRXpos.Text = "rX+"
        Me.btnRXpos.UseVisualStyleBackColor = True
        '
        'statusStrip1
        '
        Me.statusStrip1.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.notifybar})
        Me.statusStrip1.Location = New System.Drawing.Point(0, 338)
        Me.statusStrip1.Name = "statusStrip1"
        Me.statusStrip1.Size = New System.Drawing.Size(779, 22)
        Me.statusStrip1.TabIndex = 66
        Me.statusStrip1.Text = "statusStrip1"
        '
        'btnSelectStation
        '
        Me.btnSelectStation.Location = New System.Drawing.Point(10, 11)
        Me.btnSelectStation.Margin = New System.Windows.Forms.Padding(1)
        Me.btnSelectStation.Name = "btnSelectStation"
        Me.btnSelectStation.Size = New System.Drawing.Size(141, 22)
        Me.btnSelectStation.TabIndex = 64
        Me.btnSelectStation.Text = "1/ Select Station"
        Me.btnSelectStation.UseVisualStyleBackColor = True
        '
        'btnLoadAPT
        '
        Me.btnLoadAPT.Enabled = False
        Me.btnLoadAPT.Location = New System.Drawing.Point(3, 41)
        Me.btnLoadAPT.Margin = New System.Windows.Forms.Padding(1)
        Me.btnLoadAPT.Name = "btnLoadAPT"
        Me.btnLoadAPT.Size = New System.Drawing.Size(141, 22)
        Me.btnLoadAPT.TabIndex = 60
        Me.btnLoadAPT.Text = "2/ Load APT"
        Me.btnLoadAPT.UseVisualStyleBackColor = True
        '
        'btnMoveJoints
        '
        Me.btnMoveJoints.Location = New System.Drawing.Point(182, 16)
        Me.btnMoveJoints.Margin = New System.Windows.Forms.Padding(1)
        Me.btnMoveJoints.Name = "btnMoveJoints"
        Me.btnMoveJoints.Size = New System.Drawing.Size(112, 21)
        Me.btnMoveJoints.TabIndex = 59
        Me.btnMoveJoints.Text = "Move to Joints"
        Me.btnMoveJoints.UseVisualStyleBackColor = True
        '
        'txtJoints
        '
        Me.txtJoints.Location = New System.Drawing.Point(87, 39)
        Me.txtJoints.Margin = New System.Windows.Forms.Padding(1)
        Me.txtJoints.Name = "txtJoints"
        Me.txtJoints.Size = New System.Drawing.Size(207, 22)
        Me.txtJoints.TabIndex = 58
        Me.txtJoints.Text = "90 , -90 , 90 , 90 , 90 , -90"
        '
        'btnMovePose
        '
        Me.btnMovePose.Location = New System.Drawing.Point(182, 68)
        Me.btnMovePose.Margin = New System.Windows.Forms.Padding(1)
        Me.btnMovePose.Name = "btnMovePose"
        Me.btnMovePose.Size = New System.Drawing.Size(112, 21)
        Me.btnMovePose.TabIndex = 56
        Me.btnMovePose.Text = "Move to Position"
        Me.btnMovePose.UseVisualStyleBackColor = True
        '
        'label1
        '
        Me.label1.AutoSize = True
        Me.label1.Location = New System.Drawing.Point(84, 21)
        Me.label1.Margin = New System.Windows.Forms.Padding(1, 0, 1, 0)
        Me.label1.Name = "label1"
        Me.label1.Size = New System.Drawing.Size(69, 13)
        Me.label1.TabIndex = 57
        Me.label1.Text = "Joint Values"
        '
        'btnGetJoints
        '
        Me.btnGetJoints.Location = New System.Drawing.Point(7, 18)
        Me.btnGetJoints.Margin = New System.Windows.Forms.Padding(1)
        Me.btnGetJoints.Name = "btnGetJoints"
        Me.btnGetJoints.Size = New System.Drawing.Size(75, 93)
        Me.btnGetJoints.TabIndex = 55
        Me.btnGetJoints.Text = "Retrieve Current Position"
        Me.btnGetJoints.UseVisualStyleBackColor = True
        '
        'txtPosition
        '
        Me.txtPosition.Location = New System.Drawing.Point(87, 91)
        Me.txtPosition.Margin = New System.Windows.Forms.Padding(1)
        Me.txtPosition.Name = "txtPosition"
        Me.txtPosition.Size = New System.Drawing.Size(207, 22)
        Me.txtPosition.TabIndex = 54
        Me.txtPosition.Text = "0 , -90 , 90 , 0 , 90 , 90"
        '
        'panel_rdk
        '
        Me.panel_rdk.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.panel_rdk.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
        Me.panel_rdk.Location = New System.Drawing.Point(0, 277)
        Me.panel_rdk.Name = "panel_rdk"
        Me.panel_rdk.Size = New System.Drawing.Size(779, 57)
        Me.panel_rdk.TabIndex = 71
        '
        'groupAbsoluteMove
        '
        Me.groupAbsoluteMove.Controls.Add(Me.btnMovePose)
        Me.groupAbsoluteMove.Controls.Add(Me.lblJ1)
        Me.groupAbsoluteMove.Controls.Add(Me.btnMoveJoints)
        Me.groupAbsoluteMove.Controls.Add(Me.txtJoints)
        Me.groupAbsoluteMove.Controls.Add(Me.btnMoveRobotHome)
        Me.groupAbsoluteMove.Controls.Add(Me.label1)
        Me.groupAbsoluteMove.Controls.Add(Me.btnGetJoints)
        Me.groupAbsoluteMove.Controls.Add(Me.txtPosition)
        Me.groupAbsoluteMove.Location = New System.Drawing.Point(191, 132)
        Me.groupAbsoluteMove.Name = "groupAbsoluteMove"
        Me.groupAbsoluteMove.Size = New System.Drawing.Size(302, 144)
        Me.groupAbsoluteMove.TabIndex = 72
        Me.groupAbsoluteMove.TabStop = False
        Me.groupAbsoluteMove.Text = "Absolute Move"
        '
        'ComboBoxMillingSetups
        '
        Me.ComboBoxMillingSetups.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.ComboBoxMillingSetups.FormattingEnabled = True
        Me.ComboBoxMillingSetups.Location = New System.Drawing.Point(3, 16)
        Me.ComboBoxMillingSetups.Name = "ComboBoxMillingSetups"
        Me.ComboBoxMillingSetups.Size = New System.Drawing.Size(141, 21)
        Me.ComboBoxMillingSetups.TabIndex = 73
        '
        'GroupBoxMachining
        '
        Me.GroupBoxMachining.Controls.Add(Me.ComboBoxMillingSetups)
        Me.GroupBoxMachining.Controls.Add(Me.btnLoadAPT)
        Me.GroupBoxMachining.Location = New System.Drawing.Point(7, 68)
        Me.GroupBoxMachining.Name = "GroupBoxMachining"
        Me.GroupBoxMachining.Size = New System.Drawing.Size(152, 72)
        Me.GroupBoxMachining.TabIndex = 74
        Me.GroupBoxMachining.TabStop = False
        Me.GroupBoxMachining.Text = "Machining Setups"
        '
        'FormRoboDK_API
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
        Me.ClientSize = New System.Drawing.Size(779, 360)
        Me.Controls.Add(Me.GroupBoxMachining)
        Me.Controls.Add(Me.groupAbsoluteMove)
        Me.Controls.Add(Me.groupRoboDKwindow)
        Me.Controls.Add(Me.groupRunMode)
        Me.Controls.Add(Me.groupIncrementalMove)
        Me.Controls.Add(Me.statusStrip1)
        Me.Controls.Add(Me.btnSelectStation)
        Me.Controls.Add(Me.panel_rdk)
        Me.Font = New System.Drawing.Font("Segoe UI", 8.25!)
        Me.MinimumSize = New System.Drawing.Size(694, 370)
        Me.Name = "FormRoboDK_API"
        Me.Text = "Robot Panel HMI"
        Me.groupRoboDKwindow.ResumeLayout(False)
        Me.groupRoboDKwindow.PerformLayout()
        Me.groupRunMode.ResumeLayout(False)
        Me.groupRunMode.PerformLayout()
        CType(Me.numStep, System.ComponentModel.ISupportInitialize).EndInit()
        Me.groupIncrementalMove.ResumeLayout(False)
        Me.groupIncrementalMove.PerformLayout()
        Me.statusStrip1.ResumeLayout(False)
        Me.statusStrip1.PerformLayout()
        Me.groupAbsoluteMove.ResumeLayout(False)
        Me.groupAbsoluteMove.PerformLayout()
        Me.GroupBoxMachining.ResumeLayout(False)
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Private WithEvents btnTXpos As System.Windows.Forms.Button
    Private WithEvents lblJ1 As System.Windows.Forms.Label
    Private WithEvents btnTYneg As System.Windows.Forms.Button
    Private WithEvents btnTYpos As System.Windows.Forms.Button
    Private WithEvents rad_RoboDK_Integrated As System.Windows.Forms.RadioButton
    Private WithEvents btnTZneg As System.Windows.Forms.Button
    Private WithEvents btnTZpos As System.Windows.Forms.Button
    Private WithEvents rad_RoboDK_hide As System.Windows.Forms.RadioButton
    Private WithEvents btnRZpos As System.Windows.Forms.Button
    Private WithEvents btnRZneg As System.Windows.Forms.Button
    Private WithEvents notifybar As System.Windows.Forms.ToolStripStatusLabel
    Private WithEvents groupRoboDKwindow As System.Windows.Forms.GroupBox
    Private WithEvents rad_RoboDK_show As System.Windows.Forms.RadioButton
    Private WithEvents btnTXneg As System.Windows.Forms.Button
    Private WithEvents groupRunMode As System.Windows.Forms.GroupBox
    Private WithEvents rad_RunMode_Simulation As System.Windows.Forms.RadioButton
    Private WithEvents rad_RunMode_Online As System.Windows.Forms.RadioButton
    Private WithEvents rad_RunMode_Program As System.Windows.Forms.RadioButton
    Private WithEvents numStep As System.Windows.Forms.NumericUpDown
    Private WithEvents lblstepIncrement As System.Windows.Forms.Label
    Private WithEvents btnMoveRobotHome As System.Windows.Forms.Button
    Private WithEvents rad_Move_Joints As System.Windows.Forms.RadioButton
    Private WithEvents rad_Move_wrt_Tool As System.Windows.Forms.RadioButton
    Private WithEvents groupIncrementalMove As System.Windows.Forms.GroupBox
    Private WithEvents rad_Move_wrt_Reference As System.Windows.Forms.RadioButton
    Private WithEvents btnRYpos As System.Windows.Forms.Button
    Private WithEvents btnRXneg As System.Windows.Forms.Button
    Private WithEvents btnRYneg As System.Windows.Forms.Button
    Private WithEvents btnRXpos As System.Windows.Forms.Button
    Private WithEvents statusStrip1 As System.Windows.Forms.StatusStrip
    Private WithEvents btnSelectStation As System.Windows.Forms.Button
    Private WithEvents btnRun_Program As System.Windows.Forms.Button
    Private WithEvents txtRunProgram As System.Windows.Forms.TextBox
    Private WithEvents label3 As System.Windows.Forms.Label
    Private WithEvents btnLoadAPT As System.Windows.Forms.Button
    Private WithEvents btnMoveJoints As System.Windows.Forms.Button
    Private WithEvents txtJoints As System.Windows.Forms.TextBox
    Private WithEvents btnMovePose As System.Windows.Forms.Button
    Private WithEvents label1 As System.Windows.Forms.Label
    Private WithEvents btnGetJoints As System.Windows.Forms.Button
    Private WithEvents txtPosition As System.Windows.Forms.TextBox
    Private WithEvents panel_rdk As System.Windows.Forms.Panel
    Friend WithEvents groupAbsoluteMove As System.Windows.Forms.GroupBox
    Friend WithEvents ComboBoxMillingSetups As System.Windows.Forms.ComboBox
    Friend WithEvents GroupBoxMachining As System.Windows.Forms.GroupBox
    Private WithEvents btnStop_Simulation As System.Windows.Forms.Button
End Class
