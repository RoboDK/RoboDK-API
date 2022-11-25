% Copyright 2015-2022 - RoboDK Inc. - https://robodk.com/
% Licensed under the Apache License, Version 2.0 (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at
% http://www.apache.org/licenses/LICENSE-2.0
% Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.
%
% --------------------------------------------
% --------------- DESCRIPTION ----------------
% This file defines the following class:
%     Robolink()
%
% These classes are the objects used to interact with RoboDK and create macros.
% An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
% Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method)
%
% More information about the RoboDK API for Python here:
%     https://robodk.com/doc/en/RoboDK-API.html
%     https://robodk.com/doc/en/PythonAPI/index.html
%
% --------------------------------------------

classdef Robolink < handle
    % The Robolink class is the link to RoboDK and allows creating macros for Robodk, simulate applications and generate programs offline.
    % Any interaction is made through "items" (Item() objects). An item is an object in the robodk tree (it can be either a robot, an object, a tool, a frame, a program, ...).
    %
    % RoboDK api Help:
    % ->Type "doc Robolink"            for more help on the Robolink class
    % ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
    % ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes
    properties (Constant)

        % Tree item types
        ITEM_TYPE_STATION = 1;
        ITEM_TYPE_ROBOT = 2;
        ITEM_TYPE_FRAME = 3;
        ITEM_TYPE_TOOL = 4;
        ITEM_TYPE_OBJECT = 5;
        ITEM_TYPE_TARGET = 6;
        ITEM_TYPE_CURVE = 7;
        ITEM_TYPE_PROGRAM = 8;
        ITEM_TYPE_INSTRUCTION = 9
        ITEM_TYPE_PROGRAM_PYTHON = 10;
        ITEM_TYPE_MACHINING = 11;
        ITEM_TYPE_BALLBARVALIDATION = 12;
        ITEM_TYPE_CALIBPROJECT = 13;
        ITEM_TYPE_VALID_ISO9283 = 14;
        ITEM_TYPE_FOLDER = 17;
        ITEM_TYPE_ROBOT_ARM = 18;
        ITEM_TYPE_CAMERA = 19;
        ITEM_TYPE_GENERIC = 20;
        ITEM_TYPE_ROBOT_AXES = 21;
        ITEM_TYPE_NOTES = 22;

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
        INS_TYPE_ROUNDING = 10;

        % Move types
        MOVE_TYPE_INVALID = -1;
        MOVE_TYPE_JOINT = 1;
        MOVE_TYPE_LINEAR = 2;
        MOVE_TYPE_CIRCULAR = 3;
        MOVE_TYPE_LINEARSEARCH = 5;

        % Station parameters request
        PATH_OPENSTATION = 'PATH_OPENSTATION';
        FILE_OPENSTATION = 'FILE_OPENSTATION';
        PATH_DESKTOP = 'PATH_DESKTOP';

        % Script execution types
        RUNMODE_SIMULATE = 1; % performs the simulation moving the robot (default)
        RUNMODE_QUICKVALIDATE = 2; % performs a quick check to validate the robot movements
        RUNMODE_MAKE_ROBOTPROG = 3; % makes the robot program
        RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4; % makes the robot program and updates it to the robot
        RUNMODE_MAKE_ROBOTPROG_AND_START = 5; % makes the robot program and starts it on the robot (independently from the PC)
        RUNMODE_RUN_ROBOT = 6; % moves the real robot from the PC (PC is the client, the robot behaves like a server)

        % Program execution type
        PROGRAM_RUN_ON_SIMULATOR = 1; % Set the program to run on the simulator
        PROGRAM_RUN_ON_ROBOT = 2; % Set the program to run on the robot

        % Robot connection status
        ROBOTCOM_PROBLEMS = -3;
        ROBOTCOM_DISCONNECTED = -2;
        ROBOTCOM_NOT_CONNECTED = -1;
        ROBOTCOM_READY = 0;
        ROBOTCOM_WORKING = 1;
        ROBOTCOM_WAITING = 2;
        ROBOTCOM_UNKNOWN = -1000;

        % TCP calibration types
        CALIBRATE_TCP_BY_POINT = 0;
        CALIBRATE_TCP_BY_PLANE = 1;
        CALIBRATE_TCP_BY_PLANE_SCARA = 4;

        % Reference frame calibration methods
        CALIBRATE_FRAME_3P_P1_ON_X = 0;
        CALIBRATE_FRAME_3P_P1_ORIGIN = 1;
        CALIBRATE_FRAME_6P = 2;
        CALIBRATE_TURNTABLE = 3;
        CALIBRATE_TURNTABLE_2X = 4;

        % projection types (for AddCurve)
        PROJECTION_NONE = 0; % No curve projection
        PROJECTION_CLOSEST = 1; % The projection will the closest point on the surface
        PROJECTION_ALONG_NORMAL = 2; % The projection will be done along the normal.
        PROJECTION_ALONG_NORMAL_RECALC = 3; % The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
        PROJECTION_CLOSEST_RECALC = 4; % The projection will be the closest point on the surface and the normals will be recalculated
        PROJECTION_RECALC = 5; % The normals are recalculated according to the surface normal of the closest projection. The points are not changed.

        % Euler type
        EULER_RX_RYp_RZpp = 0; % generic
        EULER_RZ_RYp_RXpp = 1; % ABB RobotStudio
        EULER_RZ_RYp_RZpp = 2; % Kawasaki, Adept, Staubli
        EULER_RZ_RXp_RZpp = 3; % CATIA, SolidWorks
        EULER_RX_RY_RZ = 4; % Fanuc, Kuka, Motoman, Nachi
        EULER_RZ_RY_RX = 5; % CRS
        EULER_QUEATERNION = 6; % ABB Rapid

        % State of the RoboDK window
        WINDOWSTATE_HIDDEN = -1;
        WINDOWSTATE_SHOW = 0;
        WINDOWSTATE_MINIMIZED = 1;
        WINDOWSTATE_NORMAL = 2;
        WINDOWSTATE_MAXIMIZED = 3;
        WINDOWSTATE_FULLSCREEN = 4;
        WINDOWSTATE_CINEMA = 5;
        WINDOWSTATE_FULLSCREEN_CINEMA = 6;
        WINDOWSTATE_VIDEO = 7;

        % Instruction program call type:
        INSTRUCTION_CALL_PROGRAM = 0;
        INSTRUCTION_INSERT_CODE = 1;
        INSTRUCTION_START_THREAD = 2;
        INSTRUCTION_COMMENT = 3;
        INSTRUCTION_SHOW_MESSAGE = 4;

        % Object selection features
        FEATURE_NONE = 0;
        FEATURE_SURFACE = 1;
        FEATURE_CURVE = 2;
        FEATURE_POINT = 3;
        FEATURE_OBJECT_MESH = 7;
        FEATURE_SURFACE_PREVIEW = 8;
        FEATURE_MESH = 9;
        % The following do not require providing an object
        FEATURE_HOVER_OBJECT_MESH = 10;
        FEATURE_HOVER_OBJECT = 11;

        % Spray gun simulation:
        SPRAY_OFF = 0;
        SPRAY_ON = 1;

        % Collision checking state
        COLLISION_OFF = 0 % Collision checking turned Off
        COLLISION_ON = 1 % Collision checking turned On

        % RoboDK Window Flags
        FLAG_ROBODK_TREE_ACTIVE = 1;
        FLAG_ROBODK_3DVIEW_ACTIVE = 2;
        FLAG_ROBODK_LEFT_CLICK = 4;
        FLAG_ROBODK_RIGHT_CLICK = 8;
        FLAG_ROBODK_DOUBLE_CLICK = 16;
        FLAG_ROBODK_MENU_ACTIVE = 32;
        FLAG_ROBODK_MENUFILE_ACTIVE = 64;
        FLAG_ROBODK_MENUEDIT_ACTIVE = 128;
        FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256;
        FLAG_ROBODK_MENUTOOLS_ACTIVE = 512;
        FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024;
        FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048;
        FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096;
        FLAG_ROBODK_TREE_VISIBLE = 8192;
        FLAG_ROBODK_REFERENCES_VISIBLE = 16384;
        FLAG_ROBODK_STATUSBAR_VISIBLE = 32768;
        FLAG_ROBODK_NONE = 0;
        FLAG_ROBODK_ALL = 65535;
        FLAG_ROBODK_MENU_ACTIVE_ALL = 4064; % FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE;

        % RoboDK Item Flags
        FLAG_ITEM_SELECTABLE = 1;
        FLAG_ITEM_EDITABLE = 2;
        FLAG_ITEM_DRAGALLOWED = 4;
        FLAG_ITEM_DROPALLOWED = 8;
        FLAG_ITEM_ENABLED = 32;
        FLAG_ITEM_AUTOTRISTATE = 64
        FLAG_ITEM_NOCHILDREN = 128
        FLAG_ITEM_USERTRISTATE = 256
        FLAG_ITEM_NONE = 0;
        FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1;

        % Robot/mechanism types
        MAKE_ROBOT_1R = 1;
        MAKE_ROBOT_2R = 2;
        MAKE_ROBOT_3R = 3;
        MAKE_ROBOT_1T = 4;
        MAKE_ROBOT_2T = 5;
        MAKE_ROBOT_3T = 6;
        MAKE_ROBOT_6DOF = 7;
        MAKE_ROBOT_7DOF = 8;
        MAKE_ROBOT_SCARA = 9;
        MAKE_ROBOT_GRIPPER = 10;
        MAKE_ROBOT_6COBOT = 11;
        MAKE_ROBOT_1T1R = 12;
        MAKE_ROBOT_5XCNC = 13;
        MAKE_ROBOT_3T1R = 15;
        MAKE_ROBOT_GENERIC = 16;

        % Path Error bit mask
        ERROR_KINEMATIC = 1;
        ERROR_PATH_LIMIT = 2;
        ERROR_PATH_SINGULARITY = 4;
        ERROR_PATH_NEARSINGULARITY = 8;
        ERROR_COLLISION = 32;

        % Interactive selection option (for 3D mouse behavior and setInteractiveMode)
        SELECT_RESET = -1;
        SELECT_NONE = 0;
        SELECT_RECTANGLE = 1;
        SELECT_ROTATE = 2;
        SELECT_ZOOM = 3;
        SELECT_PAN = 4;
        SELECT_MOVE = 5;
        SELECT_MOVE_SHIFT = 6;
        SELECT_MOVE_CLEAR = 7;

        % Bit masks to show specific reference frames and customize the display of references (for picking references with the 3D mouse and setInteractiveMode)
        DISPLAY_REF_DEFAULT = -1;
        DISPLAY_REF_NONE = 0;
        DISPLAY_REF_TX = 1;
        DISPLAY_REF_TY = 2;
        DISPLAY_REF_TZ = 4;
        DISPLAY_REF_RX = 8;
        DISPLAY_REF_RY = 16;
        DISPLAY_REF_RZ = 32;
        DISPLAY_REF_PXY = 64;
        DISPLAY_REF_PXZ = 128;
        DISPLAY_REF_PYZ = 256;

        VISIBLE_REFERENCE_DEFAULT = -1;
        VISIBLE_REFERENCE_ON = 1;
        VISIBLE_REFERENCE_OFF = 0;
        VISIBLE_ROBOT_NONE = 0;
        VISIBLE_ROBOT_FLANGE = 1;
        VISIBLE_ROBOT_AXIS_Base_3D = 2;
        VISIBLE_ROBOT_AXIS_Base_REF = 4;
        VISIBLE_ROBOT_AXIS_1_3D = 8;
        VISIBLE_ROBOT_AXIS_1_REF = 16;
        VISIBLE_ROBOT_AXIS_2_3D = 32;
        VISIBLE_ROBOT_AXIS_2_REF = 64;
        VISIBLE_ROBOT_AXIS_3_3D = 128;
        VISIBLE_ROBOT_AXIS_3_REF = 256;
        VISIBLE_ROBOT_AXIS_4_3D = 512;
        VISIBLE_ROBOT_AXIS_4_REF = 1024;
        VISIBLE_ROBOT_AXIS_5_3D = 2048;
        VISIBLE_ROBOT_AXIS_5_REF = 4096;
        VISIBLE_ROBOT_AXIS_6_3D = 2 * 4096;
        VISIBLE_ROBOT_AXIS_6_REF = 4 * 4096;
        VISIBLE_ROBOT_AXIS_7_3D = 8 * 4096;
        VISIBLE_ROBOT_AXIS_7_REF = 16 * 4096;
        VISIBLE_ROBOT_DEFAULT = 715827883;
        VISIBLE_ROBOT_ALL = 2147483647;
        VISIBLE_ROBOT_ALL_REFS = 357913941;

        % ShowSequence() display type flags (use as mask)
        SEQUENCE_DISPLAY_DEFAULT = -1;
        SEQUENCE_DISPLAY_TOOL_POSES = 0;
        SEQUENCE_DISPLAY_ROBOT_POSES = 256;
        SEQUENCE_DISPLAY_ROBOT_JOINTS = 2048;
        SEQUENCE_DISPLAY_COLOR_SELECTED = 1;
        SEQUENCE_DISPLAY_COLOR_TRANSPARENT = 2;
        SEQUENCE_DISPLAY_COLOR_GOOD = 3;
        SEQUENCE_DISPLAY_COLOR_BAD = 4;
        SEQUENCE_DISPLAY_OPTION_RESET = 1024;

        % Other public variables
        TIMEOUT = 5; % timeout for communication, in seconds
    end

    properties
        APPLICATION_DIR = 'C:\RoboDK\bin\RoboDK.exe'; % file path to the Robodk program (executable)
        COM = 0; % tcpip com
    end

    properties (GetAccess = 'private', SetAccess = 'private')
        SAFE_MODE = 1; % checks that provided items exist in memory
        AUTO_UPDATE = 0; % if AUTO_UPDATE is zero, the scene is rendered after every function call
        PORT_START = 20500; % port to start looking for app connection
        PORT_END = 20500; % port to stop looking for app connection
        PORT = -1;
    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    methods % (Access = 'private')

        function connected = is_connected(this)
            % This is a private function.
            % Returns 1 if connection is valid, returns 0 if connection is invalid
            connected = 1;
        end

        function check_connection(this)
            % This is a private function.
            % If we are not connected it will attempt a connection, if it fails, it will throw an error
            if ~is_connected(this) && Connect(this) ~= 1
                error('Unable to connect');
            end

        end

        function status = check_status(this)
            % This is a private function.
            % This function checks the status of the connection
            lastwarn(''); % makes timeout warning an error
            status = rec_int(this);

            if ~isempty(lastwarn)
                error(lastwarn)
            end

            if status == 0
                % everything is OK
            elseif status > 0 && status < 10
                strproblems = 'Unknown error';

                switch status
                    case 1
                        strproblems = 'Invalid item provided: The item identifier provided is not valid or it does not exist.';
                    case 2 % output warning
                        strproblems = rec_line(this);
                        warning(strproblems);
                        status = 0;
                        return
                    case 3 % output error
                        strproblems = rec_line(this);
                    case 9
                        strproblems = 'Invalid license. Purchase a license online (www.robodk.com) or contact us at info@robodk.com.';
                    otherwise
                        % do nothing
                end

                fprintf([strproblems, '\n']);
                error(strproblems);
            elseif status < 100
                % Since RoboDK 4.0 we raise dedicated errors
                strproblems = rec_line(this);
                fprintf([strproblems, '\n']);
                error(strproblems);
            else
                disp(status)
                error('Problems running function');
            end

        end

        function send_line(this, string)
            % This is a private function.
            % Sends a string of characters with a \n
            write(this.COM, uint8([string, char(10)]));
        end

        function string = rec_line(this)
            % This is a private function.
            % Receives a string. It reads until if finds \n
            string = [];
            chari = read(this.COM, 1, 'uint8');

            while chari ~= 10 %LF
                string = [string, chari];
                chari = read(this.COM, 1, 'uint8');
            end

            string = char(string);
        end

        function send_item(this, item)
            % This is a private function.
            % Sends an item pointer
            write(this.COM, uint64(item.item(1)));
        end

        function item = rec_item(this)
            % This is a private function.
            % Receives an item pointer
            itemnum = read(this.COM, 1, 'uint64');
            itemtype = rec_int(this); %read(this.COM, 1, 'int32');
            item = RobolinkItem(this, itemnum, itemtype);
        end

        function send_ptr(this, ptr)
            % This is a private function.
            % Sends an item pointer
            write(this.COM, uint64(ptr));
        end

        function item = rec_ptr(this)
            % This is a private function.
            % Receives an item pointer
            ptr = read(this.COM, 1, 'uint64');
            item = ptr;
        end

        function bytes = bytes_double(this, num)
            % This is a private function.
            % Sends an int (32 bits)
            bytes = flip(typecast(double(num), 'uint8'));
        end

        function num = rec_double(this)
            % This is a private function.
            % Receives an int (32 bits)
            bytes = read(this.COM, 8, 'uint8');
            num = typecast(flip(bytes), 'double');
        end

        function send_pose(this, pose)
            % This is a private function.
            % Sends a pose (4x4 matrix)
            size1 = size(pose, 1);
            size2 = size(pose, 2);

            if size1 ~= 4 || size2 ~= 4
                disp(pose);
                error('Invalid pose');
            end

            bytes = [];

            for j = 1:4

                for i = 1:4
                    bytes = [bytes, bytes_double(this, pose(i, j))];
                end

            end

            write(this.COM, bytes);
        end

        function pose = rec_pose(this)
            % This is a private function.
            % Receives a pose (4x4 matrix)
            pose = eye(4);

            for j = 1:4

                for i = 1:4
                    pose(i, j) = rec_double(this);
                end

            end

        end

        function send_xyz(this, pos)
            % This is a private function.
            % Sends an xyz vector
            bytes = [];

            for i = 1:3
                bytes = [bytes, bytes_double(this, pos(i))];
            end

            write(this.COM, bytes);
        end

        function pos = rec_xyz(this)
            % This is a private function.
            % Receives an xyz vector (3x1 matrix)
            pos = [];

            for i = 1:3
                pos = [pos, rec_double(this)];
            end

        end

        function send_int(this, num)
            % This is a private function.
            % Sends an int (32 bits)
            if numel(num) > 1
                num = num(1);
            end

            bytes = typecast(int32(num), 'uint8');
            write(this.COM, flip(bytes));
        end

        function num = rec_int(this)
            % This is a private function.
            % Receives an int (32 bits)
            bytes = read(this.COM, 4, 'uint8');
            num = typecast(flip(bytes), 'int32');
        end

        function send_array(this, values)
            % This is a private function.
            % Sends an array of doubles
            nval = numel(values);
            send_int(this, nval);

            if nval == 0
                return;
            end

            bytes = [];

            for i = 1:nval
                bytes = [bytes, bytes_double(this, values(i))];
            end

            write(this.COM, bytes);
        end

        function values = rec_array(this)
            % This is a private function.
            % Receives an array of doubles
            nvalues = rec_int(this);
            values = [];

            for i = 1:nvalues
                values = [values, rec_double(this)];
            end

        end

        function send_matrix(this, mat)
            % This is a private function.
            % Sends a 2 dimensional matrix (nxm)
            size1 = size(mat, 1);
            size2 = size(mat, 2);
            send_int(this, size1);
            send_int(this, size2);
            bytes = [];

            for j = 1:size2

                for i = 1:size1
                    bytes = [bytes, bytes_double(this, mat(i, j))];
                end

            end

            write(this.COM, bytes);
        end

        function mat = rec_matrix(this)
            % This is a private function.
            % Receives a 2 dimensional matrix (nxm)
            size1 = rec_int(this);
            size2 = rec_int(this);
            mat = zeros(size1, size2);

            for j = 1:size2

                for i = 1:size1
                    mat(i, j) = rec_double(this);
                end

            end

        end

        function moveX(this, target, itemrobot, movetype, blocking)
            % This is a private function.
            % Performs a linear or joint movement. Use MoveJ or MoveL instead.
            if nargin < 5
                blocking = 300;
            end

            %check_connection(this);
            itemrobot.WaitMove(); % checks connection

            if blocking
                command = 'MoveXb';
            else
                command = 'MoveX';
            end

            send_line(this, command);
            send_int(this, movetype);

            if numel(target) == 1 % target is an item
                send_int(this, 3);
                send_array(this, []);
                send_item(this, target);
            elseif size(target, 1) == 1 || size(target, 2) == 1 % target are joints
                send_int(this, 1);
                send_array(this, target);
                send_item(this, RobolinkItem(this, 0));
            elseif numel(target) == 16 % target is a pose
                send_int(this, 2);
                send_array(this, target);
                send_item(this, RobolinkItem(this, 0));
            else
                error('Invalid input values');
            end

            send_item(this, itemrobot);
            check_status(this);

            if blocking
                %itemrobot.WaitMove();
                this.COM.Timeout = 360000;
                check_status(this);
                this.COM.Timeout = this.TIMEOUT;
            end

        end

        function moveC(this, target1, target2, itemrobot, blocking)
            % Performs a circular movement. Use robot.MoveC instead
            itemrobot.WaitMove(); % checks connection

            if blocking
                command = 'MoveCb';
            else
                command = 'MoveC';
            end

            send_line(this, command);
            send_int(this, 3);

            if numel(target1) == 1 % target1 is an item
                send_int(this, 3);
                send_array(this, []);
                send_item(this, target1);
            elseif size(target1, 1) == 1 || size(target1, 2) == 1 % target1 are joints
                send_int(this, 1);
                send_array(this, target1);
                send_item(this, RobolinkItem(this, 0));
            elseif numel(target1) == 16 % target1 is a pose
                send_int(this, 2);
                send_array(this, target1);
                send_item(this, RobolinkItem(this, 0));
            else
                error('Invalid input value for target 1');
            end

            if numel(target2) == 1 % target1 is an item
                send_int(this, 3);
                send_array(this, []);
                send_item(this, target2);
            elseif size(target2, 1) == 1 || size(target2, 2) == 1 % target2 are joints
                send_int(this, 1);
                send_array(this, target2);
                send_item(this, RobolinkItem(this, 0));
            elseif numel(target2) == 16 % target2 is a pose
                send_int(this, 2);
                send_array(this, target2);
                send_item(this, RobolinkItem(this, 0));
            else
                error('Invalid input value for target 2');
            end

            send_item(this, itemrobot);
            check_status(this);

            if blocking
                %itemrobot.WaitMove();
                this.COM.Timeout = 360000;
                check_status(this);
                this.COM.Timeout = this.TIMEOUT;
            end

        end

    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    methods

        function this = Robolink()
            % Creates a connection to the RoboDK's API
            Connect(this);
        end

        function ok = Set_connection_params(this, safe_mode, auto_update, timeout)
            % Sets the API behavior parameters: SAFE_MODE, AUTO_UPDATE and TIMEOUT.
            % SAFE_MODE checks that item pointers provided by the user are valid.
            % AUTO_UPDATE checks that item pointers provided by the user are valid.
            % TIMEOUT is the timeout to wait for a response. Increase if you experience problems loading big files.
            % If connection failed returns 0.
            % Example:  Set_connection_params(0,0); % Use for speed. Render() must be called to refresh the window.
            %           Set_connection_params(1,1); % Default behavior. Updates every time.
            % In  1 (optional) : int -> SAFE_MODE (1=yes, 0=no)
            % In  2 (optional) : int -> AUTO_UPDATE (1=yes, 0=no)
            % In  3 (optional) : int -> TIMEOUT (1=yes, 0=no)
            % Out 1 : int -> connection status (1=ok, 0=problems)
            if nargin > 1
                this.SAFE_MODE = safe_mode;
            end

            if nargin > 2
                this.AUTO_UPDATE = auto_update;
            end

            if nargin > 3
                this.TIMEOUT = timeout;
            end

            write(this.COM, uint8(['CMD_START', char(10)]));
            write(this.COM, uint8([sprintf('%i %i', this.SAFE_MODE, this.AUTO_UPDATE), char(10)])); % appends LF
            response = rec_line(this);

            if strcmp(response, 'READY')
                ok = 1;
            else
                ok = 0;
            end

        end

        function connected = Connect(this)
            % Establishes a connection with Robodk. RoboDK must be running, otherwise, the variable APPLICATION_DIR must be set properly.
            % If the connection succeededs it returns 1, otherwise it returns 0
            connected = 0;
            port_ok = -1;

            for i = 1:2

                for port = this.PORT_START:this.PORT_END

                    try
                        this.COM = tcpclient('localhost', port, 'Timeout', this.TIMEOUT);
                        connected = is_connected(this);

                        if connected
                            port_ok = port;
                            break
                        end

                    catch

                    end

                end

                if connected % if status is closed, try to open application
                    this.PORT = port_ok;
                    break;
                else

                    try
                        winopen(this.APPLICATION_DIR);
                        pause(2);
                    catch
                        error(['application path is not correct or could not start: ', this.APPLICATION_DIR]);
                    end

                end

            end

            if connected && ~Set_connection_params(this)
                connected = 0;
            end

        end

    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    methods

        function item = Item(this, name, itemtype)
            % Returns an item by its name. If there is no exact match it will return the last closest match.
            % Example: item = Item('Robot');
            check_connection(this);

            if nargin < 3
                command = 'G_Item';
                send_line(this, command);
                send_line(this, name);
            else
                command = 'G_Item2';
                send_line(this, command);
                send_line(this, name);
                send_int(this, itemtype);
            end

            item = rec_item(this); %     item = fread(com, 2, 'ulong'); % ulong is 32 bits!!!
            check_status(this);
        end

        function list = ItemList(this, filter, list_names)
            % Returns a list of items (list of name or pointers) of all available items in the currently open station of RoboDK.
            check_connection(this);

            if nargin < 2
                filter = -1;
            end

            if nargin < 3
                list_names = false;
            end

            if list_names

                if filter < 0
                    command = 'G_List_Items';
                    this.send_line(command);
                else
                    command = 'G_List_Items_Type';
                    this.send_line(command);
                    this.send_int(filter);
                end

                count = rec_int(this);
                list = cell(1, count);

                for i = 1:count
                    namei = rec_line(this);
                    list{i} = namei;
                end

            else

                if filter < 0
                    command = 'G_List_Items_ptr';
                    this.send_line(command);
                else
                    command = 'G_List_Items_Type_ptr';
                    this.send_line(command);
                    this.send_int(filter);
                end

                count = rec_int(this);
                list = cell(1, count);

                for i = 1:count
                    itemi = rec_item(this);
                    list{i} = itemi;
                end

            end

            check_status(this);
        end

        function item = ItemUserPick(this, message, itemtype)
            % Shows a RoboDK popup to select one object from the open station.
            % An item type can be specified to filter desired items. If no type is specified, all items are selectable.
            % (check variables ITEM_TYPE_*)
            % Example:
            %   RL.ItemUserPick("Pick a robot", ITEM_TYPE_ROBOT)
            if nargin < 2
                message = 'Pick one item';
            end

            if nargin < 3
                itemtype = -1;
            end

            check_connection(this)
            command = 'PickItem';
            send_line(this, command);
            send_line(this, message);
            send_int(this, itemtype);
            this.COM.Timeout = 3600; % wait up to 1 hour for user input
            item = rec_item(this);
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end

        function ShowRoboDK(this)
            % Shows or raises the RoboDK window
            check_connection(this);
            command = 'RAISE';
            send_line(this, command);
            check_status(this);
        end

        function HideRoboDK(this)
            % Hide the RoboDK window. RoboDK will keep running as a process
            check_connection(this);
            command = 'HIDE';
            send_line(this, command);
            check_status(this);
        end

        function CloseRoboDK(this)
            % Close RoboDK window and finish RoboDK's execution.
            check_connection(this);
            command = 'QUIT';
            send_line(this, command);
            check_status(this);
        end

        function ver = Version(this)
            % Return RoboDK's version as a string
            check_connection(this);
            command = 'Version';
            send_line(this, command);
            app_name = rec_line(this);
            bit_arch = rec_int(this);
            ver = rec_line(this);
            date_build = rec_line(this);
            check_status(this);
        end

        function setWindowState(this, windowstate)
            % Set the state of the RoboDK window
            if nargin < 2
                windowstate = this.WINDOWSTATE_NORMAL;
            end

            check_connection(this);
            command = 'S_WindowState';
            send_line(this, command);
            send_int(this, windowstate);
            check_status(this);
        end

        function setFlagsRoboDK(this, flags)
            % Update the RoboDK flags. RoboDK flags allow defining how much access the user has to RoboDK features. Use a FLAG_ROBODK_* variables to set one or more flags.
            if nargin < 2
                flags = this.FLAG_ROBODK_ALL;
            end

            check_connection(this);
            command = 'S_RoboDK_Rights';
            send_line(this, command);
            send_int(this, flags);
            check_status(this);
        end

        function setFlagsItem(this, item, flags)
            % Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
            check_connection(this);

            if nargin < 3
                flags = this.FLAG_ITEM_ALL;
            end

            command = 'S_Item_Rights';
            send_line(this, command);
            send_item(this, item)
            send_int(this, flags)
            check_status(this);
        end

        function flags = getFlagsItem(this, item)
            % Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
            check_connection(this);
            command = 'G_Item_Rights';
            ssend_line(this, command)
            send_item(this, item)
            flags = rec_int(this);
            check_status(this);
        end

        function ShowMessage(this, message, popup)
            % Shows or raises the RoboDK window
            if (nargin < 3)
                popup = 1;
            end

            check_connection(this);

            if popup > 0
                command = 'ShowMessage';
                send_line(this, command);
                send_line(this, message);
                this.COM.Timeout = 3600; % wait up to 1 hour user to hit OK
                check_status(this);
                this.COM.Timeout = this.TIMEOUT;
            else
                command = 'ShowMessageStatus';
                send_line(this, command);
                send_line(this, message);
                check_status(this);
            end

        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function Copy(this, item, copy_childs)
            % Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste().
            % Example:  object = RL.Item('My Object');
            %           RL.Copy(object);
            %           newobject = RL.Paste();
            %           newobject.setName(newobject, 'My Object (copy 1)');
            %           newobject = Paste();
            %           newobject.setName(newobject, 'My Object (copy 2)');
            if nargin < 2
                item = RobolinkItem(this);
            end

            if nargin < 3
                copy_childs = 1;
            end

            check_connection(this);
            command = 'Copy2';
            send_line(this, command);
            send_item(this, item);
            send_int(this, copy_childs > 0);
            check_status(this);
        end

        function newitem = Paste(this, toparent)
            % Paste the copied item as a dependency of another item (same as Ctrl+V). Paste should be used after Copy(). It returns the newly created item.
            if nargin < 2
                toparent = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Paste';
            send_line(this, command);
            send_item(this, toparent);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddFile(this, filename, parent)
            % Loads a file and attaches it to parent. It can be any file supported by Robodk.
            % Timeout may have to be increased if big files are loaded.
            % In 1  : string -> absolute path of the file
            % In 2 (optional) : item -> parent to attach
            % Out 1 : item -> added item (0 if failed)
            check_connection(this);

            if nargin < 3
                parent = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Add';
            send_line(this, command);
            send_line(this, filename);
            send_item(this, parent);
            this.COM.Timeout = 3600;
            newitem = rec_item(this);
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end

        function newitem = AddShape(this, triangle_points, add_to, override_shapes)
            % Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
            if nargin < 3
                add_to = 0;
            end

            if nargin < 4
                override_shapes = 0;
            end

            check_connection(this);
            command = 'AddShape2';
            send_line(this, command);
            send_matrix(this, triangle_points);
            send_item(this, add_to);
            send_int(this, override_shapes > 0);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddCurve(this, curve_points, reference_object, add_to_ref, projection_type)
            % Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
            if nargin < 3
                reference_object = 0;
            end

            if nargin < 4
                add_to_ref = 0;
            end

            if nargin < 5
                projection_type = this.PROJECTION_ALONG_NORMAL_RECALC;
            end

            check_connection(this);
            command = 'AddWire';
            send_line(this, command);
            send_matrix(this, curve_points);
            send_item(this, reference_object);
            send_int(this, add_to_ref > 0);
            send_int(this, projection_type);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddPoints(this, points, reference_object, add_to_ref, projection_type)
            % Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
            if nargin < 3
                reference_object = 0;
            end

            if nargin < 4
                add_to_ref = 0;
            end

            if nargin < 5
                projection_type = this.PROJECTION_ALONG_NORMAL_RECALC;
            end

            check_connection(this);
            command = 'AddPoints';
            send_line(this, command);
            send_matrix(this, points);
            send_item(this, reference_object);
            send_int(this, add_to_ref > 0);
            send_int(this, projection_type);
            newitem = rec_item(this);
            check_status(this);
        end

        function projected_points = ProjectPoints(this, points, object_project, projection_type, timeout)
            % Project a point or a list of points given its coordinates.

            if nargin < 4
                projection_type = this.PROJECTION_ALONG_NORMAL_RECALC;
            end

            if nargin < 5
                timeout = 30;
            end

            check_connection(this);
            command = 'ProjectPoints';
            send_line(this, command);
            send_matrix(this, points);
            send_item(this, object_project);
            send_int(this, projection_type);
            this.COM.Timeout = timeout;
            projected_points = rec_matrix(this); % will wait here
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end

        function CloseStation(this)
            % Closes the current RoboDK station without suggesting to save
            check_connection(this);
            send_line(this, 'RemoveStn');
            check_status(this);
        end

        function Delete(this, item_list)
            % Remove a list of items.
            check_connection(this);
            command = 'RemoveLst';
            send_line(this, command);
            send_int(this, length(item_list));

            for itm = 1:lenght(item_list)
                send_item(this, item_list{itm});
                item_list{itm}.item = 0;
            end

            check_status(this);
        end

        function Save(this, filename, itemsave)
            % Save an item to a file. If no item is provided, the open station is saved.
            if nargin < 3
                itemsave = RobolinkItem();
            end

            check_connection(this);
            command = 'Save';
            send_line(this, command);
            send_line(this, filename);
            send_item(this, itemsave);
            this.COM.Timeout = 60;
            check_status(this);
            this.COM.Timeout = this.TIMEOUT;
        end

        function newitem = AddStation(this, name)
            % Add a new empty station. It returns the station :class:`.Item` created.
            if nargin < 2
                name = 'New Station';
            end

            check_connection(this);
            command = 'NewStation';
            send_line(this, command);
            send_line(this, name)
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddTarget(this, name, itemparent, itemrobot)
            % Adds a new target that can be reached with a robot.
            % In  1 : string -> name of the target
            % In  2 (optional) : item -> parent to attach to (such as a frame)
            % In  3 (optional) : item -> main robot that will be used to go to this target
            % Out 1 : item -> the new item created
            if nargin < 3
                itemparent = RobolinkItem(this);
            end

            if nargin < 4
                itemrobot = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Add_TARGET';
            send_line(this, command);
            send_line(this, name);
            send_item(this, itemparent);
            send_item(this, itemrobot);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddFrame(this, name, itemparent)
            % Adds a new Frame that can be referenced by a robot.
            % In  1 : string -> name of the frame
            % In  2 (optional) : item -> parent to attach to (such as the rrobot base frame)
            % Out 1 : item -> the new item created
            if nargin < 3
                itemparent = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Add_FRAME';
            send_line(this, command);
            send_line(this, name);
            send_item(this, itemparent);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddProgram(this, name, itemrobot)
            % Adds a new program.
            % In  1 : string -> name of the program
            % In  2 (optional) : item -> robot that will be used
            % Out 1 : item -> the new item created
            if nargin < 3
                itemrobot = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Add_PROG';
            send_line(this, command);
            send_line(this, name);
            send_item(this, itemrobot);
            newitem = rec_item(this);
            check_status(this);
        end

        function newitem = AddMachiningProject(this, name, itemrobot)
            % Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points.
            if nargin < 3
                itemrobot = RobolinkItem(this);
            end

            check_connection(this);
            command = 'Add_MACHINING';
            send_line(this, command);
            send_line(this, name);
            send_item(this, itemrobot);
            newitem = rec_item(this);
            check_status(this);
        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function prog_status = RunProgram(this, fcn_param)
            % Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific robot. If the program exists it will also run the program in simulate mode.
            % In  1 : fcn call -> string of the program to run
            % Out 1 : this function always returns 0
            prog_status = this.RunCode(fcn_param, 1);
        end

        function prog_status = RunCode(this, code, code_is_fcn_call)
            % Adds code to run in the program output. If the program exists it will also run the program in simulate mode.
            % In  1 : code -> string of the code or program to run
            % In  2 : code_is_fcn_call -> True if the code corresponds to a function call, if so, RoboDK will handle the syntax when the code is generated
            % Out 1 : this function alsways returns 0
            if nargin < 3
                code_is_fcn_call = 0;
            end

            check_connection(this);
            command = 'RunCode';
            send_line(this, command);
            send_int(this, code_is_fcn_call);
            send_line(this, strrep(strrep(code, '\r\n', '<<br>>'), '\n', '<<br>>'))
            prog_status = rec_int(this);
            check_status(this);
        end

        function prog_status = RunMessage(this, message, message_is_comment)
            % Shows a message or a comment in the robot program.
            % In  1 : string -> message or comment to show in the teach pendant
            % Out 1 : int -> if message_is_comment is set to True (or 1) the message will appear only as a comment in the code
            if nargin < 3
                message_is_comment = 0;
            end

            check_connection(this);
            command = 'RunMessage';
            send_line(this, command);
            send_int(this, message_is_comment);
            send_line(this, strrep(strrep(message, '\r\n', '<<br>>'), '\n', '<<br>>'))
            prog_status = rec_int(this);
            check_status(this);
        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function Render(this, always_render)
            % Renders the scene. This function turns off rendering unless always_render is set to true.
            if nargin < 2
                always_render = 0;
            end

            auto_render = int32(~always_render);
            check_connection(this);
            command = 'Render';
            send_line(this, command);
            send_int(this, auto_render);
            check_status(this);
        end

        function Update(this)
            % Update the screen. This updates the position of all robots and internal links according to previously set values.
            % This function is useful when Render is turned off (Example: "RDK.Render(False)"). Otherwise, by default RoboDK will update all links after any modification of the station (when robots or items are moved).
            if nargin < 2
                always_render = 0;
            end

            auto_render = int32(~always_render);
            check_connection(this);
            command = 'Refresh';
            send_line(this, command);
            send_int(this, 0);
            check_status(this);
        end

        function inside = IsInside(this, object_inside, object)
            % Return 1 (True) if object_inside is inside the object, otherwise, it returns 0 (False). Both objects must be of type :class:`.Item`
            check_connection(this);
            command = 'IsInside';
            send_line(this, command);
            send_item(this, object_inside);
            send_item(this, object);
            inside = rec_int(this);
            check_status(this);
        end

        function ncollisions = setCollisionActive(this, check_state)
            % Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects (:class:`.Item`). This allows altering the collision map for Collision checking.
            check_connection(this);
            command = 'Collision_SetState';
            send_line(this, command);
            send_int(this, check_state);
            ncollisions = rec_int(this);
            check_status(this);
        end

        function success = setCollisionActivePair(this, check_state, item1, item2, id1, id2)
            % Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects (:class:`.Item`).
            % This allows altering the collision map for Collision checking.
            % Specify the link id for robots or moving mechanisms (id 0 is the base)
            % Returns 1 if succeeded. Returns 0 if setting the pair failed (wrong id is provided)
            if nargin < 5
                id1 = 0;
            end

            if nargin < 6
                id2 = 0;
            end

            check_connection(this);
            command = 'Collision_SetPair';
            send_line(this, command);
            send_item(this, item1);
            send_item(this, item2);
            send_int(this, id1);
            send_int(this, id2);
            send_int(this, check_state);
            success = rec_int(this);
            check_status(this);
        end

        function ncollisions = Collisions(this)
            % Returns the number of pairs of objects that are currently in collision state.
            check_connection(this);
            command = 'Collisions';
            send_line(this, command);
            ncollisions = rec_int(this);
            check_status(this);
        end

        function ncollisions = Collision(this, item1, item2)
            % Returns 1 if item1 and item2 collided. Otherwise returns 0.
            check_connection(this);
            command = 'Collided';
            send_line(this, command);
            send_item(this, item1)
            send_item(this, item2)
            ncollisions = rec_int(this);
            check_status(this);
        end

        function item_list = CollisionItems(this)
            % Return the list of items that are in a collision state. This function can be used after calling Collisions() to retrieve the items that are in a collision state.
            check_connection(this);
            command = 'Collision_Items';
            send_line(this, command);
            nitems = rec_int(this);
            item_list = cell(1, nitems);

            for i = 1:nitems
                itemi = rec_item(this);
                item_list{i} = itemi;
                link_id = rec_int(this); % link id for robot items (ignored)
                collision_times = rec_int(this); % number of objects it is in collisions with
            end

            check_status(this);
        end

        function setSimulationSpeed(this, speed)
            % Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed.
            % A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.
            % The slowest speed ratio allowed is 0.001. Set a large simmulation ratio (>100) for fast simulation results.
            check_connection(this);
            command = 'SimulateSpeed';
            send_line(this, command);
            send_int(this, speed * 1000);
            check_status(this);
        end

        function speed = SimulationSpeed(this)
            % Return the simulation speed. A simulation speed of 1 means real-time simulation.
            % A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.
            check_connection(this);
            command = 'GetSimulateSpeed';
            send_line(this, command);
            speed = rec_int(this) / 1000.0;
            check_status(this);
        end

        function speed = SimulationTime(this)
            % Retrieve the simulation time (in seconds). Time of 0 seconds starts with the first time this function is called.
            % The simulation time changes depending on the simulation speed. The simulation time is usually faster than the real time (5 times by default).
            check_connection(this);
            command = 'GetSimTime';
            send_line(this, command);
            speed = rec_int(this) / 1000.0;
            check_status(this);
        end

        function setRunMode(this, run_mode)
            % Sets the behavior of the script. By default, robodk shows the path simulation for movement instructions (run_mode=1).
            % Setting the run_mode to 2 allows to perform a quick check to see if the path is feasible.
            % In   1 : int = RUNMODE
            % RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
            % RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
            % RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
            % RUNMODE_RUN_REAL=4        moves the real robot is it is connected
            if nargin < 2
                run_mode = 1;
            end

            check_connection(this);
            command = 'S_RunMode';
            send_line(this, command);
            send_int(this, run_mode);
            check_status(this);
        end

        function run_mode = RunMode(this)
            % Gets the behavior of the script. By default, robodk shows the path simulation for movement instructions (run_mode=1).
            % If run_mode = 2, the script is performing a quick check to see if the path is feasible (usually managed by the GUI).
            % If run_mode = 3, the script is generating the robot program (usually managed by the GUI).
            % Out  1 : int = RUNMODE
            % RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
            % RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
            % RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
            % RUNMODE_RUN_REAL=4        moves the real robot is it is connected
            check_connection(this);
            command = 'G_RunMode';
            send_line(this, command);
            run_mode = rec_int(this);
            check_status(this);
        end

        function params = getParams(this)
            % Get all the user parameters from the open RoboDK station.
            % Station parameters can also be modified manually by right clicking the station item and selecting "Station parameters"

            check_connection(this);
            command = 'G_Params';
            send_line(this, command);
            nparam = rec_int(this);
            params = cell(1, nparam);

            for i = 1:nparam
                param = rec_line(this);
                value = rec_line(this);
                params{i} = [param, value];
            end

            check_status(this);
        end

        function value = getParam(this, param)
            % Gets a global parameter from the RoboDK station.
            % In  1 : string = parameter
            % Out 1 : string = value
            % Available parameters:
            % PATH_OPENSTATION = folder path of the current .stn file
            % FILE_OPENSTATION = file path of the current .stn file
            % PATH_DESKTOP = folder path of the user's folder
            % PATH_LIBRARY = library path
            if nargin < 2
                param = 'PATH_OPENSTATION';
            end

            check_connection(this);
            command = 'G_Param';
            send_line(this, command);
            send_line(this, param);
            value = rec_line(this);
            check_status(this);
        end

        function setParam(this, param, value)
            % Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
            % The parameters can also be modified by right clicking the station and selecting "shared parameters"
            % In 1 : string = parameter
            % In 2 : string = value
            % Available parameters:
            % PATH_OPENSTATION = folder path of the current .stn file
            % FILE_OPENSTATION = file path of the current .stn file
            % PATH_DESKTOP = folder path of the user's folder
            % Other parameters can be added or modified by the user
            check_connection(this);
            command = 'S_Param';
            send_line(this, command);
            send_line(this, param);
            send_line(this, value);
            check_status(this);
        end

        function response = Command(this, cmd, value)
            % Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
            check_connection(this);
            command = 'SCMD';
            send_line(this, command);
            send_line(this, cmd);
            send_line(this, strrep(value, '\n', '<br>'));
            this.COM.Timeout = 3600; % wait up to 1 hour for user input
            response = rec_line(this);
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end

        function list_stn = getOpenStations(this)
            % Returns the list of open stations in RoboDK
            check_connection(this);
            command = 'G_AllStn';
            send_line(this, command);
            nstn = rec_int(this);
            list_stn = cell(1, nstn);

            for i = 1:nstn
                list_stn{i} = rec_item(this);
            end

            check_status(this);
        end

        function stn = ActiveStation(this)
            % Returns the active station item (station currently visible)
            check_connection(this);
            command = 'G_ActiveStn';
            send_line(this, command);
            stn = rec_item(this);
            check_status(this);
        end

        function setActiveStation(this, stn)
            % Set the active station (project currently visible)
            check_connection(this);
            command = 'S_ActiveStn';
            send_line(this, command);
            send_item(this, stn)
            check_status(this);
        end

        function ShowSequence(this, matrix, display_type, timeout)
            % Displays a sequence of joints
            % In  1 : joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix
            if nargin < 3
                display_type = this.SEQUENCE_DISPLAY_DEFAULT;
            end

            if nargin < 4
                timeout = -1;
            end

            RobolinkItem(this, 0).ShowSequence(matrix, display_type, timeout);
        end

        function xyz = LaserTracker_Measure(this, estimate, search)
            % Takes a laser tracker measurement with respect to the reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
            % Returns the XYZ coordinates of target if it was found. Othewise it retuns the vector [0;0;0].
            if nargin < 2
                estimate = [0; 0; 0];
            end

            if nargin < 3
                search = 0;
            end

            check_connection(this);
            command = 'MeasLT';
            send_line(this, command);
            send_xyz(this, estimate);
            send_int(this, search > 0);
            xyz = rec_xyz(this);
            check_status(this);
        end

        function [collision, itempicked, xyz] = Collision_Line(this, p1, p2, ref)
            % Checks the collision between a line and the station. The line is composed by 2 points.
            % In  1 : p1 -> start point of the line
            % In  2 : p2 -> end point of the line
            % In  3 : pose (optional) -> reference of the 2 points
            % Out 1 : collision -> True if there is a collision, False otherwise
            % Out 2 : item -> Item collided
            % Out 3 : point -> collision point (station reference)
            if nargin < 4
                ref = eye(4);
            end

            p1abs = ref * [p1(1:3); 1];
            p2abs = ref * [p2(1:3); 1];
            check_connection(this);
            command = 'CollisionLine';
            send_line(this, command);
            send_xyz(this, p1abs);
            send_xyz(this, p2abs);
            itempicked = rec_item(this);
            xyz = rec_xyz(this);
            collision = itempicked.Valid();
            check_status(this);
        end

        function setPoses(this, items, poses)
            % Sets the relative positions (poses) of a list of items with respect to their parent. For example, the position of an object/frame/target with respect to its parent.
            % Use this function instead of setPose() for faster speed.

            if isempty(items)
                return
            end

            check_connection(this);
            command = 'S_Hlocals';
            send_line(this, command);
            send_int(this, length(items));

            for i = 1:length(items)
                send_item(this, items{i});
                send_pose(this, poses{i});
            end

            check_status(this);
        end

        function setPosesAbs(this, items, poses)
            % Set the absolute positions (poses) of a list of items with respect to the station reference. For example, the position of an object/frame/target with respect to its parent.
            % Use this function instead of setPose() for faster speed.

            if isempty(items)
                return
            end

            check_connection(this);
            command = 'S_Hlocal_AbsS';
            send_line(this, command);
            send_int(this, length(items));

            for i = 0:length(items)
                send_item(this, items{i});
                send_pose(this, poses{i});
            end

            check_status(this);
        end

        function joints_list = Joints(this, robot_item_list)
            % Return the current joints of a list of robots.

            check_connection(this);
            command = 'G_ThetasList';
            send_line(this, command);
            nrobs = length(robot_item_list);
            send_int(this, nrobs);
            joints_list = cell(1, nrobs);

            for i = 1:nrobs
                send_item(this, robot_item_list{i})
                joints_i = rec_array(this);
                joints_list{i} = joints_i;
            end

            check_status(this);
        end

        function setJoints(this, robot_item_list, joints_list)
            % Sets the current robot joints for a list of robot items and a list joints.

            nrobs = length(robot_item_list);

            check_connection(this);
            command = 'S_ThetasList';
            send_line(this, command);
            send_int(this, nrobs);

            for i = 1:nrobs
                send_item(this, robot_item_list{i});
                send_array(this, joints_list{i});
            end

            check_status(this);
        end

        function errors = ProgramStart(this, programname, folder, postprocessor, robot)
            % Defines the name of the program when the program is generated (offline programming).
            % It is also possible to specify the name of the post processor as well as the folder to save the program.
            % This method must be called before any program output is generated (before any robot movement or other instruction).
            if nargin < 3
                folder = '';
            end

            if nargin < 4
                postprocessor = '';
            end

            if nargin < 5
                robot = 0;
            end

            check_connection(this);
            command = 'ProgramStart';
            send_line(this, command);
            send_line(this, programname);
            send_line(this, folder);
            send_line(this, postprocessor);

            if robot
                send_item(this, RobolinkItem());
            else
                send_item(this, robot);
            end

            errors = rec_int(this);
            check_status(this);
        end

        function setViewPose(this, pose)
            % Set the pose of the world reference frame with respect to the view (camera/screen)
            check_connection(this);
            command = 'S_ViewPose';
            send_line(this, command);
            send_pose(this, pose);
            check_status(this);
        end

        function pose = ViewPose(this)
            % Get the pose of the world reference frame with respect to the view (camera/screen)%
            check_connection(this);
            command = 'G_ViewPose';
            send_line(this, command);
            pose = rec_pose(this);
            check_status(this);
        end

        %------------------------------------------------------------------
        %----------------------- CAMERA VIEWS ----------------------------
        function cam_h = Cam2D_Add(this, item_object, cam_params, camera_as_item)
            % Adds a 2D camera view
            % In  1: Parameters of the camera
            % Out 1: camera handle pointer
            if nargin < 3
                cam_params = '';
                camera_as_item = true;
            elseif nargin < 4
                camera_as_item = true;
            end

            if camera_as_item
                check_connection(this);
                command = 'Cam2D_PtrAdd';
                send_line(this, command);
                send_item(this, item_object);
                send_line(this, cam_params);
                cam_h = rec_item(this);
                check_status(this);
            else
                check_connection(this);
                command = 'Cam2D_Add';
                send_line(this, command);
                send_item(this, item_object);
                send_line(this, cam_params);
                cam_h = rec_ptr(this);
                check_status(this);
            end

        end

        function success = Cam2D_Snapshot(this, file_save_img, cam_h, params)
            % Returns the current joints of a list of robots.
            % In  1 : Parameters of the camera
            % Out 1 : 0 if snapshot failed or 1 if succeeded

            if nargin < 2
                file_save_img = "";
            end

            if nargin < 3
                cam_h = 0;
            end

            if nargin < 4
                params = "";
            end

            check_connection(this);

            if isa(cam_h, 'numeric')
                command = 'Cam2D_Snapshot';
                send_line(this, command);
                send_ptr(this, cam_h);
                send_line(this, file_save_img);
                success = rec_int(this);

            else
                command = 'Cam2D_PtrSnapshot';
                send_line(this, command);
                send_item(this, cam_h);
                send_line(this, file_save_img);
                send_line(this, params);
                this.COM.Timeout = 3600;

                if isempty(file_save_img)
                    % If the file name is empty we are expecting a byte array as PNG file
                    success = rec_double(this);
                else
                    success = rec_int(this);
                end

                this.COM.Timeout = this.TIMEOUT;
            end

            check_status(this);
        end

        function success = Cam2D_Close(this, cam_h)
            % Returns the current joints of a list of robots.
            % In  1 : Parameters of the camera
            % Out 1 : 0 if snapshot failed or 1 if succeeded
            if nargin < 2
                cam_h = 0;
            end

            check_connection(this);

            if isa(cam_h, 'numeric')

                if cam_h == 0
                    command = 'Cam2D_CloseAll';
                    send_line(this, command);
                else
                    command = 'Cam2D_Close';
                    send_line(this, command);
                    send_ptr(this, cam_handle);
                end

            else
                command = 'Cam2D_PtrClose';
                send_line(this, command);
                send_item(this, cam_handle);
            end

            success = rec_int(this) > 0;
            check_status(this);
        end

        function success = Cam2D_SetParams(this, params, cam_handle)
            % Set the parameters of the simulated camera.

            if nargsin < 3
                cam_handle = 0;
            end

            check_connection(this);

            if isa(cam_handle, 'numeric')
                command = 'Cam2D_SetParams';
                send_line(this, command);
                send_ptr(cam_handle);
                send_line(this, params);
                success = rec_int(this);
            else
                command = 'Cam2D_PtrSetParams';
                send_line(this, command);
                send_item(this, cam_handle);
                send_line(this, params);
                success = rec_int(this);
            end

            check_status(this);
        end

        %------------------------------------------------------------------
        %----------------------- SPRAY GUN SIMULATION ----------------------------
        function id_spray = Spray_Add(this, item_tool, item_object, params, points, geometry)
            % Add a simulated spray gun that allows projecting particles to a part. This is useful to simulate applications such as:
            % arc welding, spot welding, 3D printing, painting, inspection or robot machining to verify the trace.
            %
            % The scripts ArcStart, ArcEnd and WeldOn and SpindleOn behave in a similar way, the only difference is the default behavior
            % This behavior simmulates Fanuc Arc Welding and triggers appropriate output when using the customized post processor.
            %
            % Select ESC to clear the trace manually.

            if nargin < 2
                item_tool = 0;
            end

            if nargin < 3
                item_object = 0;
            end

            if nargin < 4
                params = "";
            end

            if nargin < 5
                points = 0;
            end

            if nargin < 6
                geometry = 0;
            end

            check_connection(this);
            command = 'Gun_Add';
            send_line(this, command);
            send_item(this, item_tool);
            send_item(this, item_object);
            send_line(this, params);
            send_matrix(this, points);
            send_matrix(this, geometry);
            id_spray = rec_int(this);
            check_status(this);
        end

        function success = Spray_SetState(this, state, id_spray)
            % Sets the state of a simulated spray gun (ON or OFF)
            if nargin < 2
                state = this.SPRAY_ON;
            end

            if nargin < 3
                id_spray = -1;
            end

            check_connection(this);
            command = 'Gun_SetState';
            send_line(this, command);
            send_int(this, id_spray);
            send_int(this, state);
            success = rec_int(this);
            check_status(this);
        end

        function [info, data] = Spray_GetStats(this, id_spray)
            % Gets statistics from all simulated spray guns or a specific spray gun.
            if nargin < 2
                id_spray = -1;
            end

            check_connection(this);
            command = 'Gun_Stats';
            send_line(this, command);
            send_int(this, id_spray);
            info = rec_line(this);
            info = strrep(info, '<br>', '\t');
            data = rec_matrix(this);
            check_status(this);
        end

        function success = Spray_Clear(this, id_spray)
            % Stops simulating a spray gun. This will clear the simulated particles.
            if nargin < 2
                id_spray = -1;
            end

            check_connection(this);
            command = 'Gun_Clear';
            send_line(this, command);
            send_int(this, id_spray);
            success = rec_int(this);
            check_status(this);
        end

        function [lic_name, lic_cid] = License(this)
            % Get the license string
            check_connection(this);
            command = 'G_License2';
            send_line(this, command);
            lic_name = rec_line(this);
            lic_cid = rec_line(this);
            check_status(this);
        end

        function item_list = Selection(this)
            % Return the list of currently selected items

            check_connection(this);
            command = 'G_Selection';
            send_line(this, command);
            nitems = rec_int(this);
            item_list = cell(1, nitems);

            for i = 1:nitems
                item_list{i} = rec_item(this);
            end

            check_status(this);
        end

        function setSelection(this, list_items)
            % Set the selection in the tree

            check_connection(this);
            command = 'S_Selection';
            send_line(this, command);
            send_int(this, length(list_items))

            for i = 1:length(list_items)
                send_item(this, list_items{i})
            end

            check_status(this);
        end

        function newitem = MergeItems(this, list_items)
            % Merge multiple object items as one. Source objects are not deleted and a new object is created.

            check_connection(this);
            command = 'MergeItems';
            send_line(this, command);
            send_int(this, length(list_items))

            for i = 1:length(list_items)
                send_item(this, list_items{i})
            end

            newitem = rec_item(this);
            check_status(this);
        end

        function [object, feature_type, feature_id, feature_name, points] = GetPoints(this, feature_type)
            % Retrieves the object under the mouse cursor.
            if nargin < 2
                feature_type = this.FEATURE_HOVER_OBJECT_MESH;
            end

            check_connection(this);
            command = 'G_ObjPoint';
            send_line(this, command);
            send_item(this, RobolinkItem());
            send_int(this, feature_type);
            feature_id = 0; % not used here
            send_int(this, feature_id);
            points = [];

            if feature_type == this.FEATURE_HOVER_OBJECT_MESH;
                points = rec_matrix(this);
            end

            object = rec_item(this);
            is_frame = rec_int(this) > 0;
            feature_type = rec_int(this);
            feature_id = rec_int(this);
            feature_name = rec_line(this);
            check_status(this);
        end

    end

end
