classdef RobolinkItem < handle
% The Item class represents an item in RoboDK station.
% An item can be a robot, a frame, a tool, an object, a target, ... (any item visible in the station tree)
% An item can also be seen as a node where other items can be attached to (child items).
% Items (RobolinkItem) are created by certain functions calls from Robolink class.
% Every item has one parent item/node and can have one or more child items/nodes.
% 
% RoboDK api Help:
% ->Type "doc Robolink"            for more help on the Robolink class
% ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
% ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes
    properties (Constant)    
        % Instruction types
        INS_TYPE_INVALID = -1;
        INS_TYPE_MOVE = 0;
        INS_TYPE_MOVEC = 1;
        INS_TYPE_CHANGESPEED = 2;
        INS_TYPE_CHANGEFRAME = 3;
        INS_TYPE_CHANGETOOL = 4;
        INS_TYPE_CHANGEROBOT = 5;
        INS_TYPE_PAUSE = 6;
        INS_TYPE_EVENT = 7;
        INS_TYPE_CODE = 8;
        INS_TYPE_PRINT = 9;
        
    end    
    properties
        item = 0; % This value should not be modified. It stores the object pointer
        link = 0; % This value should not be modified. It stores the connection pointer
        type = 0; % This value should not be modified. It stores the type of the item
    end
    methods
        function this = RobolinkItem(rl, ptr_item, itemtype)
            % Creates an item object from the Robolink() connection and an
            % item number
            if nargin < 2
                ptr_item = 0;
            end
            if nargin < 3
                itemtype = -1;
            end
            this.item = ptr_item;
            this.link = rl;
            this.type = itemtype;
        end
        function rdk = RDK(this)
            % Get the pointer to RoboDK instance
            rdk = this.link;
        end            
        function type = Type(this)
            % Returns an integer that represents the type of the item (robot, object, tool, frame, ...)
            this.link.check_connection();
            command = 'G_Item_Type';
            this.link.send_line(command);
            this.link.send_item(this);
            type = this.link.rec_int(); 
            this.link.check_status();
        end
        function Copy(this)
            % Copy the item to the clipboard (same as Ctrl+C). Use together with Paste() to duplicate items.
            this.link.Copy(this);
        end
        function newitem = Paste(this)
            % Paste the item from the clipboard as a child of this item (same as Ctrl+V)
            % Out 1: item -> new item pasted (created)
            newitem = this.link.Paste(this.item);
        end
        function AddGeometry(this, fromitem, pose)
            % Makes a copy of the geometry fromitem adding it at a given position (pose) relative to this item.
            this.link.check_connection();
            command = 'CopyFaces';
            this.link.send_line(command);
            this.link.send_item(fromitem);
            this.link.send_item(this);
            this.link.send_pose(pose);            
            this.link.check_status();
        end
        function Delete(this)
            % Deletes an item in the station.
            this.link.check_connection();
            command = 'Remove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end
        function valid = Valid(this)
            valid = (this.item ~= 0);
        end
        function setParent(this, parent)
            % Moves the item to another location (parent)
            % In 1  : parent -> parent to attach the item
            this.link.check_connection();
            command = 'S_Parent';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);            
            this.link.check_status();
        end
        function setParentStatic(this, parent)
            % Moves the item to another location (parent) without changing the current position in the station
            % In 1  : parent -> parent to attach the item
            this.link.check_connection();
            command = 'S_Parent_Static';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);            
            this.link.check_status();
        end
        function item_attached = AttachClosest(this)
            % Attaches the closest object to the provided tool.
            % Out  : item -> returns the item that was attached (0 if none found)
            this.link.check_connection();
            command = 'Attach_Closest';
            this.link.send_line(command);
            this.link.send_item(this);
            item_attached = this.link.rec_item();
            this.link.check_status();
        end
        function DetachClosest(this, parent)
            % Detaches the closest object attached to the tool (see also: Set_Parent_Static).
            % In  1 : item (optional) -> parent to leave the objects
            if nargin < 2
                parent = 0;
            end
            this.link.check_connection();
            command = 'Detach_Closest';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);            
            this.link.check_status();
        end    
        function DetachAll(this, parent)
            % Detaches any object attached to a tool (see also: Set_Parent_Static).
            % In  1 : item (optional) -> parent to leave the objects
            if nargin < 2
                parent = RobolinkItem(this.link);
            end
            this.link.check_connection();
            command = 'Detach_All';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);            
            this.link.check_status();
        end        
        function parent = Parent(this)
            % Returns the parent item of the provided item.
            % Out : parent -> parent of the item
            this.link.check_connection();
            command = 'G_Parent';
            this.link.send_line(command);
            this.link.send_item(this);
            parent = this.link.rec_item();
            this.link.check_status();
        end
        function itemlist = Childs(this)
            % Returns a list of the item childs that are attached to the provided item.
            % Out  : child x n -> list of child item pointers
            this.link.check_connection();
            command = 'G_Childs';
            this.link.send_line(command);
            this.link.send_item(this);
            nitems = this.link.rec_int();
            itemlist = cell(nitems,1);
            for i=1:nitems
                itemlist{i} = this.link.rec_item();
            end
            this.link.check_status();
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function visible = Visible(this)
            % Returns 1 if the item is visible, otherwise, returns 0.
            % Out : int -> visible (1) or not visible (0)
            this.link.check_connection();
            command = 'G_Visible';
            this.link.send_line(command);
            this.link.send_item(this);
            visible = this.link.rec_int();
            this.link.check_status();
        end
        function setVisible(this, visible, visible_frame)
            % Sets the item visiblity
            % In 2 : int -> set visible (1) or not visible (0)
            % In 3 : int (optional) -> set visible frame (True or 1) or not visible (False or 0)
            if nargin < 3
                visible_frame = visible;
            end
            this.link.check_connection();
            command = 'S_Visible';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(visible);
            this.link.send_int(visible_frame);            
            this.link.check_status();
        end
        function name = Name(this)
            % Gets the name of an item.
            % Out : name (string)
            this.link.check_connection();
            command = 'G_Name';
            this.link.send_line(command);
            this.link.send_item(this);
            name = this.link.rec_line();
            this.link.check_status();
        end
        function setName(this, name)
            % Sets the name of an item.
            % In 1 : name (string)
            this.link.check_connection();
            command = 'S_Name';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(name);
            this.link.check_status();
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function setPose(this, pose)
            % Sets the local position (pose) of an item. For example, the position of an object/frame/target with respect to its parent.
            % In 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'S_Hlocal';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end
        function pose = Pose(this)
            % Gets the local position (pose) of an item. For example, the position of an object/frame/target with respect to its parent.
            % Out 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'G_Hlocal';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end
        function setHtool(this, pose)
            % Sets the tool pose of an item.
            % In 2 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'S_Htool';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end
        function pose = Htool(this)
            % Gets the tool pose of an item.
            % Out 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'G_Htool';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end
        function setPoseAbs(this, pose)
            % Sts the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
            % In  1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'S_Hlocal_Abs';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end
        function pose = PoseAbs(this)
            % Gets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
            % Out 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'G_Hlocal_Abs';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end
        function color = check_color(~, color)
            % Makes formats color in a vector of size 4x1 and ranges [0,1]
            cs = numel(color);
            color = reshape(color, 1, cs);
            if cs > 4
                color = color(1:4);
            elseif cs < 4
                color = [color(1:end), zeros(1,4-cs)];
                color(4) = 1;
            end
            maxc = max(color);
            if maxc > 1
                color = color/maxc;
            end
        end
        function Recolor(this, tocolor, fromcolor, tolerance)
            % Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            % Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
            % In  1 : color -> color to change to
            % In  2 (optional) : color -> filter by this color
            % In  3 (optional) : int -> optional tolerance to use if a color filter is used (defaults to 0.1)            
            this.link.check_connection();
            if nargin < 3
                fromcolor = [0,0,0,0];
                tolerance = 2;
            elseif nargin < 4
                tolerance = 0.1;
            end
            tocolor = check_color(this,tocolor);     
            fromcolor = check_color(this,fromcolor);       
            command = 'Recolor';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array([tolerance(1), fromcolor, tocolor]);
            this.link.check_status();
        end
        function Scale(this, scale)
            % Apply a scale to an object to make it bigger or smaller.
            % the scale can be uniform (one single value) or per axis (if scale is a vector [scale_x, scale_y, scale_z]).
            % In  1 : scale -> scale to apply
            this.link.check_connection();
            if numel(scale) < 3
                scale = [scale(1); scale(1); scale(1)];
            end
            command = 'Scale';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(scale);
            this.link.check_status();
        end
        function [newprog, status] = setMachiningParameters(this, ncfile, part, params)
            % Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
            if nargin < 4
                params = '';
            end
            this.link.check_connection();
            command = 'S_MachiningParams';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
            this.link.send_line(ncfile);
            this.link.send_item(part);
            this.link.send_line(params);
            set(this.link.COM,'Timeout', 3600);            
            newprog = this.link.rec_item();
            set(this.link.COM,'Timeout', this.link.TIMEOUT);            
            status = this.link.rec_int()/1000.0;
            this.link.check_status();            
        end
        function setAsCartesianTarget(this)
            % Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
            this.link.check_connection();
            command = 'S_Target_As_RT';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end
        function setAsJointTarget(this)
            % Sets a target as a joint target. A joint target moves to a joints position.
            this.link.check_connection();
            command = 'S_Target_As_JT';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end

        function joints = Joints(this)
            % Returns the current joints of a robot or a target. In case of a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
            % Out 1 : double x n -> joints
            this.link.check_connection();
            command = 'G_Thetas';
            this.link.send_line(command);
            this.link.send_item(this);
            joints = this.link.rec_array();
            this.link.check_status();
        end
        function setJoints(this, joints)
            % Sets the current joints of a robot or a target. In case of a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
            % In  1 : double x n -> joints
            this.link.check_connection();
            command = 'S_Thetas';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            this.link.check_status();
        end
        function [lim_inf, lim_sup, joints_type] = JointLimits(this)
            % Retrieve the joint limits of a robot. Returns (lower limits, upper limits, joint type)
            % In  1 : double x n -> joints
            this.link.check_connection();
            command = 'G_RobLimits';
            this.link.send_line(command);
            this.link.send_item(this);
            lim_inf = this.link.rec_array()';
            lim_sup = this.link.rec_array()';
            joints_type = this.link.rec_int()/1000.0;
            this.link.check_status();
        end
        function setRobot(this, robot)
            % Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
            % If the robot is not provided, the first available robot will be chosen automatically.
            % In  1 : robot (optional) -> robot item
            if nargin < 2
                robot = RobolinkItem(this.link);
            end
            this.link.check_connection();
            command = 'S_Robot';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(robot);
            this.link.check_status();
        end
        function setFrame(this, frame)
            % Sets the frame of a robot. The frame can be either an item pointer or a 4x4 Matrix.
            % If "frame" is an item pointer, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
            % In  1 : item/pose -> frame item or 4x4 Matrix (pose of the reference frame)
            this.link.check_connection();
            if numel(frame) == 1
                command = 'S_Frame_ptr';
                this.link.send_line(command);            
                this.link.send_item(frame);
            else
                command = 'S_Frame';
                this.link.send_line(command);
                this.link.send_pose(frame);
            end
            this.link.send_item(this);
            this.link.check_status();
        end
        function setTool(this, tool)
            % Sets the tool pose of a robot. The tool pose can be either an item pointer or a 4x4 Matrix.
            % If "tool" is an item pointer, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
            % In  1 : item/pose -> tool item or 4x4 Matrix (pose of the tool frame)
            this.link.check_connection();
            if numel(tool) == 1
                command = 'S_Tool_ptr';
                this.link.send_line(command);
                this.link.send_item(tool);
            else
                command = 'S_Tool';
                this.link.send_line(command);
                this.link.send_pose(tool);
            end            
            this.link.send_item(this);
            this.link.check_status();
        end
        function pose = SolveFK(this, joints)
            % Computes the forward kinematics for the specified robot and joints.
            % In  1 : double x n -> joints
            % Out 1 : 4x4 matrix -> pose of the robot tool with respect to the robot frame
            this.link.check_connection();
            command = 'G_FK';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end
        function joints = SolveIK(this, pose)
            % Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see Solve_IK_All()).
            % In  1 : 4x4 matrix -> pose of the robot tool with respect to the robot frame
            % Out 1 : double x n -> joints
            this.link.check_connection();
            command = 'G_IK';
            this.link.send_line(command);
            this.link.send_pose(pose);
            this.link.send_item(this);
            joints = this.link.rec_array();
            this.link.check_status();
        end
        function joints_list = SolveIK_All(this, pose)
            % Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
            % In  1 : 4x4 matrix -> pose of the robot tool with respect to the robot frame
            % Out 1 : double x n x m -> joint list (2D matrix)
            this.link.check_connection();
            command = 'G_IK_cmpl';
            this.link.send_line(command);
            this.link.send_pose(pose);
            this.link.send_item(this);
            joints_list = this.link.rec_matrix();
            if size(joints_list,1) > 6
                joints_list = joints_list(1:end-2,:);
            end
            this.link.check_status();
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function status = Connect(this, robot_ip, blocking)
            % Connect to a real robot and wait for a connection to succeed. Returns 1 if connection succeeded, or 0 if it failed.
            % In  1 : Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
            % Out 1 : Status (1 if success)
            if nargin < 2
                robot_ip = '';
            end
            if nargin < 3
                blocking = 1;
            end
            this.link.check_connection();
            command = 'Connect2';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(robot_ip);
            this.link.send_int(blocking);
            status = this.link.rec_int();
            this.link.check_status();
        end
        function [robot_ip, port, remote_path, ftp_user, ftp_pass] = ConnectionParams(this)
            % Retrieve robot connection parameters
            this.link.check_connection();
            command = 'ConnectParams';
            this.link.send_line(command);
            this.link.send_item(this);
            robot_ip = this.link.rec_line();
            port = this.link.rec_int();
            remote_path = this.link.rec_line();
            ftp_user = this.link.rec_line();
            ftp_pass = this.link.rec_line();
        end        
        function itm = setConnectionParams(this, robot_ip, port, remote_path, ftp_user, ftp_pass)
            % Retrieve robot connection parameters
            this.link.check_connection();
            command = 'setConnectParams';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(robot_ip);
            this.link.send_int(port);
            this.link.send_line(remote_path);
            this.link.send_line(ftp_user);
            this.link.send_line(ftp_pass);
            this.link.check_status();
            itm = this;
        end        
        function [robotcom_status, status_msg] = ConnectedState(this)
            % Check connection status with a real robobt
            % Out 1 : status code -> (int) ROBOTCOM_READY if the robot is ready to move, otherwise, status message will provide more information about the issue
            % Out 2 : status message -> Message description of the robot status
            this.link.check_connection();
            command = 'ConnectedState';
            this.link.send_line(command);
            this.link.send_item(this);
            robotcom_status = this.link.rec_int();
            status_msg = this.link.rec_line();            
            this.link.check_status();
        end
        function status = Disconnect(this)
            % Disconnect from a real robot (when the robot driver is used)
            % Returns 1 if it disconnected successfully, 0 if it failed. It can fail if it was previously disconnected manually for example.
            % Out 1 : Status (1 if success)
            this.link.check_connection();
            command = 'Disconnect';
            this.link.send_line(command);
            this.link.send_item(this);
            status = this.link.rec_int();
            this.link.check_status();
        end
        
        function MoveJ(this, target, blocking)
            % Moves a robot to a specific target ("Move Joint" mode). This function blocks until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional): blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 3
                blocking = 1;
            end
            if this.type == this.link.ITEM_TYPE_PROGRAM
                if class(target) ~= class(this)
                    error('Adding a movement instruction to a program given joints or a pose is not supported. Use a target item instead, for example, add a target as with RDK.AddTarget(...) and set the pose or joints.')
                end
                this.addMoveJ(target)
            else
                this.link.moveX(target,this,1,blocking);
            end
        end
        function MoveL(this, target, blocking)
            % Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional): blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 3
                blocking = 1;
            end
            if this.type == this.link.ITEM_TYPE_PROGRAM
                if ~isa(target, class(this))
                    error('Adding a movement instruction to a program given joints or a pose is not supported. Use a target item instead, for example, add a target as with RDK.AddTarget(...) and set the pose or joints.')
                end
                this.addMoveL(target);
            else
                this.link.moveX(target,this,2,blocking);
            end
        end
        function MoveC(this, target1, target2, blocking)
            % Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional): blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 4
                blocking = 1;
            end
            if this.type == this.link.ITEM_TYPE_PROGRAM
                if ~isa(target1, class(this)) || ~isa(target2, class(this))
                    error('Adding a movement instruction to a program given joints or a pose is not supported. Use a target item instead, for example, add a target as with RDK.AddTarget(...) and set the pose or joints.')
                end
                this.addMoveC(target1,target2);
            else
                this.link.moveC(target1,target2,this,blocking);
            end
        end
        function collision = MoveJ_Test(this, j1, j2, minstep_deg)
            % Checks if a joint movement is free of collision.
            % In  1 : joints -> start joints
            % In  2 : joints -> destination joints
            % In  3 (optional): maximum joint step in degrees
            % Out : collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.
            if nargin < 4
                minstep_deg = -1;
            end
            this.link.check_connection();
            command = 'CollisionMove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(j1);
            this.link.send_array(j2);            
            this.link.send_int(minstep_deg*1000);
            set(this.link.COM,'Timeout', 3600);
            collision = this.link.rec_int();
            set(this.link.COM,'Timeout', this.link.TIMEOUT);            
            this.link.check_status();   
        end   
        function collision = MoveL_Test(this, j1, poseto, minstep_deg)
            % Checks if a joint movement is free of collision.
            % In  1 : joints -> start joints
            % In  2 : pose -> destination pose with respect to current reference and tool frames
            % In  3 (optional): maximum joint step in degrees
            % Out : collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.
            %                  if the robot can not reach the target pose it returns -2. If the robot can reach the target but it can not make a linear movement it returns -1
            if nargin < 4
                minstep_deg = -1;
            end
            this.link.check_connection();
            command = 'CollisionMoveL';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(j1);
            this.link.send_pose(poseto);            
            this.link.send_int(minstep_deg*1000);
            set(this.link.COM,'Timeout', 3600);
            collision = this.link.rec_int();
            set(this.link.COM,'Timeout', this.link.TIMEOUT);            
            this.link.check_status();   
        end   
        function setSpeed(this, speed_linear, speed_joints, accel_linear, accel_joints)
            % Sets the speed and/or the acceleration of a robot.
            % In  1 : speed_linear: linear speed -> speed in mm/s (-1 = no change)
            % In  2 : speed_joints: joint speed (optional) -> acceleration in mm/s2 (-1 = no change)
            % In  3 : accel_linear: linear acceleration (optional) -> acceleration in mm/s2 (-1 = no change)
            % In  4 : accel_joints: joint acceleration (optional) -> acceleration in deg/s2 (-1 = no change)
            if nargin < 3
                speed_joints = -1;
            end
            if nargin < 4
                accel_linear = -1;
            end
            if nargin < 5
                accel_joints = -1;
            end            
            this.link.check_connection();
            command = 'S_Speed4';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array([speed_linear, speed_joints, accel_linear, accel_joints]);            
            this.link.check_status();            
        end
        function setZoneData(this, zonedata)
            % Sets the robot zone data value.
            % In  1 : zonedata value (robot dependent, set to -1 for fine movements)
            this.link.check_connection();
            command = 'S_ZoneData';
            this.link.send_line(command);
            this.link.send_int(zonedata*1000);         
            this.link.send_item(this);
            this.link.check_status();
        end
        function ShowSequence(this, sequence)
            % Sends a joint sequence or an instruction sequence (like in RoKiSim).
            % In  1 : sequence
            this.link.check_connection();
            command = 'Show_Seq';
            this.link.send_line(command);
            this.link.send_matrix(sequence);         
            this.link.send_item(this);
            this.link.check_status();
        end
        function busy = Busy(this)
            % Checks if a robot or program is currently running (busy or moving).
            % In  1 : item -> robot to check
            % Out 1 : int -> busy status (1=moving, 0=stopped)
            this.link.check_connection();
            command = 'IsBusy';
            this.link.send_line(command);
            this.link.send_item(this);
            busy = this.link.rec_int();
            this.link.check_status();
        end
        function WaitMove(this, timeout)
            % Waits (blocks) until the robot finished its move.
            % In  1 (optional): timeout -> Max time to wait for robot to finish its movement (in seconds)
            if nargin < 2
                timeout = 300;
            end
            this.link.check_connection();
            command = 'WaitMove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
            set(this.link.COM,'Timeout', timeout);
            this.link.check_status();
            set(this.link.COM,'Timeout', this.link.TIMEOUT);
