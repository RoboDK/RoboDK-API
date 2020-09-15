namespace SamplePanelRoboDK
{
    partial class FormRobot
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.lblJ1 = new System.Windows.Forms.Label();
            this.txtPosition = new System.Windows.Forms.TextBox();
            this.btnGetJoints = new System.Windows.Forms.Button();
            this.btnMovePose = new System.Windows.Forms.Button();
            this.btnMoveJoints = new System.Windows.Forms.Button();
            this.txtJoints = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.btnSelectRobot = new System.Windows.Forms.Button();
            this.label3 = new System.Windows.Forms.Label();
            this.txtRunProgram = new System.Windows.Forms.TextBox();
            this.btnRun_Program = new System.Windows.Forms.Button();
            this.btnSelectStation = new System.Windows.Forms.Button();
            this.btnRunTestProgram = new System.Windows.Forms.Button();
            this.btnTXneg = new System.Windows.Forms.Button();
            this.btnTXpos = new System.Windows.Forms.Button();
            this.btnTYpos = new System.Windows.Forms.Button();
            this.btnTYneg = new System.Windows.Forms.Button();
            this.btnTZpos = new System.Windows.Forms.Button();
            this.btnTZneg = new System.Windows.Forms.Button();
            this.btnRXpos = new System.Windows.Forms.Button();
            this.btnRXneg = new System.Windows.Forms.Button();
            this.btnRYpos = new System.Windows.Forms.Button();
            this.btnRYneg = new System.Windows.Forms.Button();
            this.btnRZpos = new System.Windows.Forms.Button();
            this.btnRZneg = new System.Windows.Forms.Button();
            this.btnOLPdone = new System.Windows.Forms.Button();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.notifybar = new System.Windows.Forms.ToolStripStatusLabel();
            this.groupRoboDKwindow = new System.Windows.Forms.GroupBox();
            this.rad_RoboDK_Integrated = new System.Windows.Forms.RadioButton();
            this.rad_RoboDK_hide = new System.Windows.Forms.RadioButton();
            this.rad_RoboDK_show = new System.Windows.Forms.RadioButton();
            this.groupIncrementalMove = new System.Windows.Forms.GroupBox();
            this.numStep = new System.Windows.Forms.NumericUpDown();
            this.lblstepIncrement = new System.Windows.Forms.Label();
            this.rad_Move_Joints = new System.Windows.Forms.RadioButton();
            this.rad_Move_wrt_Tool = new System.Windows.Forms.RadioButton();
            this.rad_Move_wrt_Reference = new System.Windows.Forms.RadioButton();
            this.rad_RunMode_Online = new System.Windows.Forms.RadioButton();
            this.rad_RunMode_Program = new System.Windows.Forms.RadioButton();
            this.rad_RunMode_Simulation = new System.Windows.Forms.RadioButton();
            this.groupRunMode = new System.Windows.Forms.GroupBox();
            this.btnMoveRobotHome = new System.Windows.Forms.Button();
            this.panel_rdk = new System.Windows.Forms.Panel();
            this.statusStrip1.SuspendLayout();
            this.groupRoboDKwindow.SuspendLayout();
            this.groupIncrementalMove.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numStep)).BeginInit();
            this.groupRunMode.SuspendLayout();
            this.SuspendLayout();
            // 
            // lblJ1
            // 
            this.lblJ1.AutoSize = true;
            this.lblJ1.Location = new System.Drawing.Point(274, 182);
            this.lblJ1.Margin = new System.Windows.Forms.Padding(1, 0, 1, 0);
            this.lblJ1.Name = "lblJ1";
            this.lblJ1.Size = new System.Drawing.Size(137, 13);
            this.lblJ1.TabIndex = 1;
            this.lblJ1.Text = "Cartesian Position (mm,deg)";
            // 
            // txtPosition
            // 
            this.txtPosition.Location = new System.Drawing.Point(277, 201);
            this.txtPosition.Margin = new System.Windows.Forms.Padding(1);
            this.txtPosition.Name = "txtPosition";
            this.txtPosition.Size = new System.Drawing.Size(237, 20);
            this.txtPosition.TabIndex = 2;
            this.txtPosition.Text = "0 , -90 , 90 , 0 , 90 , 90";
            // 
            // btnGetJoints
            // 
            this.btnGetJoints.Location = new System.Drawing.Point(197, 128);
            this.btnGetJoints.Margin = new System.Windows.Forms.Padding(1);
            this.btnGetJoints.Name = "btnGetJoints";
            this.btnGetJoints.Size = new System.Drawing.Size(75, 93);
            this.btnGetJoints.TabIndex = 3;
            this.btnGetJoints.Text = "Retrieve Current Position";
            this.btnGetJoints.UseVisualStyleBackColor = true;
            this.btnGetJoints.Click += new System.EventHandler(this.btnGetJoints_Click);
            // 
            // btnMovePose
            // 
            this.btnMovePose.Location = new System.Drawing.Point(413, 178);
            this.btnMovePose.Margin = new System.Windows.Forms.Padding(1);
            this.btnMovePose.Name = "btnMovePose";
            this.btnMovePose.Size = new System.Drawing.Size(101, 21);
            this.btnMovePose.TabIndex = 7;
            this.btnMovePose.Text = "Move to Position";
            this.btnMovePose.UseVisualStyleBackColor = true;
            this.btnMovePose.Click += new System.EventHandler(this.btnMovePose_Click);
            // 
            // btnMoveJoints
            // 
            this.btnMoveJoints.Location = new System.Drawing.Point(413, 126);
            this.btnMoveJoints.Margin = new System.Windows.Forms.Padding(1);
            this.btnMoveJoints.Name = "btnMoveJoints";
            this.btnMoveJoints.Size = new System.Drawing.Size(101, 21);
            this.btnMoveJoints.TabIndex = 12;
            this.btnMoveJoints.Text = "Move to Joints";
            this.btnMoveJoints.UseVisualStyleBackColor = true;
            this.btnMoveJoints.Click += new System.EventHandler(this.btnMoveJoints_Click);
            // 
            // txtJoints
            // 
            this.txtJoints.Location = new System.Drawing.Point(277, 149);
            this.txtJoints.Margin = new System.Windows.Forms.Padding(1);
            this.txtJoints.Name = "txtJoints";
            this.txtJoints.Size = new System.Drawing.Size(237, 20);
            this.txtJoints.TabIndex = 10;
            this.txtJoints.Text = "90 , -90 , 90 , 90 , 90 , -90";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(274, 131);
            this.label1.Margin = new System.Windows.Forms.Padding(1, 0, 1, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(91, 13);
            this.label1.TabIndex = 9;
            this.label1.Text = "Joint Values (deg)";
            // 
            // btnSelectRobot
            // 
            this.btnSelectRobot.Location = new System.Drawing.Point(10, 36);
            this.btnSelectRobot.Margin = new System.Windows.Forms.Padding(1);
            this.btnSelectRobot.Name = "btnSelectRobot";
            this.btnSelectRobot.Size = new System.Drawing.Size(141, 22);
            this.btnSelectRobot.TabIndex = 14;
            this.btnSelectRobot.Text = "Select Robot";
            this.btnSelectRobot.UseVisualStyleBackColor = true;
            this.btnSelectRobot.Click += new System.EventHandler(this.btnSelectRobot_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(199, 243);
            this.label3.Margin = new System.Windows.Forms.Padding(1, 0, 1, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(78, 13);
            this.label3.TabIndex = 18;
            this.label3.Text = "Program name:";
            // 
            // txtRunProgram
            // 
            this.txtRunProgram.Location = new System.Drawing.Point(279, 239);
            this.txtRunProgram.Margin = new System.Windows.Forms.Padding(1);
            this.txtRunProgram.Name = "txtRunProgram";
            this.txtRunProgram.Size = new System.Drawing.Size(100, 20);
            this.txtRunProgram.TabIndex = 20;
            this.txtRunProgram.Text = "MainProgram";
            // 
            // btnRun_Program
            // 
            this.btnRun_Program.Location = new System.Drawing.Point(381, 238);
            this.btnRun_Program.Margin = new System.Windows.Forms.Padding(1);
            this.btnRun_Program.Name = "btnRun_Program";
            this.btnRun_Program.Size = new System.Drawing.Size(87, 22);
            this.btnRun_Program.TabIndex = 23;
            this.btnRun_Program.Text = "Run Program";
            this.btnRun_Program.UseVisualStyleBackColor = true;
            this.btnRun_Program.Click += new System.EventHandler(this.btnRun_Program_Click);
            // 
            // btnSelectStation
            // 
            this.btnSelectStation.Location = new System.Drawing.Point(10, 11);
            this.btnSelectStation.Margin = new System.Windows.Forms.Padding(1);
            this.btnSelectStation.Name = "btnSelectStation";
            this.btnSelectStation.Size = new System.Drawing.Size(141, 22);
            this.btnSelectStation.TabIndex = 25;
            this.btnSelectStation.Text = "Load File";
            this.btnSelectStation.UseVisualStyleBackColor = true;
            this.btnSelectStation.Click += new System.EventHandler(this.btnLoadFile_Click);
            // 
            // btnRunTestProgram
            // 
            this.btnRunTestProgram.Location = new System.Drawing.Point(10, 86);
            this.btnRunTestProgram.Name = "btnRunTestProgram";
            this.btnRunTestProgram.Size = new System.Drawing.Size(141, 22);
            this.btnRunTestProgram.TabIndex = 26;
            this.btnRunTestProgram.Text = "Run Test Program";
            this.btnRunTestProgram.UseVisualStyleBackColor = true;
            this.btnRunTestProgram.Click += new System.EventHandler(this.btnRunTestProgram_Click);
            // 
            // btnTXneg
            // 
            this.btnTXneg.Location = new System.Drawing.Point(10, 104);
            this.btnTXneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnTXneg.Name = "btnTXneg";
            this.btnTXneg.Size = new System.Drawing.Size(60, 25);
            this.btnTXneg.TabIndex = 27;
            this.btnTXneg.Text = "X-";
            this.btnTXneg.UseVisualStyleBackColor = true;
            this.btnTXneg.Click += new System.EventHandler(this.btnTXneg_Click);
            // 
            // btnTXpos
            // 
            this.btnTXpos.Location = new System.Drawing.Point(90, 104);
            this.btnTXpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnTXpos.Name = "btnTXpos";
            this.btnTXpos.Size = new System.Drawing.Size(60, 25);
            this.btnTXpos.TabIndex = 28;
            this.btnTXpos.Text = "X+";
            this.btnTXpos.UseVisualStyleBackColor = true;
            this.btnTXpos.Click += new System.EventHandler(this.btnTXpos_Click);
            // 
            // btnTYpos
            // 
            this.btnTYpos.Location = new System.Drawing.Point(90, 129);
            this.btnTYpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnTYpos.Name = "btnTYpos";
            this.btnTYpos.Size = new System.Drawing.Size(60, 25);
            this.btnTYpos.TabIndex = 30;
            this.btnTYpos.Text = "Y+";
            this.btnTYpos.UseVisualStyleBackColor = true;
            this.btnTYpos.Click += new System.EventHandler(this.btnTYpos_Click);
            // 
            // btnTYneg
            // 
            this.btnTYneg.Location = new System.Drawing.Point(10, 129);
            this.btnTYneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnTYneg.Name = "btnTYneg";
            this.btnTYneg.Size = new System.Drawing.Size(60, 25);
            this.btnTYneg.TabIndex = 29;
            this.btnTYneg.Text = "Y-";
            this.btnTYneg.UseVisualStyleBackColor = true;
            this.btnTYneg.Click += new System.EventHandler(this.btnTYneg_Click);
            // 
            // btnTZpos
            // 
            this.btnTZpos.Location = new System.Drawing.Point(90, 154);
            this.btnTZpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnTZpos.Name = "btnTZpos";
            this.btnTZpos.Size = new System.Drawing.Size(60, 25);
            this.btnTZpos.TabIndex = 32;
            this.btnTZpos.Text = "Z+";
            this.btnTZpos.UseVisualStyleBackColor = true;
            this.btnTZpos.Click += new System.EventHandler(this.btnTZpos_Click);
            // 
            // btnTZneg
            // 
            this.btnTZneg.Location = new System.Drawing.Point(10, 154);
            this.btnTZneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnTZneg.Name = "btnTZneg";
            this.btnTZneg.Size = new System.Drawing.Size(60, 25);
            this.btnTZneg.TabIndex = 31;
            this.btnTZneg.Text = "Z-";
            this.btnTZneg.UseVisualStyleBackColor = true;
            this.btnTZneg.Click += new System.EventHandler(this.btnTZneg_Click);
            // 
            // btnRXpos
            // 
            this.btnRXpos.Location = new System.Drawing.Point(90, 179);
            this.btnRXpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnRXpos.Name = "btnRXpos";
            this.btnRXpos.Size = new System.Drawing.Size(60, 25);
            this.btnRXpos.TabIndex = 34;
            this.btnRXpos.Text = "rX+";
            this.btnRXpos.UseVisualStyleBackColor = true;
            this.btnRXpos.Click += new System.EventHandler(this.btnRXpos_Click);
            // 
            // btnRXneg
            // 
            this.btnRXneg.Location = new System.Drawing.Point(10, 179);
            this.btnRXneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnRXneg.Name = "btnRXneg";
            this.btnRXneg.Size = new System.Drawing.Size(60, 25);
            this.btnRXneg.TabIndex = 33;
            this.btnRXneg.Text = "rX-";
            this.btnRXneg.UseVisualStyleBackColor = true;
            this.btnRXneg.Click += new System.EventHandler(this.btnRXneg_Click);
            // 
            // btnRYpos
            // 
            this.btnRYpos.Location = new System.Drawing.Point(90, 204);
            this.btnRYpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnRYpos.Name = "btnRYpos";
            this.btnRYpos.Size = new System.Drawing.Size(60, 25);
            this.btnRYpos.TabIndex = 36;
            this.btnRYpos.Text = "rY+";
            this.btnRYpos.UseVisualStyleBackColor = true;
            this.btnRYpos.Click += new System.EventHandler(this.btnRYpos_Click);
            // 
            // btnRYneg
            // 
            this.btnRYneg.Location = new System.Drawing.Point(10, 204);
            this.btnRYneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnRYneg.Name = "btnRYneg";
            this.btnRYneg.Size = new System.Drawing.Size(60, 25);
            this.btnRYneg.TabIndex = 35;
            this.btnRYneg.Text = "rY-";
            this.btnRYneg.UseVisualStyleBackColor = true;
            this.btnRYneg.Click += new System.EventHandler(this.btnRYneg_Click);
            // 
            // btnRZpos
            // 
            this.btnRZpos.Location = new System.Drawing.Point(90, 229);
            this.btnRZpos.Margin = new System.Windows.Forms.Padding(1);
            this.btnRZpos.Name = "btnRZpos";
            this.btnRZpos.Size = new System.Drawing.Size(60, 25);
            this.btnRZpos.TabIndex = 38;
            this.btnRZpos.Text = "rZ+";
            this.btnRZpos.UseVisualStyleBackColor = true;
            this.btnRZpos.Click += new System.EventHandler(this.btnRZpos_Click);
            // 
            // btnRZneg
            // 
            this.btnRZneg.Location = new System.Drawing.Point(10, 229);
            this.btnRZneg.Margin = new System.Windows.Forms.Padding(1);
            this.btnRZneg.Name = "btnRZneg";
            this.btnRZneg.Size = new System.Drawing.Size(60, 25);
            this.btnRZneg.TabIndex = 37;
            this.btnRZneg.Text = "rZ-";
            this.btnRZneg.UseVisualStyleBackColor = true;
            this.btnRZneg.Click += new System.EventHandler(this.btnRZneg_Click);
            // 
            // btnOLPdone
            // 
            this.btnOLPdone.Location = new System.Drawing.Point(123, 43);
            this.btnOLPdone.Name = "btnOLPdone";
            this.btnOLPdone.Size = new System.Drawing.Size(89, 23);
            this.btnOLPdone.TabIndex = 0;
            this.btnOLPdone.Text = "Generate Prog";
            this.btnOLPdone.Click += new System.EventHandler(this.btnOLPdone_Click);
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.notifybar});
            this.statusStrip1.Location = new System.Drawing.Point(0, 309);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(699, 22);
            this.statusStrip1.TabIndex = 44;
            this.statusStrip1.Text = "statusStrip1";
            // 
            // notifybar
            // 
            this.notifybar.Name = "notifybar";
            this.notifybar.Size = new System.Drawing.Size(95, 17);
            this.notifybar.Text = "Notification area";
            // 
            // groupRoboDKwindow
            // 
            this.groupRoboDKwindow.Controls.Add(this.rad_RoboDK_Integrated);
            this.groupRoboDKwindow.Controls.Add(this.rad_RoboDK_hide);
            this.groupRoboDKwindow.Controls.Add(this.rad_RoboDK_show);
            this.groupRoboDKwindow.Location = new System.Drawing.Point(10, 144);
            this.groupRoboDKwindow.Name = "groupRoboDKwindow";
            this.groupRoboDKwindow.Size = new System.Drawing.Size(166, 98);
            this.groupRoboDKwindow.TabIndex = 45;
            this.groupRoboDKwindow.TabStop = false;
            this.groupRoboDKwindow.Text = "Display Mode";
            // 
            // rad_RoboDK_Integrated
            // 
            this.rad_RoboDK_Integrated.AutoSize = true;
            this.rad_RoboDK_Integrated.Location = new System.Drawing.Point(10, 73);
            this.rad_RoboDK_Integrated.Name = "rad_RoboDK_Integrated";
            this.rad_RoboDK_Integrated.Size = new System.Drawing.Size(153, 17);
            this.rad_RoboDK_Integrated.TabIndex = 2;
            this.rad_RoboDK_Integrated.TabStop = true;
            this.rad_RoboDK_Integrated.Text = "Integrate RoboDK Window";
            this.rad_RoboDK_Integrated.UseVisualStyleBackColor = true;
            this.rad_RoboDK_Integrated.CheckedChanged += new System.EventHandler(this.rad_RoboDK_Integrated_CheckedChanged);
            // 
            // rad_RoboDK_hide
            // 
            this.rad_RoboDK_hide.AutoSize = true;
            this.rad_RoboDK_hide.Location = new System.Drawing.Point(10, 47);
            this.rad_RoboDK_hide.Name = "rad_RoboDK_hide";
            this.rad_RoboDK_hide.Size = new System.Drawing.Size(91, 17);
            this.rad_RoboDK_hide.TabIndex = 1;
            this.rad_RoboDK_hide.TabStop = true;
            this.rad_RoboDK_hide.Text = "Hide RoboDK";
            this.rad_RoboDK_hide.UseVisualStyleBackColor = true;
            this.rad_RoboDK_hide.CheckedChanged += new System.EventHandler(this.rad_RoboDK_hide_CheckedChanged);
            // 
            // rad_RoboDK_show
            // 
            this.rad_RoboDK_show.AutoSize = true;
            this.rad_RoboDK_show.Location = new System.Drawing.Point(10, 21);
            this.rad_RoboDK_show.Name = "rad_RoboDK_show";
            this.rad_RoboDK_show.Size = new System.Drawing.Size(96, 17);
            this.rad_RoboDK_show.TabIndex = 0;
            this.rad_RoboDK_show.TabStop = true;
            this.rad_RoboDK_show.Text = "Show RoboDK";
            this.rad_RoboDK_show.UseVisualStyleBackColor = true;
            this.rad_RoboDK_show.CheckedChanged += new System.EventHandler(this.rad_RoboDK_show_CheckedChanged);
            // 
            // groupIncrementalMove
            // 
            this.groupIncrementalMove.Controls.Add(this.numStep);
            this.groupIncrementalMove.Controls.Add(this.lblstepIncrement);
            this.groupIncrementalMove.Controls.Add(this.rad_Move_Joints);
            this.groupIncrementalMove.Controls.Add(this.rad_Move_wrt_Tool);
            this.groupIncrementalMove.Controls.Add(this.rad_Move_wrt_Reference);
            this.groupIncrementalMove.Controls.Add(this.btnTXneg);
            this.groupIncrementalMove.Controls.Add(this.btnTXpos);
            this.groupIncrementalMove.Controls.Add(this.btnTYneg);
            this.groupIncrementalMove.Controls.Add(this.btnTYpos);
            this.groupIncrementalMove.Controls.Add(this.btnRZpos);
            this.groupIncrementalMove.Controls.Add(this.btnTZneg);
            this.groupIncrementalMove.Controls.Add(this.btnRZneg);
            this.groupIncrementalMove.Controls.Add(this.btnTZpos);
            this.groupIncrementalMove.Controls.Add(this.btnRYpos);
            this.groupIncrementalMove.Controls.Add(this.btnRXneg);
            this.groupIncrementalMove.Controls.Add(this.btnRYneg);
            this.groupIncrementalMove.Controls.Add(this.btnRXpos);
            this.groupIncrementalMove.Location = new System.Drawing.Point(529, 8);
            this.groupIncrementalMove.Name = "groupIncrementalMove";
            this.groupIncrementalMove.Size = new System.Drawing.Size(161, 260);
            this.groupIncrementalMove.TabIndex = 46;
            this.groupIncrementalMove.TabStop = false;
            this.groupIncrementalMove.Text = "Incremental Move";
            // 
            // numStep
            // 
            this.numStep.DecimalPlaces = 1;
            this.numStep.Increment = new decimal(new int[] {
            5,
            0,
            0,
            0});
            this.numStep.Location = new System.Drawing.Point(73, 77);
            this.numStep.Maximum = new decimal(new int[] {
            2000,
            0,
            0,
            0});
            this.numStep.Name = "numStep";
            this.numStep.Size = new System.Drawing.Size(70, 20);
            this.numStep.TabIndex = 48;
            // 
            // lblstepIncrement
            // 
            this.lblstepIncrement.AutoSize = true;
            this.lblstepIncrement.Location = new System.Drawing.Point(6, 81);
            this.lblstepIncrement.Name = "lblstepIncrement";
            this.lblstepIncrement.Size = new System.Drawing.Size(57, 13);
            this.lblstepIncrement.TabIndex = 47;
            this.lblstepIncrement.Text = "Step (mm):";
            // 
            // rad_Move_Joints
            // 
            this.rad_Move_Joints.AutoSize = true;
            this.rad_Move_Joints.Location = new System.Drawing.Point(11, 57);
            this.rad_Move_Joints.Name = "rad_Move_Joints";
            this.rad_Move_Joints.Size = new System.Drawing.Size(77, 17);
            this.rad_Move_Joints.TabIndex = 2;
            this.rad_Move_Joints.TabStop = true;
            this.rad_Move_Joints.Text = "Joint Move";
            this.rad_Move_Joints.UseVisualStyleBackColor = true;
            this.rad_Move_Joints.CheckedChanged += new System.EventHandler(this.rad_Move_Joints_CheckedChanged);
            // 
            // rad_Move_wrt_Tool
            // 
            this.rad_Move_wrt_Tool.AutoSize = true;
            this.rad_Move_wrt_Tool.Location = new System.Drawing.Point(11, 37);
            this.rad_Move_wrt_Tool.Name = "rad_Move_wrt_Tool";
            this.rad_Move_wrt_Tool.Size = new System.Drawing.Size(46, 17);
            this.rad_Move_wrt_Tool.TabIndex = 1;
            this.rad_Move_wrt_Tool.TabStop = true;
            this.rad_Move_wrt_Tool.Text = "Tool";
            this.rad_Move_wrt_Tool.UseVisualStyleBackColor = true;
            this.rad_Move_wrt_Tool.CheckedChanged += new System.EventHandler(this.rad_Move_wrt_Tool_CheckedChanged);
            // 
            // rad_Move_wrt_Reference
            // 
            this.rad_Move_wrt_Reference.AutoSize = true;
            this.rad_Move_wrt_Reference.Location = new System.Drawing.Point(11, 17);
            this.rad_Move_wrt_Reference.Name = "rad_Move_wrt_Reference";
            this.rad_Move_wrt_Reference.Size = new System.Drawing.Size(75, 17);
            this.rad_Move_wrt_Reference.TabIndex = 0;
            this.rad_Move_wrt_Reference.TabStop = true;
            this.rad_Move_wrt_Reference.Text = "Reference";
            this.rad_Move_wrt_Reference.UseVisualStyleBackColor = true;
            this.rad_Move_wrt_Reference.CheckedChanged += new System.EventHandler(this.rad_Move_wrt_Reference_CheckedChanged);
            // 
            // rad_RunMode_Online
            // 
            this.rad_RunMode_Online.AutoSize = true;
            this.rad_RunMode_Online.Location = new System.Drawing.Point(7, 73);
            this.rad_RunMode_Online.Name = "rad_RunMode_Online";
            this.rad_RunMode_Online.Size = new System.Drawing.Size(94, 17);
            this.rad_RunMode_Online.TabIndex = 47;
            this.rad_RunMode_Online.TabStop = true;
            this.rad_RunMode_Online.Text = "Run On Robot";
            this.rad_RunMode_Online.UseVisualStyleBackColor = true;
            this.rad_RunMode_Online.CheckedChanged += new System.EventHandler(this.rad_RunMode_Online_CheckedChanged);
            // 
            // rad_RunMode_Program
            // 
            this.rad_RunMode_Program.AutoSize = true;
            this.rad_RunMode_Program.Location = new System.Drawing.Point(7, 47);
            this.rad_RunMode_Program.Name = "rad_RunMode_Program";
            this.rad_RunMode_Program.Size = new System.Drawing.Size(119, 17);
            this.rad_RunMode_Program.TabIndex = 48;
            this.rad_RunMode_Program.TabStop = true;
            this.rad_RunMode_Program.Text = "Offline Programming";
            this.rad_RunMode_Program.UseVisualStyleBackColor = true;
            this.rad_RunMode_Program.CheckedChanged += new System.EventHandler(this.rad_RunMode_Program_CheckedChanged);
            // 
            // rad_RunMode_Simulation
            // 
            this.rad_RunMode_Simulation.AutoSize = true;
            this.rad_RunMode_Simulation.Location = new System.Drawing.Point(7, 21);
            this.rad_RunMode_Simulation.Name = "rad_RunMode_Simulation";
            this.rad_RunMode_Simulation.Size = new System.Drawing.Size(73, 17);
            this.rad_RunMode_Simulation.TabIndex = 49;
            this.rad_RunMode_Simulation.TabStop = true;
            this.rad_RunMode_Simulation.Text = "Simulation";
            this.rad_RunMode_Simulation.UseVisualStyleBackColor = true;
            this.rad_RunMode_Simulation.CheckedChanged += new System.EventHandler(this.rad_RunMode_Simulation_CheckedChanged);
            // 
            // groupRunMode
            // 
            this.groupRunMode.Controls.Add(this.btnOLPdone);
            this.groupRunMode.Controls.Add(this.rad_RunMode_Simulation);
            this.groupRunMode.Controls.Add(this.rad_RunMode_Online);
            this.groupRunMode.Controls.Add(this.rad_RunMode_Program);
            this.groupRunMode.Location = new System.Drawing.Point(222, 8);
            this.groupRunMode.Name = "groupRunMode";
            this.groupRunMode.Size = new System.Drawing.Size(216, 100);
            this.groupRunMode.TabIndex = 50;
            this.groupRunMode.TabStop = false;
            this.groupRunMode.Text = "Run Mode";
            // 
            // btnMoveRobotHome
            // 
            this.btnMoveRobotHome.Location = new System.Drawing.Point(10, 61);
            this.btnMoveRobotHome.Name = "btnMoveRobotHome";
            this.btnMoveRobotHome.Size = new System.Drawing.Size(141, 22);
            this.btnMoveRobotHome.TabIndex = 51;
            this.btnMoveRobotHome.Text = "Move Robot Home";
            this.btnMoveRobotHome.UseVisualStyleBackColor = true;
            this.btnMoveRobotHome.Click += new System.EventHandler(this.btnMoveRobotHome_Click);
            // 
            // panel_rdk
            // 
            this.panel_rdk.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.panel_rdk.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.panel_rdk.Location = new System.Drawing.Point(0, 274);
            this.panel_rdk.Name = "panel_rdk";
            this.panel_rdk.Size = new System.Drawing.Size(699, 32);
            this.panel_rdk.TabIndex = 52;
            this.panel_rdk.Resize += new System.EventHandler(this.panel_Resized);
            // 
            // FormRobot
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.ClientSize = new System.Drawing.Size(699, 331);
            this.Controls.Add(this.btnMoveRobotHome);
            this.Controls.Add(this.groupRunMode);
            this.Controls.Add(this.groupIncrementalMove);
            this.Controls.Add(this.groupRoboDKwindow);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.btnRunTestProgram);
            this.Controls.Add(this.btnSelectStation);
            this.Controls.Add(this.btnRun_Program);
            this.Controls.Add(this.txtRunProgram);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.btnSelectRobot);
            this.Controls.Add(this.btnMoveJoints);
            this.Controls.Add(this.txtJoints);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.btnMovePose);
            this.Controls.Add(this.btnGetJoints);
            this.Controls.Add(this.txtPosition);
            this.Controls.Add(this.lblJ1);
            this.Controls.Add(this.panel_rdk);
            this.MinimumSize = new System.Drawing.Size(715, 370);
            this.Name = "FormRobot";
            this.Text = "Robot Panel HMI";
            this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.FormRobot_FormClosed);
            this.Load += new System.EventHandler(this.FormRobot_Load);
            this.Shown += new System.EventHandler(this.FormRobot_Shown);
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.groupRoboDKwindow.ResumeLayout(false);
            this.groupRoboDKwindow.PerformLayout();
            this.groupIncrementalMove.ResumeLayout(false);
            this.groupIncrementalMove.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numStep)).EndInit();
            this.groupRunMode.ResumeLayout(false);
            this.groupRunMode.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Label lblJ1;
        private System.Windows.Forms.TextBox txtPosition;
        private System.Windows.Forms.Button btnGetJoints;
        private System.Windows.Forms.Button btnMovePose;
        private System.Windows.Forms.Button btnMoveJoints;
        private System.Windows.Forms.TextBox txtJoints;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Button btnSelectRobot;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox txtRunProgram;
        private System.Windows.Forms.Button btnRun_Program;
        private System.Windows.Forms.Button btnSelectStation;
        private System.Windows.Forms.Button btnRunTestProgram;
        private System.Windows.Forms.Button btnTXneg;
        private System.Windows.Forms.Button btnTXpos;
        private System.Windows.Forms.Button btnTYpos;
        private System.Windows.Forms.Button btnTYneg;
        private System.Windows.Forms.Button btnTZpos;
        private System.Windows.Forms.Button btnTZneg;
        private System.Windows.Forms.Button btnRXpos;
        private System.Windows.Forms.Button btnRXneg;
        private System.Windows.Forms.Button btnRYpos;
        private System.Windows.Forms.Button btnRYneg;
        private System.Windows.Forms.Button btnRZpos;
        private System.Windows.Forms.Button btnRZneg;
        private System.Windows.Forms.Button btnOLPdone;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripStatusLabel notifybar;
        private System.Windows.Forms.GroupBox groupRoboDKwindow;
        private System.Windows.Forms.RadioButton rad_RoboDK_hide;
        private System.Windows.Forms.RadioButton rad_RoboDK_show;
        private System.Windows.Forms.GroupBox groupIncrementalMove;
        private System.Windows.Forms.RadioButton rad_Move_Joints;
        private System.Windows.Forms.RadioButton rad_Move_wrt_Tool;
        private System.Windows.Forms.RadioButton rad_Move_wrt_Reference;
        private System.Windows.Forms.Label lblstepIncrement;
        private System.Windows.Forms.NumericUpDown numStep;
        private System.Windows.Forms.RadioButton rad_RunMode_Online;
        private System.Windows.Forms.RadioButton rad_RunMode_Program;
        private System.Windows.Forms.RadioButton rad_RunMode_Simulation;
        private System.Windows.Forms.GroupBox groupRunMode;
        private System.Windows.Forms.Button btnMoveRobotHome;
        private System.Windows.Forms.RadioButton rad_RoboDK_Integrated;
        private System.Windows.Forms.Panel panel_rdk;
    }
}

