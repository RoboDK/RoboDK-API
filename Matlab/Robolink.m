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
% In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
%
% More information about the RoboDK API for Python here:
%     https://robodk.com/doc/en/RoboDK-API.html
%     https://robodk.com/doc/en/PythonAPI/index.html
%
% More information about RoboDK post processors here:
%     https://robodk.com/help%PostProcessor
%
% Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
%     http://www.j3d.org/matrix_faq/matrfaq_latest.html
%
% --------------------------------------------

classdef Robolink < handle
% This class allows to create macros for RoboDK.
% Any interaction is made through "items". An item is an object in the
% Robodk tree (it can be either a robot, an object, a tool, a frame, a 
% program, ...).
% An item is a unique number (pointer) that represents one object.
%
% RoboDK api Help:
% ->Type "doc Robolink"            for more help on the Robolink class
% ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
% ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes
    properties (Constant)
        % Tree item types
        ITEM_TYPE_STATION=1;
        ITEM_TYPE_ROBOT=2;
        ITEM_TYPE_FRAME=3;
        ITEM_TYPE_TOOL=4;
        ITEM_TYPE_OBJECT=5;
        ITEM_TYPE_TARGET=6;
        ITEM_TYPE_PROGRAM=8;
        ITEM_TYPE_INSTRUCTION=9
        ITEM_TYPE_PROGRAM_PYTHON=10;
        ITEM_TYPE_MACHINING=11;
        ITEM_TYPE_BALLBARVALIDATION=12;
        ITEM_TYPE_CALIBPROJECT=13;
        ITEM_TYPE_VALID_ISO9283=14;

        % Move types
        MOVE_TYPE_INVALID = -1;
        MOVE_TYPE_JOINT = 1;
        MOVE_TYPE_LINEAR = 2;
        MOVE_TYPE_CIRCULAR = 3;
        
        
        % Station parameters request
        PATH_OPENSTATION = 'PATH_OPENSTATION';
        FILE_OPENSTATION = 'FILE_OPENSTATION';
        PATH_DESKTOP = 'PATH_DESKTOP';

        % Script execution types
        RUNMODE_SIMULATE=1;                      % performs the simulation moving the robot (default)
        RUNMODE_QUICKVALIDATE=2;                 % performs a quick check to validate the robot movements
        RUNMODE_MAKE_ROBOTPROG=3;                % makes the robot program
        RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD=4;     % makes the robot program and updates it to the robot
        RUNMODE_MAKE_ROBOTPROG_AND_START=5;      % makes the robot program and starts it on the robot (independently from the PC)
        RUNMODE_RUN_ROBOT=6;                     % moves the real robot from the PC (PC is the client, the robot behaves like a server)

        % Program execution type
        PROGRAM_RUN_ON_SIMULATOR=1;  % Set the program to run on the simulator
        PROGRAM_RUN_ON_ROBOT=2;      % Set the program to run on the robot
        
        % Robot connection status
        ROBOTCOM_PROBLEMS       = -3;
        ROBOTCOM_DISCONNECTED   = -2;
        ROBOTCOM_NOT_CONNECTED  = -1;
        ROBOTCOM_READY          = 0;
        ROBOTCOM_WORKING        = 1;
        ROBOTCOM_WAITING        = 2;
        ROBOTCOM_UNKNOWN        = -1000;

        % TCP calibration types
        CALIBRATE_TCP_BY_POINT = 0;
        CALIBRATE_TCP_BY_PLANE = 1;

        % projection types (for AddCurve)
        PROJECTION_NONE                = 0; % No curve projection
        PROJECTION_CLOSEST             = 1; % The projection will the closest point on the surface
        PROJECTION_ALONG_NORMAL        = 2; % The projection will be done along the normal.
        PROJECTION_ALONG_NORMAL_RECALC = 3; % The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.

        % Euler type
        EULER_RX_RYp_RZpp = 0; % generic
        EULER_RZ_RYp_RXpp = 1; % ABB RobotStudio
        EULER_RZ_RYp_RZpp = 2; % Kawasaki, Adept, Staubli
        EULER_RZ_RXp_RZpp = 3; % CATIA, SolidWorks
        EULER_RX_RY_RZ    = 4; % Fanuc, Kuka, Motoman, Nachi
        EULER_RZ_RY_RX    = 5; % CRS
        EULER_QUEATERNION = 6; % ABB Rapid
        
        % Collision checking state
        COLLISION_OFF = 0 % Collision checking turned Off
        COLLISION_ON = 1 % Collision checking turned On
        
        % Other public variables
        TIMEOUT = 5;     % timeout for communication, in seconds
    end
    properties
        APPLICATION_DIR = 'C:\RoboDK\bin\RoboDK.exe'; % file path to the Robodk program (executable)
        COM = 0;         % tcpip com
    end
    properties(GetAccess = 'private', SetAccess = 'private')
        SAFE_MODE = 1;   % checks that provided items exist in memory
        AUTO_UPDATE = 0; % if AUTO_UPDATE is zero, the scene is rendered after every function call
        PORT_START = 20500; % port to start looking for app connection
        PORT_END   = 20500; % port to stop looking for app connection
        PORT = -1;
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
    methods % (Access = 'private')
        function connected = is_connected(this)
            % This is a private function. 
            % Returns 1 if connection is valid, returns 0 if connection is invalid