%             busy = Is_Busy(this, itemrobot);
%             while busy
%                 busy = Is_Busy(this, itemrobot);
%             end
        end
        function prog_status = RunProgram(this)
            % Runs a program. It returns the number of instructions that can be executed successfully (a quick check is performed before the program starts)
            % This is a non-blocking call.
            % Out 1 : int -> number of instructions that can be executed        
            this.link.check_connection();
            command = 'RunProg';
            this.link.send_line(command);
            this.link.send_item(this);          
            prog_status = this.link.rec_int();
            this.link.check_status();
        end  
        function addMoveJ(this, itemtarget)
            % Adds a new "Move Joint" instruction to a program.
            % In  1 : item -> target to move to         
            this.link.check_connection();
            command = 'Add_INSMOVE';
            this.link.send_line(command);
            this.link.send_item(itemtarget);
            this.link.send_item(this);
            this.link.send_int(1);
            this.link.check_status();
        end
        function addMoveL(this, itemtarget)
            % (Obsolete, use MoveL instead) Adds a new "Move Linear" instruction to a program.
            % In  1 : item -> target to move to          
            this.link.check_connection();
            command = 'Add_INSMOVE';
            this.link.send_line(command);
            this.link.send_item(itemtarget);
            this.link.send_item(this);
            this.link.send_int(2);
            this.link.check_status();
        end  
        function addMoveC(this, itemtarget1, itemtarget2)
            % (Obsolete, use MoveC instead) Adds a new "Move Circular" instruction to a program.
            % In  1 : item -> target to move to (via point)
            % In  2 : item -> target to move to (final point)
            this.link.check_connection();
            command = 'Add_INSMOVEC';
            this.link.send_line(command);
            this.link.send_item(itemtarget1);
            this.link.send_item(itemtarget2);
            this.link.send_item(this);
            this.link.check_status();
        end  
        function ShowInstructions(this, display)
            % Show or hide instruction items of a program in the RoboDK tree
            if nargin < 2
                display = 1;
            end
            this.link.check_connection();
            command = 'Prog_ShowIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(display);   
            this.link.check_status();
        end
        function ShowTargets(this, display)
            % Show or hide targets of a program in the RoboDK tree
            if nargin < 2
                display = 1;
            end
            this.link.check_connection();
            command = 'Prog_ShowTargets';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(display);
            this.link.check_status();
        end
        function nins = InstructionCount(this)
            % Returns the number of instructions of a program.        
            this.link.check_connection();
            command = 'Prog_Nins';
            this.link.send_line(command);
            this.link.send_item(this);
            nins = this.link.rec_int();
            this.link.check_status();
        end  
        function [name, instype, movetype, isjointtarget, target, joints] = Instruction(this, ins_id)
            % Returns the program instruction at position id.     
            this.link.check_connection();
            command = 'Prog_GIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(ins_id-1);
            name = this.link.rec_line();
            instype = this.link.rec_int();
            movetype = -1;
            isjointtarget = -1;
            target = -1;
            joints = -1;
            if instype == this.INS_TYPE_MOVE
                movetype = this.link.rec_int();
                isjointtarget = this.link.rec_int();
                target = this.link.rec_pose();
                joints = this.link.rec_array();
            end
            this.link.check_status();
        end 
        function setInstruction(this, ins_id, name, instype, movetype, isjointtarget, target, joints)
            % Sets the program instruction at position id. 
            this.link.check_connection();
            command = 'Prog_SIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(ins_id-1);
            this.link.send_line(name);
            this.link.send_int(instype);
            if instype == this.INS_TYPE_MOVE
                this.link.send_int(movetype);
                this.link.send_int(isjointtarget);
                this.link.send_pose(target);
                this.link.send_array(joints);
            end
            this.link.check_status();
        end       
    end    
end