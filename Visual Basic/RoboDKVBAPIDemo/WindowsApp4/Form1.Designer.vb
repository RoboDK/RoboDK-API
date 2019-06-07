<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
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
		Me.btnLoadFile = New System.Windows.Forms.Button()
		Me.btnSelectRobot = New System.Windows.Forms.Button()
		Me.btnMoveRobotHome = New System.Windows.Forms.Button()
		Me.btnRunTestProgram = New System.Windows.Forms.Button()
		Me.Label1 = New System.Windows.Forms.Label()
		Me.notifybar = New System.Windows.Forms.Label()
		Me.RoboDkPanel = New System.Windows.Forms.Panel()
		Me.SuspendLayout()
		'
		'btnLoadFile
		'
		Me.btnLoadFile.Location = New System.Drawing.Point(10, 18)
		Me.btnLoadFile.Name = "btnLoadFile"
		Me.btnLoadFile.Size = New System.Drawing.Size(148, 56)
		Me.btnLoadFile.TabIndex = 0
		Me.btnLoadFile.Text = "Load File"
		Me.btnLoadFile.UseVisualStyleBackColor = True
		'
		'btnSelectRobot
		'
		Me.btnSelectRobot.Location = New System.Drawing.Point(10, 87)
		Me.btnSelectRobot.Name = "btnSelectRobot"
		Me.btnSelectRobot.Size = New System.Drawing.Size(147, 62)
		Me.btnSelectRobot.TabIndex = 1
		Me.btnSelectRobot.Text = "Select Robot"
		Me.btnSelectRobot.UseVisualStyleBackColor = True
		'
		'btnMoveRobotHome
		'
		Me.btnMoveRobotHome.Location = New System.Drawing.Point(10, 160)
		Me.btnMoveRobotHome.Name = "btnMoveRobotHome"
		Me.btnMoveRobotHome.Size = New System.Drawing.Size(146, 67)
		Me.btnMoveRobotHome.TabIndex = 2
		Me.btnMoveRobotHome.Text = "Move Robot Home"
		Me.btnMoveRobotHome.UseVisualStyleBackColor = True
		'
		'btnRunTestProgram
		'
		Me.btnRunTestProgram.Location = New System.Drawing.Point(10, 239)
		Me.btnRunTestProgram.Name = "btnRunTestProgram"
		Me.btnRunTestProgram.Size = New System.Drawing.Size(145, 75)
		Me.btnRunTestProgram.TabIndex = 3
		Me.btnRunTestProgram.Text = "Dummy"
		Me.btnRunTestProgram.UseVisualStyleBackColor = True
		'
		'Label1
		'
		Me.Label1.AutoSize = True
		Me.Label1.Location = New System.Drawing.Point(0, 0)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(39, 13)
		Me.Label1.TabIndex = 4
		Me.Label1.Text = "Label1"
		'
		'notifybar
		'
		Me.notifybar.AutoSize = True
		Me.notifybar.Location = New System.Drawing.Point(14, 376)
		Me.notifybar.Name = "notifybar"
		Me.notifybar.Size = New System.Drawing.Size(54, 13)
		Me.notifybar.TabIndex = 5
		Me.notifybar.Text = "Loading..."
		'
		'RoboDkPanel
		'
		Me.RoboDkPanel.Location = New System.Drawing.Point(440, 12)
		Me.RoboDkPanel.Name = "RoboDkPanel"
		Me.RoboDkPanel.Size = New System.Drawing.Size(348, 433)
		Me.RoboDkPanel.TabIndex = 6
		'
		'Form1
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(800, 450)
		Me.Controls.Add(Me.RoboDkPanel)
		Me.Controls.Add(Me.notifybar)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.btnRunTestProgram)
		Me.Controls.Add(Me.btnMoveRobotHome)
		Me.Controls.Add(Me.btnSelectRobot)
		Me.Controls.Add(Me.btnLoadFile)
		Me.Name = "Form1"
		Me.Text = "Form1"
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents btnLoadFile As Button
	Friend WithEvents btnSelectRobot As Button
	Friend WithEvents btnMoveRobotHome As Button
	Friend WithEvents btnRunTestProgram As Button
	Friend WithEvents Label1 As Label
	Friend WithEvents notifybar As Label
	Friend WithEvents RoboDkPanel As Panel
End Class