%             if strcmp(this.COM,'tcpclient') ~= 0
%                 connected = 0;
%                 return
%             end
%             status = get(this.COM,'status');
%             if status(1) == 'o'
%                 connected = 1;
%             end
            connected = 1;
        end
        function check_connection(this)
            % This is a private function. 
            % If we are not connected it will attempt a connection, if it fails, it will throw an error
            if ~is_connected(this) && Connect(this) ~= 1
                error('Unable to connect');
            end
%             flushinput(this.COM);%Clear anything still in the input buffer from the previous commands                
%             flushoutput(this.COM);%Remove data from output buffer.
        end
        function status = check_status(this)
            % This is a private function. 
            % this function checks the status of the connection
            lastwarn(''); % makes timeout warning an error
%             status = read(this.COM, 1, 'int32');
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
                        strproblems = 'Invalid item: The item identifier provided is not valid or it does not exist.';
                    case 2
                        strproblems = rec_line(this);
                        warning(strproblems);
                        status = 0;
                        return
                        %error(strproblems);
                        %status = -1;
                        %return
                    case 3
                        strproblems = rec_line(this);
                    case 9
                        strproblems = 'Invalid license. Contact us at: www.robodk.org';
                    otherwise
                        % do nothing
                end
                fprintf([strproblems,'\n']);
                error(strproblems);
            elseif status < 100
                strproblems = rec_line(this);
                fprintf([strproblems,'\n']);
                error(strproblems);
            else
                disp(status)
                error('connection problems');
%                 fclose(this.COM);% reconnect to reset connection                
%                 fopen(this.COM);
%                 validate_connection(this);
            end
        end
        function send_line(this, string)
            % This is a private function. 
            % Sends a string of characters with a \n
%             fprintf(this.COM, string);
            write(this.COM, uint8([string, char(10)]));
        end
        function string = rec_line(this)
            % This is a private function. 
            % Receives a string. It reads until if finds \n
            string = [];
%             chari = fread(this.COM, 1, 'char');
            chari = read(this.COM, 1, 'uint8');
            while chari ~= 10 %LF
                string = [string, chari];
%                 chari = fread(this.COM, 1, 'char');
                chari = read(this.COM, 1, 'uint8');
            end
            string = char(string);
        end        
        function send_item(this, item)
            % This is a private function. 
            % Sends an item pointer
%             fwrite(this.COM, item.item(1), 'float64'); 
            write(this.COM, uint64(item.item(1))); 
        end
        function item = rec_item(this)
            % This is a private function. 
            % Receives an item pointer
            itemnum = read(this.COM, 1, 'uint64');
            itemtype = rec_int(this);%read(this.COM, 1, 'int32');
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
%         function send_double(this, num)
%             % This is a private function. 
%             % Sends an int (32 bits)
%             if numel(num) > 1
%                 num = num(1);
%             end
%             bytes = typecast(double(num), 'uint8');
%             write(this.COM, flip(bytes)); 
%         end
        function bytes = bytes_double(this, num)
            % This is a private function. 
            % Sends an int (32 bits)
            bytes = flip(typecast(double(num), 'uint8'));
        end
        function num = rec_double(this)
            % This is a private function. 
            % Receives an int (32 bits)
%             num = read(this.COM, 1, 'int32'); % typecast(flip(typecast(int32(100663296), 'uint8')), 'int32')
            bytes = read(this.COM, 8, 'uint8');
            num = typecast(flip(bytes), 'double');
        end
        function send_pose(this, pose)
            % This is a private function. 
            % Sends a pose (4x4 matrix)
%             write(this.COM, pose(1:16), 'double');
%             write(this.COM, double(pose(1:16)));
%             bytes = typecast(double(pose(1:16)), 'uint8');
%             write(this.COM, flip(bytes));
            size1 = size(pose,1);
            size2 = size(pose,2);
            if size1 ~= 4 || size2 ~= 4
                disp(pose);
                error('Invalid pose');
            end
            bytes = [];
            for j=1:4
                for i=1:4
%                     write(this.COM,mat(i,j),'float64');
%                     write(this.COM,double(mat(i,j)));
                    bytes = [bytes, bytes_double(this,pose(i,j))];
                end
            end
            write(this.COM, bytes); 
        end
        function pose = rec_pose(this)
            % This is a private function. 
            % Receives a pose (4x4 matrix)
%             pose = read(this.COM, 16, 'double');
%             bytes = read(this.COM, 16*8, 'uint8');            
%             pose = reshape(pose,4,4);
            pose = eye(4);
            for j=1:4
                for i=1:4
%                     write(this.COM,mat(i,j),'float64');
%                     write(this.COM,double(mat(i,j)));
                    pose(i,j) = rec_double(this);
                end
            end
        end
        function send_xyz(this, pos)
            % This is a private function. 
            % Sends an xyz vector
%             write(this.COM, double(pos(1:3), 'double');
%             write(this.COM, double(pos(1:3)));
            bytes = [];
            for i=1:3
                bytes = [bytes, bytes_double(this,pos(i))];
            end
            write(this.COM, bytes); 
        end
        function pos = rec_xyz(this)
            % This is a private function. 
            % Receives an xyz vector (3x1 matrix)
%             pos = read(this.COM, 3, 'double');
%             pos = reshape(pos,3,1);
            pos = [];
            for i=1:3
                pos = [pos, rec_double(this)];
            end
        end        
        function send_int(this, num)
            % This is a private function. 
            % Sends an int (32 bits)
            if numel(num) > 1
                num = num(1);
            end
%             write(this.COM, num, 'int32'); 
%             write(this.COM, int32(num)); 
            bytes = typecast(int32(num), 'uint8');
            write(this.COM, flip(bytes)); 
        end
        function num = rec_int(this)
            % This is a private function. 
            % Receives an int (32 bits)
%             num = read(this.COM, 1, 'int32'); % typecast(flip(typecast(int32(100663296), 'uint8')), 'int32')
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
            for i=1:nval
                bytes = [bytes, bytes_double(this,values(i))];
            end
            write(this.COM, bytes); 
        end
        function values = rec_array(this)
            % This is a private function. 
            % Receives an array of doubles
            nvalues = rec_int(this);
            values = [];
            for i=1:nvalues
                values = [values, rec_double(this)];
            end
        end
        function send_matrix(this, mat)
            % This is a private function. 
            % Sends a 2 dimensional matrix (nxm)
            size1 = size(mat,1);
            size2 = size(mat,2);
            send_int(this,size1);
            send_int(this,size2);
            bytes = [];
            for j=1:size2
                for i=1:size1
%                     write(this.COM,mat(i,j),'float64');
%                     write(this.COM,double(mat(i,j)));
                    bytes = [bytes, bytes_double(this,mat(i,j))];
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
            for j=1:size2
                for i=1:size1
                    mat(i,j) = rec_double(this);
                end
            end
%             if size1*size2 > 0
%                 mat = read(this.COM, size1*size2, 'double');
%                 mat = reshape(mat, size2, size1)';
%             else
%                 mat = [];
%             end            
        end
        function moveX(this, target, itemrobot, movetype, blocking)
            % This is a private function. 
            % Performs a linear or joint movement. Use MoveJ or MoveL instead.
            if nargin < 5
                blocking = 300;
            end
            %check_connection(this);
            itemrobot.WaitMove();% checks connection
            command = 'MoveX';
            send_line(this, command);
            send_int(this, movetype);
            if numel(target) == 1 % target is an item
                send_int(this,3);
                send_array(this,[]);
                send_item(this,target);
            elseif size(target,1) == 1 || size(target,2) == 1 % target are joints
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
                itemrobot.WaitMove();
            end
        end
        function moveC(this, target1, target2, itemrobot, blocking)
            % Performs a circular movement. Use robot.MoveC instead
            % self._check_connection();
            itemrobot.WaitMove(); % checks connection
            command = 'MoveC';
            send_line(this, command);
            send_int(this, 3);
            if numel(target1) == 1 % target1 is an item
                send_int(this, 3);
                send_array(this, []);
                send_item(this, target1);
            elseif size(target1,1) == 1 || size(target1,2) == 1 % target1 are joints
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
            elseif size(target2,1) == 1 || size(target2,2) == 1 % target2 are joints
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
                itemrobot.WaitMove();
            end
        end        
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
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
%             fprintf(this.COM, 'CMD_START'); % appends LF (char(10))
%             fprintf(this.COM, sprintf('%i %i', this.SAFE_MODE, this.AUTO_UPDATE));% appends LF
            write(this.COM, uint8(['CMD_START', char(10)]));
            write(this.COM, uint8([sprintf('%i %i', this.SAFE_MODE, this.AUTO_UPDATE), char(10)]));% appends LF
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
            for i=1:2
                for port=this.PORT_START:this.PORT_END
%                     this.COM = tcpip('localhost', port, 'Timeout', this.TIMEOUT, 'BytesAvailableFcnMode', 'byte', 'InputBufferSize', 4000); 
                    try
                        this.COM = tcpclient('localhost', port, 'Timeout', this.TIMEOUT); 
%                         fopen(this.COM); % only for tcpip object
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
                        error(['application path is not correct or could not start: ',this.APPLICATION_DIR]);
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
            item = rec_item(this);        %     item = fread(com, 2, 'ulong');% ulong is 32 bits!!!
            check_status(this);
        end     
        function list = ItemList(this, filter)
            % Returns a list of names of all available items in the currently open station in Robodk.
            check_connection(this);
            if nargin < 2
                filter = -1;                
            end
            if filter < 0
                command = 'G_List_Items';
                this.send_line(command);
            else
                command = 'G_List_Items_Type';
                this.send_line(command);
                this.send_int(filter);
            end
            count = rec_int(this);
            list = cell(1,count);
            for i=1:count
                namei = rec_line(this);
%                 fprintf('%i\t->\t%s\n',i,namei);
                list{i} = namei;
            end
            check_status(this);
        end
                
        
        function item = ItemUserPick(this, message, itemtype)
            % Shows a RoboDK popup to select one object from the open station.
            %An item type can be specified to filter desired items. If no type is specified, all items are selectable.
            %(check variables ITEM_TYPE_*)
            %Example:
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
            % Shows or raises the RoboDK window
            check_connection(this);
            command = 'HIDE';
            send_line(this, command);
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
        function Copy(this, item)
            % Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste_Item().
            % In 1 : item (optional) -> Parent item
            % Example:  object = RL.Item('My Object');
            %           RL.Copy(object);
            %           newobject = RL.Paste();
            %           newobject.setName(newobject, 'My Object (copy 1)');
            %           newobject = Paste();
            %           newobject.setName(newobject, 'My Object (copy 2)');
            if nargin < 2
                item = RobolinkItem(this);
            end
            check_connection(this);
            command = 'Copy';
            send_line(this, command);
            send_item(this, item);
            check_status(this);
        end
        function newitem = Paste(this, toparent)
            % Pastes the copied item (same as Ctrl+V). Needs to be used after Copy_Item(). See Copy() for an example.
            % In 1 : item
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
            command = 'Add';
            send_line(this, command);
            send_line(this, filename);
            send_item(this, parent);
            this.COM.Timeout = 3600;
            newitem = rec_item(this);
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
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
            % Out 1 : this function always returns 0"""
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
            send_line(this, strrep(strrep(code,'\r\n','<<br>>'),'\n','<<br>>'))
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
            send_line(this, strrep(strrep(message,'\r\n','<<br>>'),'\n','<<br>>'))
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
            % Return 1 (True) if object_inside is inside the object, otherwise, it returns 0 (False). Both objects must be of type :class:`.Item`"""
            check_connection(this);
            command = 'IsInside';
            send_line(this, command);
            send_item(this, object_inside);
            send_item(this, object);
            inside = rec_int(self);
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
        
        function setSimulationSpeed(this, speed)
            % Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed.
            check_connection(this);
            command = 'SimulateSpeed';
            send_line(this, command);
            send_int(this, speed*1000);
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
            send_line(this, strrep(value, '\n','<br>'));
            this.COM.Timeout = 3600; % wait up to 1 hour for user input
            response = rec_line(this);
            this.COM.Timeout = this.TIMEOUT;
            check_status(this);
        end        
        function ShowSequence(this, matrix)
            % Displays a sequence of joints
            % In  1 : joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix
            RobolinkItem(this, 0).ShowSequence(matrix);
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
            send_int(this, search);
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
            p1abs = ref*[p1(1:3);1];
            p2abs = ref*[p2(1:3);1];            
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
        
        function cam_h = Cam2D_Add(this, item_object, cam_params)
            % Adds a 2D camera view
            % In  1: Parameters of the camera
            % Out 1: camera handle pointer
            if nargin < 3
                cam_params = '';
            end
            check_connection(this);
            command = 'Cam2D_Add';
            send_line(this, command);
            send_item(this, item_object);
            send_line(this, cam_params);
            cam_h = rec_ptr(this);
            check_status(this);
        end
        
        function success = Cam2D_Snapshot(this, file_save_img, cam_h)
            % Returns the current joints of a list of robots.
            % In  1 : Parameters of the camera 
            % Out 1 : 0 if snapshot failed or 1 if succeeded
            if nargin < 3
                cam_h = 0;
            end
            check_connection(this);
            command = 'Cam2D_Snapshot';
            send_line(this, command);
            send_ptr(this, cam_h);
            send_line(this, file_save_img);     
            success = rec_int(this);
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
            if cam_h == 0
                command = 'Cam2D_CloseAll';
                send_line(this, command);
            else
                command = 'Cam2D_Close';
                send_line(this, command);
                send_ptr(this, cam_handle);
            end
            success = self.rec_int(this);
            check_status(this);
        end        
   end
end