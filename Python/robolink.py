# Copyright 2015 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --------------------------------------------
# --------------- DESCRIPTION ----------------
# This file defines the following two classes:
#     Robolink()
#     Item()
# These classes are the objects used to interact with RoboDK and create macros.
# An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
# Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method) 
#
# In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information about RoboDK post processors here:
#     https://robodk.com/help#PostProcessor
#
# Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
#     http://www.j3d.org/matrix_faq/matrfaq_latest.html
#
# --------------------------------------------


import struct
from robodk import *
from warnings import warn
import sys  # Only used to detect python version using sys.version_info

# Tree item types
ITEM_TYPE_STATION=1
ITEM_TYPE_ROBOT=2
ITEM_TYPE_FRAME=3
ITEM_TYPE_TOOL=4
ITEM_TYPE_OBJECT=5
ITEM_TYPE_TARGET=6
ITEM_TYPE_PROGRAM=8
ITEM_TYPE_INSTRUCTION=9
ITEM_TYPE_PROGRAM_PYTHON=10
ITEM_TYPE_MACHINING=11
ITEM_TYPE_BALLBARVALIDATION=12
ITEM_TYPE_CALIBPROJECT=13
ITEM_TYPE_VALID_ISO9283=14

# Instruction types
INS_TYPE_INVALID = -1
INS_TYPE_MOVE = 0
INS_TYPE_MOVEC = 1
INS_TYPE_CHANGESPEED = 2
INS_TYPE_CHANGEFRAME = 3
INS_TYPE_CHANGETOOL = 4
INS_TYPE_CHANGEROBOT = 5
INS_TYPE_PAUSE = 6
INS_TYPE_EVENT = 7
INS_TYPE_CODE = 8
INS_TYPE_PRINT = 9

# Move types
MOVE_TYPE_INVALID = -1
MOVE_TYPE_JOINT = 1
MOVE_TYPE_LINEAR = 2
MOVE_TYPE_CIRCULAR = 3
MOVE_TYPE_LINEARSEARCH = 4 # Such as ABB's SearchL function


# Station parameters request
PATH_OPENSTATION = 'PATH_OPENSTATION'
FILE_OPENSTATION = 'FILE_OPENSTATION'
PATH_DESKTOP = 'PATH_DESKTOP'

# Script execution types
RUNMODE_SIMULATE=1                      # performs the simulation moving the robot (default)
RUNMODE_QUICKVALIDATE=2                 # performs a quick check to validate the robot movements
RUNMODE_MAKE_ROBOTPROG=3                # makes the robot program
RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD=4     # makes the robot program and updates it to the robot
RUNMODE_MAKE_ROBOTPROG_AND_START=5      # makes the robot program and starts it on the robot (independently from the PC)
RUNMODE_RUN_ROBOT=6                     # moves the real robot from the PC (PC is the client, the robot behaves like a server)

# Program execution type
PROGRAM_RUN_ON_SIMULATOR=1  # Set the program to run on the simulator
PROGRAM_RUN_ON_ROBOT=2      # Set the program to run on the robot

# Robot connection status
ROBOTCOM_PROBLEMS       = -3
ROBOTCOM_DISCONNECTED   = -2
ROBOTCOM_NOT_CONNECTED  = -1
ROBOTCOM_READY          = 0
ROBOTCOM_WORKING        = 1
ROBOTCOM_WAITING        = 2
ROBOTCOM_UNKNOWN        = -1000

# TCP calibration methods
CALIBRATE_TCP_BY_POINT = 0
CALIBRATE_TCP_BY_PLANE = 1
# Reference frame calibration methods 
CALIBRATE_FRAME_3P_P1_ON_X = 0 # Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
CALIBRATE_FRAME_3P_P1_ORIGIN = 1 # Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
CALIBRATE_FRAME_6P = 2 # Calibrate by 6 points
CALIBRATE_TURNTABLE = 3 # Calibrate turntable


# projection types (for AddCurve)
PROJECTION_NONE                = 0 # No curve projection
PROJECTION_CLOSEST             = 1 # The projection will the closest point on the surface
PROJECTION_ALONG_NORMAL        = 2 # The projection will be done along the normal.
PROJECTION_ALONG_NORMAL_RECALC = 3 # The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.

# Euler type
JOINT_FORMAT = -1 # Using joints (not poses)
EULER_RX_RYp_RZpp = 0 # generic
EULER_RZ_RYp_RXpp = 1 # ABB RobotStudio
EULER_RZ_RYp_RZpp = 2 # Kawasaki, Adept, Staubli
EULER_RZ_RXp_RZpp = 3 # CATIA, SolidWorks
EULER_RX_RY_RZ    = 4 # Fanuc, Kuka, Motoman, Nachi
EULER_RZ_RY_RX    = 5 # CRS
EULER_QUEATERNION = 6 # ABB Rapid

# State of the RoboDK window
WINDOWSTATE_HIDDEN      = -1
WINDOWSTATE_SHOW        = 0
WINDOWSTATE_MINIMIZED   = 1
WINDOWSTATE_NORMAL      = 2
WINDOWSTATE_MAXIMIZED   = 3
WINDOWSTATE_FULLSCREEN  = 4
WINDOWSTATE_CINEMA      = 5
WINDOWSTATE_FULLSCREEN_CINEMA= 6

# Instruction program call type:
INSTRUCTION_CALL_PROGRAM = 0
INSTRUCTION_INSERT_CODE = 1
INSTRUCTION_START_THREAD = 2
INSTRUCTION_COMMENT = 3

# Object selection features
FEATURE_NONE=0
FEATURE_SURFACE=1
FEATURE_CURVE=2
FEATURE_POINT=3

# Spray gun simulation:
SPRAY_OFF = 0
SPRAY_ON = 1

# Collision checking state
COLLISION_OFF = 0
COLLISION_ON = 1

# RoboDK Window Flags
FLAG_ROBODK_TREE_ACTIVE = 1
FLAG_ROBODK_3DVIEW_ACTIVE = 2
FLAG_ROBODK_LEFT_CLICK = 4
FLAG_ROBODK_RIGHT_CLICK = 8
FLAG_ROBODK_DOUBLE_CLICK = 16
FLAG_ROBODK_MENU_ACTIVE = 32
FLAG_ROBODK_MENUFILE_ACTIVE = 64
FLAG_ROBODK_MENUEDIT_ACTIVE = 128
FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256
FLAG_ROBODK_MENUTOOLS_ACTIVE = 512
FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024
FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048
FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096
FLAG_ROBODK_TREE_VISIBLE = 8192
FLAG_ROBODK_REFERENCES_VISIBLE = 16384
FLAG_ROBODK_NONE = 0x00
FLAG_ROBODK_ALL = 0xFFFF
FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE

# RoboDK Item Flags
FLAG_ITEM_SELECTABLE = 1
FLAG_ITEM_EDITABLE = 2
FLAG_ITEM_DRAGALLOWED = 4
FLAG_ITEM_DROPALLOWED = 8
FLAG_ITEM_ENABLED = 32
FLAG_ITEM_AUTOTRISTATE = 64
FLAG_ITEM_NOCHILDREN = 128
FLAG_ITEM_USERTRISTATE = 256
FLAG_ITEM_NONE = 0
FLAG_ITEM_ALL = 64+32+8+4+2+1

class Robolink:
    """The Robolink class is the link to to RoboDK and allows creating macros for Robodk, simulate applications and generate programs offline.
    Any interaction is made through \"items\" (Item() objects). An item is an object in the
    robodk tree (it can be either a robot, an object, a tool, a frame, a 
    program, ...).
    
    :param str robodk_ip: IP of the RoboDK API server (default='localhost')
    :param int port: Port of the RoboDK API server (default=None, it will use the default values)
    :param str args: Command line arguments to pass to RoboDK on startup (such as '/NOSPLASH /NOSHOW), to not display RoboDK. It has no effect if RoboDK is already running.\n
        For more information: `RoboDK list of arguments on startup <https://robodk.com/doc/en/RoboDK-API.html#CommandLine>`_.
    :param str robodk_path: RoboDK installation path. It defaults to RoboDK's default path (C:/RoboDK/bin/RoboDK.exe)
    
    .. seealso:: :func:`~robolink.Robolink.Item`
    
    """
    APPLICATION_DIR = 'C:/RoboDK/bin/RoboDK.exe'    # file path to the robodk program (executable)
    SAFE_MODE = 1           # checks that provided items exist in memory
    AUTO_UPDATE = 0         # if AUTO_UPDATE is zero, the scene is rendered after every function call
    TIMEOUT = 10             # timeout for communication, in seconds
    COM = None              # tcpip com
    IP = 'localhost'        # IP address of the simulator (localhost if it is the same computer), otherwise, use RL = Robolink('yourip') to set to a different IP
    ARGUMENTS = []        # Command line arguments to RoboDK, such as /NOSPLASH /NOSHOW to not display RoboDK. It has no effect if RoboDK is already running.
    PORT_START = 20500      # port to start looking for app connection
    PORT_END = 20500        # port to stop looking for app connection
    PORT = -1
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    def _is_connected(self):
        """Returns 1 if connection is valid, returns 0 if connection is invalid"""
        if not self.COM: return 0
        connected = 1        
        #try:
        #    self.COM.settimeout(0)
        #    check = self.COM.recv(1)
        #except:
        #    connected = 0
        #    
        #self.COM.settimeout(self.TIMEOUT)
        return connected

    def _check_connection(self):
        """If we are not connected it will attempt a connection, if it fails, it will throw an error"""
        if not self._is_connected() and self.Connect() < 1:
            raise Exception('Unable to connect')
        #To do: Clear input buffer.

    def _check_status(self):
        """This procedure checks the status of the connection"""
        status = self._rec_int()
        if status > 0 and status < 10:
            strproblems = 'Unknown error'
            if status == 1:
                strproblems = 'Invalid item provided: The item identifier provided is not valid or it does not exist.'
            elif status == 2: #output warning
                strproblems = self._rec_line()
                print('WARNING: ' + strproblems)
                #warn(strproblems)# does not show where is the problem...
                return 0
            elif status == 3: #output error
                strproblems = self._rec_line()
                raise Exception(strproblems)
            elif status == 9:
                strproblems = 'Invalid license. Contact us at: www.robodk.com'
            print(strproblems)
            raise Exception(strproblems)
        elif status == 0:
            # everything is OK
            status = status;
        else:
            raise Exception('Problems running function')
        return status

    def _check_color(self, color):
        """Formats the color in a vector of size 4x1 and ranges [0,1]"""
        if not isinstance(color,list) or len(color) < 3 or len(color) > 4:
            raise Exception('The color vector must be a list of 3 or 4 values')
        if len(color) == 3:
            color.append(1)
        if max(color) > 1 or min(color) < -1:
            print("WARNING: Color provided is not in the range [0,1] ([r,g,b,a])")
        return color

    def _send_line(self, string=None):
        """Sends a string of characters with a \\n"""
        if sys.version_info[0] < 3:
            self.COM.send(bytes(string+'\n')) # Python 2.x only
        else:
            self.COM.send(bytes(string+'\n','utf-8')) # Python 3.x only

    def _rec_line(self):
        """Receives a string. It reads until if finds LF (\\n)"""
        string = b''
        chari = self.COM.recv(1)
        while chari != b'\n':    # read until LF
            string = string + chari
            chari = self.COM.recv(1)
        return str(string.decode('utf-8')) # python 2 and python 3 compatible
        #string = ''
        #chari = self.COM.recv(1).decode('utf-8')
        #while chari != '\n':    # read until LF
        #    string = string + chari
        #    chari = self.COM.recv(1).decode('utf-8')
        #return str(string) # python 2 and python 3 compatible

    def _send_item(self, item):
        """Sends an item pointer"""
        if isinstance(item, Item):
            self.COM.send(struct.pack('>Q',item.item))#q=unsigned long long (64 bits), d=float64
            return
        if item is None:
            item = 0
        self.COM.send(struct.pack('>Q',item))#q=unsigned long long (64 bits), d=float64

    def _rec_item(self):
        """Receives an item pointer"""
        buffer = self.COM.recv(8)
        item = struct.unpack('>Q',buffer)#q=unsigned long long (64 bits), d=float64
        buffer2 = self.COM.recv(4)
        itemtype = struct.unpack('>i',buffer2)
        return Item(self,item[0], itemtype[0])
        
    def _send_ptr(self, ptr_h):
        """Sends a generic pointer"""
        self.COM.send(struct.pack('>Q',ptr_h))#q=unsigned long long (64 bits), d=float64

    def _rec_ptr(self):
        """Receives a generic pointer"""
        buffer = self.COM.recv(8)
        ptr_h = struct.unpack('>Q',buffer)#q=unsigned long long (64 bits), d=float64
        return ptr_h[0] #return ptr_h

    def _send_pose(self, pose):
        """Sends a pose (4x4 matrix)"""
        if not pose.isHomogeneous():
            print("Warning: pose is not homogeneous!")
            print(pose)
        posebytes = b''
        for j in range(4):
            for i in range(4):
                posebytes = posebytes + struct.pack('>d',pose[i,j])
        self.COM.send(posebytes)

    def _rec_pose(self):
        """Receives a pose (4x4 matrix)"""
        posebytes = self.COM.recv(16*8)
        posenums = struct.unpack('>16d',posebytes)
        pose = Mat(4,4)
        cnt = 0
        for j in range(4):
            for i in range(4):
                pose[i,j] = posenums[cnt]
                cnt = cnt + 1
        return pose
        
    def _send_xyz(self, pos):
        """Sends an xyz vector"""
        posbytes = b''
        for i in range(3):
            posbytes = posbytes + struct.pack('>d',pos[i])
        self.COM.send(posbytes)

    def _rec_xyz(self):
        """Receives an xyz vector"""
        posbytes = self.COM.recv(3*8)
        posnums = struct.unpack('>3d',posbytes)
        pos = [0,0,0]
        for i in range(3):
            pos[i] = posnums[i]
        return pos

    def _send_int(self, num):
        """Sends an int (32 bits)"""
        if isinstance(num, float):
            num = round(num)
        elif not isinstance(num, int):
            num = num[0]
        self.COM.send(struct.pack('>i',num))

    def _rec_int(self):
        """Receives an int (32 bits)"""
        buffer = self.COM.recv(4)
        num = struct.unpack('>i',buffer)
        return num[0]

    def _send_array(self, values):
        """Sends an array of doubles"""
        if not isinstance(values,list):#if it is a Mat() with joints
            values = (values.tr()).rows[0];          
        nval = len(values)
        self._send_int(nval)        
        if nval > 0:
            buffer = b''
            for i in range(nval):
                buffer = buffer + struct.pack('>d',values[i])
            self.COM.send(buffer)

    def _rec_array(self):
        """Receives an array of doubles"""
        nvalues = self._rec_int()
        if nvalues > 0:
            buffer = self.COM.recv(8*nvalues)
            values = list(struct.unpack('>'+str(nvalues)+'d',buffer))
            #values = fread(self.COM, nvalues, 'double')
        else:
            values = [0]
        return Mat(values)

    def _send_matrix(self, mat):
        """Sends a 2 dimensional matrix (nxm)"""
        if mat is None:
            self._send_int(0)
            self._send_int(0)
            return
        if type(mat) == list:
            mat = Mat(mat).tr()
        size = mat.size()
        self._send_int(size[0])
        self._send_int(size[1])
        for j in range(size[1]):
            matbytes = b''
            for i in range(size[0]):
                matbytes = matbytes + struct.pack('>d',mat[i,j])
            self.COM.send(matbytes)

    def _rec_matrix(self):
        """Receives a 2 dimensional matrix (nxm)"""
        size1 = self._rec_int()
        size2 = self._rec_int()
        recvsize = size1*size2*8
        BUFFER_SIZE = 512
        if recvsize > 0:
            matbytes = b''
            to_receive = min(recvsize, BUFFER_SIZE)
            while to_receive > 0:
                matbytes += self.COM.recv(to_receive)
                to_receive = min(recvsize - len(matbytes), BUFFER_SIZE)
            matnums = struct.unpack('>'+str(size1*size2)+'d',matbytes)
            mat = Mat(size1,size2)
            cnt = 0
            for j in range(size2):
                for i in range(size1):
                    mat[i,j] = matnums[cnt]
                    cnt = cnt + 1
        else:
            mat = Mat([[]])
        return mat

    def _moveX(self, target, itemrobot, movetype, blocking=True):
        """Performs a linear or joint movement. Use MoveJ or MoveL instead."""
        #self._check_connection();
        itemrobot.WaitMove()# checks connection
        command = 'MoveX'
        self._send_line(command)
        self._send_int(movetype)
        if isinstance(target,Item):# target is an item
            self._send_int(3)
            self._send_array([])
            self._send_item(target)
        elif isinstance(target,list) or target.size() != (4,4):# target are joints
            self._send_int(1)
            self._send_array(target)
            self._send_item(0)
        elif target.size() == (4,4):    # target is a pose
            self._send_int(2)
            mattr = target.tr()
            self._send_array(mattr.rows[0]+mattr.rows[1]+mattr.rows[2]+mattr.rows[3])
            self._send_item(0)
        else:
            raise Exception('Invalid input values')
        self._send_item(itemrobot)
        self._check_status()
        if blocking:
            itemrobot.WaitMove()
            
    def MoveC(self, target1, target2, itemrobot, blocking=True):
        """Performs a circular movement. Use robot.MoveC instead."""
        #self._check_connection();
        itemrobot.WaitMove()# checks connection
        command = 'MoveC'
        self._send_line(command)
        self._send_int(3)
        if isinstance(target1,Item):# target1 is an item
            self._send_int(3)
            self._send_array([])
            self._send_item(target1)
        elif isinstance(target1,list) or target1.size() != (4,4):# target1 are joints
            self._send_int(1)
            self._send_array(target1)
            self._send_item(0)
        elif target1.size() == (4,4):    # target1 is a pose
            self._send_int(2)
            mattr = target1.tr()
            self._send_array(mattr.rows[0]+mattr.rows[1]+mattr.rows[2]+mattr.rows[3])
            self._send_item(0)
        else:
            raise Exception('Invalid input value for target 1')
        if isinstance(target2,Item):# target1 is an item
            self._send_int(3)
            self._send_array([])
            self._send_item(target2)
        elif isinstance(target2,list) or target2.size() != (4,4):# target2 are joints
            self._send_int(1)
            self._send_array(target2)
            self._send_item(0)
        elif target2.size() == (4,4):    # target2 is a pose
            self._send_int(2)
            mattr = target2.tr()
            self._send_array(mattr.rows[0]+mattr.rows[1]+mattr.rows[2]+mattr.rows[3])
            self._send_item(0)
        else:
            raise Exception('Invalid input value for target 2')
        self._send_item(itemrobot)
        self._check_status()
        if blocking:
            itemrobot.WaitMove()

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
    def __init__(self, robodk_ip='localhost', port=None, args=[], robodk_path=None):
        """A connection is attempted upon creation of the object
        In  1 (optional) : robodk_ip -> IP of the RoboDK API server (default='localhost')
        In  2 (optional) : port -> Port of the RoboDK API server (default=None)
        In  3 (optional) : args -> Command line arguments, as a list, to pass to RoboDK on startup (such as '/NOSPLASH /NOSHOW), to not display RoboDK. It has no effect if RoboDK is already running.
        In  4 (optional) : robodk_path -> RoboDK path. Leave it to the default None for the default path (C:/RoboDK/bin/RoboDK.exe)."""
        self.IP = robodk_ip
        self.ARGUMENTS = args
        if robodk_path is not None:
            self.APPLICATION_DIR = robodk_path
            
        if port is not None:
            self.PORT_START = port
            self.PORT_END = port
            self.ARGUMENTS.append("/PORT=%i" % port)
            
        elif '/NEWINSTANCE' in self.ARGUMENTS:
            from socket import socket
            with socket() as s:
                s.bind(('',0))
                port = s.getsockname()[1]
                print("Using available port %i" % port)
                self.PORT_START = port
                self.PORT_END = port
                self.ARGUMENTS.append("/PORT=%i" % port)
                
        self.Connect()

    def _set_connection_params(self, safe_mode=1, auto_update=0, timeout=None):
        """Sets some behavior parameters: SAFE_MODE, AUTO_UPDATE and TIMEOUT.
        SAFE_MODE checks that item pointers provided by the user are valid.
        AUTO_UPDATE checks that item pointers provided by the user are valid.
        TIMEOUT is the timeout to wait for a response. Increase if you experience problems loading big files.
        If connection failed returns 0.
        In  1 (optional) : int -> SAFE_MODE (1=yes, 0=no)
        In  2 (optional) : int -> AUTO_UPDATE (1=yes, 0=no)
        In  3 (optional) : int -> TIMEOUT (1=yes, 0=no)
        Out 1 : int -> connection status (1=ok, 0=problems)
        Example:
            _set_connection_params(0,0); # Use for speed. Render() must be called to refresh the window.
            _set_connection_params(1,1); # Default behavior. Updates every time."""
        self.SAFE_MODE = safe_mode
        self.AUTO_UPDATE = auto_update
        self.TIMEOUT = timeout or self.TIMEOUT
        self._send_line('CMD_START')
        self._send_line(str(self.SAFE_MODE) + ' ' + str(self.AUTO_UPDATE))
        #fprintf(self.COM, sprintf('%i %i'), self.SAFE_MODE, self.AUTO_UPDATE))# appends LF
        response = self._rec_line()
        if response == 'READY':
            ok = 1
        else:
            ok = 0
        return ok
    
    def Disconnect(self):
        """Stops the communication with RoboDK. If setRunMode is set to RUNMODE_MAKE_ROBOTPROG for offline programming, any programs pending will be generated."""
        self.COM.close()
        
    def Finish(self):
        """Stops the communication with RoboDK. If setRunMode is set to RUNMODE_MAKE_ROBOTPROG for offline programming, any programs pending will be generated.
        
        .. seealso:: :func:`~robolink.Robolink.setRunMode`, :func:`~robolink.Robolink.AddProgram`, :func:`~robolink.Robolink.ProgramStart`"""
        self.Disconnect()
    
    def NewLink(self):
        """Reconnect the API using a different communication link."""
        try:
        #if True:
            import socket
            #self.COM.close()
            self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.COM.connect((self.IP, self.PORT))                
            connected = self._is_connected()
            if connected > 0:
                self._set_connection_params()
                self.COM.settimeout(self.TIMEOUT)
            else:
                print("Failed to reconnect (1)")
        except:
            print("Failed to reconnect (2)")
            
    def Connect(self):
        """Establish a connection with RoboDK. If RoboDK is not running it will attempt to start RoboDK from the default installation path (otherwise APPLICATION_DIR must be set properly).
        If the connection succeeds it returns 1, otherwise it returns 0"""
        def start_robodk(command):
            print('Starting %s\n' % self.APPLICATION_DIR)
            import subprocess
            #import time            
            #tstart = time.time()
            p = subprocess.Popen(command,stdout=subprocess.PIPE)
            while True:
                line = str(p.stdout.readline().decode("utf-8")).strip()
                print(line)
                if 'running' in line.lower():
                    #telapsed = time.time() - tstart
                    #print("RoboDK startup time: %.3f" % telapsed)
                    break
            
            #with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            #    self._ProcessID = p.pid
            #    for line in p.stdout:
            #        line_ok = line.strip()
            #        print(line_ok)
            #        if 'running' in line_ok.lower():
            #            print("RoboDK is running")
            #            return #does not return!!
                        
        import socket
        connected = 0
        for i in range(2):
            for port in range(self.PORT_START,self.PORT_END+1):
                self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.COM.settimeout(1)
                try:
                    self.COM.connect((self.IP, port))                
                    connected = self._is_connected()
                    if connected > 0:
                        self.COM.settimeout(self.TIMEOUT)
                        break
                except:
                    connected = connected

            if connected > 0:# if status is closed, try to open application
                self.PORT = port
                break;
            elif i == 0:            
                if self.IP != 'localhost':
                    break;
                    
                try:
                    command = [self.APPLICATION_DIR] + self.ARGUMENTS
                    start_robodk(command)                    
                    #import time
                    #time.sleep(5) # wait for RoboDK to start and check network license.
                except:
                    raise Exception('Application path is not correct or could not start: ' + self.APPLICATION_DIR)

        if connected > 0 and not self._set_connection_params():
            connected = 0
        return connected

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # public methods
    def Item(self, name, itemtype=None):
        """Returns an item by its name. If there is no exact match it will return the last closest match.
        Specify what type of item you are looking for with itemtype. This is useful if 2 items have the same name but different type.
        (check variables ITEM_TYPE_*)    
            
        :param str name: name of the item (name of the item shown in the RoboDK station tree)
        :param int itemtype: type of the item to be retrieved (avoids confusion if there are similar name matches). Use ITEM_TYPE_*.

        .. code-block:: python
            :caption: Available Item types
            
            ITEM_TYPE_STATION=1             # station item (.rdk files)
            ITEM_TYPE_ROBOT=2               # robot item (.robot files)
            ITEM_TYPE_FRAME=3               # reference frame item
            ITEM_TYPE_TOOL=4                # tool item (.tool files or tools without geometry)
            ITEM_TYPE_OBJECT=5              # object item (.stl, .step, .iges, ...)
            ITEM_TYPE_TARGET=6              # target item
            ITEM_TYPE_PROGRAM=8             # program item (made using the GUI)
            ITEM_TYPE_PROGRAM_PYTHON=10     # Python program or macro
                
        .. seealso:: :func:`~robolink.Robolink.ItemList`, :func:`~robolink.Robolink.ItemUserPick`
                
        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                # Retrieve an item named tool
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # the first available robot

        """
        self._check_connection()
        if itemtype is None:
            command = 'G_Item'
            self._send_line(command)
            self._send_line(name)
        else:
            command = 'G_Item2'
            self._send_line(command)
            self._send_line(name)
            self._send_int(itemtype)
        item = self._rec_item()#     item = fread(com, 2, 'ulong');% ulong is 32 bits!!!
        self._check_status()
        return item


    def ItemList(self, filter=None, list_names=False):
        """Returns a list of items (list of name or pointers) of all available items in the currently open station of RoboDK.
        
        :param int filter: (optional) Filter the list by a specific item type (ITEM_TYPE_*). For example: RDK.ItemList(filter = ITEM_TYPE_ROBOT)
        :param int list_names: (optional) Set to True to return a list of names instead of a list of :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.Item`, :func:`~robolink.Robolink.ItemUserPick`
        """
        self._check_connection()
        retlist = []
        if list_names:
            if filter is None:
                command = 'G_List_Items'
                self._send_line(command)
            else:
                command = 'G_List_Items_Type'
                self._send_line(command)
                self._send_int(filter)
            count = self._rec_int()
            for i in range(count):
                namei = self._rec_line()
                retlist.append(namei)
        else:
            if filter is None:
                command = 'G_List_Items_ptr'
                self._send_line(command)
            else:
                command = 'G_List_Items_Type_ptr'
                self._send_line(command)
                self._send_int(filter)
            count = self._rec_int()
            for i in range(count):
                itemi = self._rec_item()
                retlist.append(itemi)
        self._check_status()
        return retlist

    def ItemUserPick(self, message="Pick one item", itemtype=None):
        """Shows a RoboDK popup to select one object from the open station.
        An item type can be specified to filter desired items. If no type is specified, all items are selectable.
        (check variables ITEM_TYPE_*)
        Example:
           RL.ItemUserPick("Pick a robot", ITEM_TYPE_ROBOT)
           
        :param str message: message to display
        :param int itemtype: filter choices by a specific item type (ITEM_TYPE_*)
        
        .. seealso:: :func:`~robolink.Robolink.Item`, :func:`~robolink.Robolink.ItemList`
        """
        self._check_connection()
        if itemtype is None:
            itemtype = -1
        command = 'PickItem'
        self._send_line(command)
        self._send_line(message)
        self._send_int(itemtype)
        self.COM.settimeout(3600) # wait up to 1 hour for user input
        item = self._rec_item()
        self.COM.settimeout(self.TIMEOUT)
        self._check_status()
        return item

    def ShowRoboDK(self):
        """Show or raise the RoboDK window
        
        .. seealso:: :func:`~robolink.Robolink.setWindowState`"""
        self._check_connection()
        command = 'RAISE'
        self._send_line(command)
        self._check_status()
        
    def HideRoboDK(self):
        """Hide the RoboDK window. RoboDK will keep running as a process
        
        .. seealso:: :func:`~robolink.Robolink.setWindowState`"""
        self._check_connection()
        command = 'HIDE'
        self._send_line(command)
        self._check_status()
        
    def CloseRoboDK(self):
        """Close RoboDK window and finish RoboDK's execution."""
        self._check_connection()
        command = 'QUIT'
        self._send_line(command)
        self._check_status()
        
    def setWindowState(self, windowstate=WINDOWSTATE_NORMAL):
        """Set the state of the RoboDK window
        
        :param int windowstate: state of the window (WINDOWSTATE_*)
        
        .. code-block:: python
            :caption: Allowed window states
            
            WINDOWSTATE_HIDDEN      = -1        # Hidden
            WINDOWSTATE_SHOW        = 0         # Visible
            WINDOWSTATE_MINIMIZED   = 1         # Minimize window
            WINDOWSTATE_NORMAL      = 2         # Show normal window (last known state)
            WINDOWSTATE_MAXIMIZED   = 3         # Show maximized window
            WINDOWSTATE_FULLSCREEN  = 4         # Show fulscreen window
            WINDOWSTATE_CINEMA      = 5         # Show maximized window without the toolbar and without the menu
            WINDOWSTATE_FULLSCREEN_CINEMA= 6    # Show fulscreen window without the toolbar and without the menu
            
        .. seealso:: :func:`~robolink.Robolink.setFlagsRoboDK`
        """
        self._check_connection()
        command = 'S_WindowState'
        self._send_line(command)
        self._send_int(windowstate)
        self._check_status()
        
    def setFlagsRoboDK(self, flags=FLAG_ROBODK_ALL):
        """Update the RoboDK flags. RoboDK flags allow defining how much access the user has to RoboDK features. Use a FLAG_ROBODK_* variables to set one or more flags.
        
        :param int flags: state of the window (FLAG_ROBODK_*)
        
        .. code-block:: python
            :caption: Allowed RoboDK flags
        
            FLAG_ROBODK_TREE_ACTIVE = 1                 # Enable the tree
            FLAG_ROBODK_3DVIEW_ACTIVE = 2               # Enable the 3D view (3D mouse navigation)
            FLAG_ROBODK_LEFT_CLICK = 4                  # Enable left clicks
            FLAG_ROBODK_RIGHT_CLICK = 8                 # Enable right clicks
            FLAG_ROBODK_DOUBLE_CLICK = 16               # Enable double clicks
            FLAG_ROBODK_MENU_ACTIVE = 32                # Enable the main menu (complete menu)
            FLAG_ROBODK_MENUFILE_ACTIVE = 64            # Enable the File menu
            FLAG_ROBODK_MENUEDIT_ACTIVE = 128           # Enable the Edit menu
            FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256        # Enable the Program menu
            FLAG_ROBODK_MENUTOOLS_ACTIVE = 512          # Enable the Tools menu
            FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024     # Enable the Utilities menu
            FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048       # Enable the Connect menu
            FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096        # Enable the keyboard
            FLAG_ROBODK_TREE_VISIBLE = 8192             # Make the station tree visible
            FLAG_ROBODK_REFERENCES_VISIBLE = 16384      # Make the reference frames visible
            FLAG_ROBODK_NONE = 0                        # Disable everything
            FLAG_ROBODK_ALL = 0xFFFF                    # Enable everything
            FLAG_ROBODK_MENU_ACTIVE_ALL                 # Enable the menu only
            
        .. seealso:: :func:`~robolink.Robolink.setFlagsItem`, :func:`~robolink.Robolink.setWindowState`
        """
        self._check_connection()
        command = 'S_RoboDK_Rights'
        self._send_line(command)
        self._send_int(flags)
        self._check_status()
        
    def setFlagsItem(self, item, flags=FLAG_ITEM_ALL):
        """Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
        
        :param item: item to set (set to 0 to apply to all items)
        :type item: :class:`Item`
        :param flags: set the item flags (FLAG_ITEM_*)
        :type flags: int        
        
        .. seealso:: :func:`~robolink.Robolink.getFlagsItem`, :func:`~robolink.Robolink.setFlagsRoboDK`, :func:`~robolink.Robolink.setWindowState`"""
        self._check_connection()
        command = 'S_Item_Rights'
        self._send_line(command)
        self._send_item(item)
        self._send_int(flags)
        self._check_status()
        
    def getFlagsItem(self, item):
        """Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
        
        :param item: item to get flags
        :type item: :class:`Item`

        .. code-block:: python
            :caption: Allowed RoboDK flags
            
            FLAG_ITEM_SELECTABLE = 1        # Allow selecting the item
            FLAG_ITEM_EDITABLE = 2          # Allow editing the item
            FLAG_ITEM_DRAGALLOWED = 4       # Allow dragging the item
            FLAG_ITEM_DROPALLOWED = 8       # Allow dropping nested items
            FLAG_ITEM_ENABLED = 32          # Enable this item in the tree
            FLAG_ITEM_NONE = 0              # Disable everything
            FLAG_ITEM_ALL = 64+32+8+4+2+1   # Enable everything
        
        .. seealso:: :func:`~robolink.Robolink.setFlagsItem`, :func:`~robolink.Robolink.setFlagsRoboDK`, :func:`~robolink.Robolink.setWindowState`
        """
        self._check_connection()
        command = 'S_Item_Rights'
        self._send_line(command)
        self._send_item(item)
        flags = self._red_int()
        self._check_status()
        return flags
    
    def ShowMessage(self, message, popup=True):
        """Show a message from the RoboDK window. By default, the message will be a blocking popup. Alternatively, it can be a message displayed at the bottom of RoboDK's main window.
        
        :param str message: message to display
        :param bool popup: Set to False to display the message in the RoboDK's status bar (not blocking)
        """
        self._check_connection()
        if popup:
            command = 'ShowMessage'
            self._send_line(command)
            self._send_line(message)
            self.COM.settimeout(3600) # wait up to 1 hour user to hit OK
            self._check_status()
            self.COM.settimeout(self.TIMEOUT)
        else:
            command = 'ShowMessageStatus'
            self._send_line(command)
            self._send_line(message)
            self._check_status()
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def Copy(self, item):
        """Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste().
        
        :param item: Item to copy to the clipboard
        :type item: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.Paste`, Item. :func:`~robolink.Item.Copy`
        
        Example:
        
        .. code-block:: python
        
            RDK = Robolink()
            object = RDK.Item('My Object')
            object.Copy()               # same as RDK.Copy(object) also works
            object_copy1 = RDK.Paste()
            object_copy1.setName('My Object (copy 1)')
            object_copy2 = RDK.Paste()
            object_copy2.setName('My Object (copy 2)')
        
        """
        self._check_connection()
        command = 'Copy'
        self._send_line(command)
        self._send_item(item)
        self._check_status()

    def Paste(self, paste_to=0):
        """Paste the copied item as a dependency of another item (same as Ctrl+V). Paste should be used after Copy(). It returns the newly created item. 
        
        :param paste_to: Item to attach the copied item (optional)
        :type paste_to: :class:`.Item`        
        :return: New item created
        :rtype: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.Copy`
        
        """
        self._check_connection()
        command = 'Paste'
        self._send_line(command)
        self._send_item(paste_to)
        newitem = self._rec_item()
        self._check_status()
        return newitem

    def AddFile(self, filename, parent=0):
        """Load a file and attaches it to parent and returns the newly added :class:`.Item`. 
        
        :param str filename: any file to load, supported by RoboDK. Supported formats include STL, STEP, IGES, ROBOT, TOOL, RDK,... It is also possible to load supported robot programs, such as SRC (KUKA), SCRIPT (Universal Robots), LS (Fanuc), JBI (Motoman), MOD (ABB), PRG (ABB), ...
        :param parent: item to attach the newly added object (optional)
        :type parent: :class:`.Item`
        
        Example:
        
        .. code-block:: python
            
            RDK = Robolink()
            item = RDK.AddFile(r'C:\\Users\\Name\\Desktop\\object.step')
            RDK.setPose(item, transl(100,50,500))
            
        .. seealso:: :func:`~robolink.Robolink.Save`
            
        """
        self._check_connection()
        command = 'Add'
        self._send_line(command)
        self._send_line(filename)
        self._send_item(parent)
        newitem = self._rec_item()
        self._check_status()
        return newitem
        
    def AddShape(self, triangle_points, add_to=0, override_shapes = False):
        """Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
        
        :param triangle_points: List of vertices grouped by triangles.
        :type triangle_points: :class:`robodk.Mat` (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)
        :param parent: item to attach the newly added geometry (optional)
        :type parent: :class:`.Item`
        :param override_shapes: Set to True to fill the object with a new shape
        :type override_shapes: bool
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddCurve`, :func:`~robolink.Robolink.AddPoints`
        """
        if isinstance(triangle_points,list):
            triangle_points = tr(Mat(triangle_points))
        elif not isinstance(triangle_points, Mat):
            raise Exception("triangle_points must be a 3xN or 6xN list or matrix")
        self._check_connection()
        command = 'AddShape2'
        self._send_line(command)
        self._send_matrix(triangle_points)
        self._send_item(add_to)
        self._send_int(1 if override_shapes else 0)
        newitem = self._rec_item()
        self._check_status()
        return newitem    
        
    def AddCurve(self, curve_points, reference_object=0, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        
        :param curve_points: List of points defining the curve
        :type curve_points: :class:`robodk.Mat` (3xN matrix, or 6xN to provide curve normals as ijk vectors)
        :param reference_object: item to attach the newly added geometry (optional)
        :type reference_object: :class:`.Item`
        :param bool add_to_ref: If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)
        :param int projection_type: type of projection. Use the PROJECTION_* flags.
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`
        
        .. code-block:: python
            :caption: Available projection types
            
            PROJECTION_NONE                = 0      # No projection
            PROJECTION_CLOSEST             = 1      # The projection will the closest point on the surface
            PROJECTION_ALONG_NORMAL        = 2      # The projection will be done along the normal.
            PROJECTION_ALONG_NORMAL_RECALC = 3      # The projection will be done along the normal and the normal will be recalculated according to the surface normal.            
        
        .. seealso:: :func:`~robolink.Robolink.AddShape`, :func:`~robolink.Robolink.AddPoints`
        """
        if isinstance(curve_points,list):
            curve_points = Mat(curve_points).tr()
        elif not isinstance(curve_points, Mat):
            raise Exception("curve_points must be a 3xN or 6xN list or matrix")
        self._check_connection()
        command = 'AddWire'
        self._send_line(command)
        self._send_matrix(curve_points)
        self._send_item(reference_object)
        self._send_int(1 if add_to_ref else 0)
        self._send_int(projection_type)        
        newitem = self._rec_item()
        self._check_status()
        return newitem   
        
    def AddPoints(self, points, reference_object=0, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        
        :param points: list of points or matrix
        :type points: :class:`robodk.Mat` (3xN matrix, or 6xN to provide point normals as ijk vectors)
        :param reference_object: item to attach the newly added geometry (optional)
        :type reference_object: :class:`.Item`
        :param bool add_to_ref: If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)
        :param int projection_type: type of projection. Use the PROJECTION_* flags.
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`
                
        .. seealso:: :func:`~robolink.Robolink.ProjectPoints`, :func:`~robolink.Robolink.AddShape`, :func:`~robolink.Robolink.AddCurve`
        
        The difference between ProjectPoints and AddPoints is that ProjectPoints does not add the points to the RoboDK station.
        """
        if isinstance(points,list):
            points = Mat(points).tr()
        elif not isinstance(points, Mat):
            raise Exception("points must be a 3xN or 6xN list or matrix")
        self._check_connection()
        command = 'AddPoints'
        self._send_line(command)
        self._send_matrix(points)
        self._send_item(reference_object)
        self._send_int(1 if add_to_ref else 0)
        self._send_int(projection_type)        
        newitem = self._rec_item()
        self._check_status()
        return newitem   

    def ProjectPoints(self, points, object_project, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Project a point or a list of points given its coordinates. 
        The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
        It returns the projected points as a list of points (empty matrix if failed). 
        
        :param points: list of points to project
        :type points: list of points (XYZ or XYZijk list of floats), or :class:`robodk.Mat` (3xN matrix, or 6xN to provide point normals as ijk vectors)
        :param object_project: object to project the points
        :type object_project: :class:`.Item`
        :param projection_type: Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.
        :type projection_type: int
        
        The difference between ProjectPoints and AddPoints is that ProjectPoints does not add the points to the RoboDK station.
        """
        islist = False
        if isinstance(points,list):
            islist = True
            points = Mat(points)
        elif not isinstance(points, Mat):
            raise Exception("points must be a 3xN or 6xN list or matrix")
        self._check_connection()
        command = 'ProjectPoints'
        self._send_line(command)
        self._send_matrix(points)
        self._send_item(object_project)
        self._send_int(projection_type)  
        self.COM.settimeout(30) # 30 seconds timeout
        projected_points = self._rec_matrix() # will wait here
        self.COM.settimeout(self.TIMEOUT)        
        self._check_status()
        if islist:
            projected_points = projected_points.tolist()
        return projected_points
        
    def Save(self, filename, itemsave=0):
        """Save an item or a station to a file (formats supported include RDK, STL, ROBOT, TOOL, ...). If no item is provided, the open station is saved.
        
        :param str filename: File path to save
        :param itemsave: Item to save (leave at 0 to save the current RoboDK station as an RDK file
        :type itemsave: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddFile`
        """
        self._check_connection()
        command = 'Save'
        self._send_line(command)
        self._send_line(filename)
        self._send_item(itemsave)
        self._check_status()
    
    def AddStation(self, name='New Station'):
        """Add a new empty station. It returns the station :class:`.Item` created.
        
        :param str name: name of the station
        
        .. seealso:: :func:`~robolink.Robolink.AddFile`"""
        self._check_connection()
        command = 'NewStation'
        self._send_line(command)
        self._send_line(name)
        newitem = self._rec_item()
        self._check_status()
        return newitem
        
    def AddTarget(self, name, itemparent=0, itemrobot=0):
        """Add a new target that can be reached with a robot.
        
        :param str name: Target name
        :param itemparent: Reference frame to attach the target
        :type itemparent: :class:`.Item`
        :param itemrobot: Robot that will be used to go to self target (optional)
        :type itemrobot: :class:`.Item`
        :return: New target item created
        :rtype: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddFrame`
        """
        self._check_connection()
        command = 'Add_TARGET'
        self._send_line(command)
        self._send_line(name)
        self._send_item(itemparent)
        self._send_item(itemrobot)
        newitem = self._rec_item()
        self._check_status()
        return newitem

    def AddFrame(self, name, itemparent=0):
        """Adds a new reference Frame. It returns the new :class:`.Item` created.
        
        :param str name: name of the new reference frame
        :param itemparent: Item to attach the new reference frame (such as another reference frame)
        :type itemparent: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddTarget`"""
        self._check_connection()
        command = 'Add_FRAME'
        self._send_line(command)
        self._send_line(name)
        self._send_item(itemparent)
        newitem = self._rec_item()
        self._check_status()
        return newitem

    def AddProgram(self, name, itemrobot=0):
        """Add a new program to the RoboDK station. Programs can be used to simulate a specific sequence, to generate vendor specific programs (Offline Programming) or to run programs on the robot (Online Programming).
        It returns the new :class:`.Item` created. 
        Tip: Use the MoveRobotThroughLine.py macro to create programs in the RoboDK station (Option 2).
        
        :param name: Name of the program
        :type name: str
        :param itemrobot: Robot that will be used for this program. It is not required to specify the robot if the station has only one robot or mechanism.
        :type itemrobot: :class:`.Item`
        :return: New program item
        :rtype: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddTarget`, :func:`~robolink.Item.MoveL`
        
        Example:
        
        .. code-block:: python
            
            # Turn off rendering (faster)
            RDK.Render(False)
            prog = RDK.AddProgram('AutoProgram')
            
            # Retrieve the current robot position:
            pose_ref = robot.Pose()

            # Iterate through a number of points
            for i in range(len(POINTS)):
                # add a new target
                ti = RDK.AddTarget('Auto Target %i' % (i+1))
                
                # use the reference pose and update the XYZ position
                pose_ref.setPos(POINTS[i])
                ti.setPose(pose_ref)
                
                # force to use the target as a Cartesian target (default)
                ti.setAsCartesianTarget()

                # Add the target as a Linear/Joint move in the new program
                prog.MoveL(ti)

            # Turn rendering ON before starting the simulation (automatic if we are done)
            RDK.Render(True)
            
        More examples: :ref:`lbl-move-through-points`. or the macro MoveRobotThroughLine.py
        """
        self._check_connection()
        command = 'Add_PROG'
        self._send_line(command)
        self._send_line(name)
        self._send_item(itemrobot)
        newitem = self._rec_item()
        self._check_status()
        return newitem
        
    def AddMillingProject(self, name='Milling settings', itemrobot=0):
        """Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points. 
        It returns the newly created :class:`.Item` containing the project settings.
        Tip: Use the MoveRobotThroughLine.py macro to see an example that creates a new "curve follow project" given a list of points to follow (Option 4).
        
        :param str name: Name of the project settings
        :param itemrobot: Robot to use for the project settings (optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.
        :type itemrobot: :class:`.Item`"""
        self._check_connection()
        command = 'Add_MACHINING'
        self._send_line(command)
        self._send_line(name)
        self._send_item(itemrobot)
        newitem = self._rec_item()
        self._check_status()
        return newitem

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def RunProgram(self, fcn_param, wait_for_finished = False):
        """Run a program (start a program). If the program exists in the RoboDK station it has the same behavior as right clicking a and selecting Run (or Run Python script for Python programs).
        When generating a program offline (Offline Programming), the program call will be generated in the program output (RoboDK will handle the syntax when the code is generated for a specific robot using the post processor).
                
        :param fcn_param: program name and parameters. Parameters can be provided for Python programs available in the RoboDK station as well.
        :type fcn_param: str
        :param bool wait_for_finished: Set to True to block execution during a simulation until the program finishes (skipped if the program does not exist or when the program is generated)
        
        .. seealso:: :func:`~robolink.Robolink.Item`, :func:`~robolink.Robolink.AddProgram`, :func:`~robolink.Item.Busy`
        """        
        if wait_for_finished:
            prog_item = self.Item(fcn_param, ITEM_TYPE_PROGRAM)
            if not prog_item.Valid():
                raise Exception('Invalid program %s' % fcn_param)
            prog_status = prog_item.RunProgram()
            prog_item.WaitFinished()
        else:
            prog_status = self.RunCode(fcn_param, True)
        return prog_status
    
    def RunCode(self, code, code_is_fcn_call=False):
        """Generate a program call or a customized instruction output in a program. 
        If code_is_fcn_call is set to True it has the same behavior as RDK.RunProgram(). In this case, when generating a program offline (offline programming), a function/procedure call will be generated in the program output (RoboDK will handle the syntax when the code is generated for a specific robot using the post processor).
        If the program exists it will also run the program in simulate mode.        
        
        :param code: program name or code to generate
        :type code: str
        :param code_is_fcn_call: Set to True if the provided code corresponds to a function call (same as RunProgram()), if so, RoboDK will handle the syntax when the code is generated for a specific robot.
        :type code_is_fcn_call: bool
        
        Example to run an existing program in the RoboDK station:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            RDK.RunCode("Prog1", True)              # Run a program named Prog1 available in the RoboDK station
            
        """
        self._check_connection()
        command = 'RunCode'
        self._send_line(command)
        self._send_int(code_is_fcn_call)
        self._send_line(code.replace('\r\n','<<br>>').replace('\n','<<br>>'))
        prog_status = self._rec_int()
        self._check_status()
        return prog_status
    
    def RunMessage(self, message, message_is_comment=False):
        """Show a message or a comment in the program generated offline (program generation). The message (or code) is displayed on the teach pendant of the robot.
        
        :param str message: message or comment to display.
        :param bool message_is_comment: Set to True to generate a comment in the generated code instead of displaying a message on the teach pendant of the robot.
        
        """
        print('Message: ' + message)
        self._check_connection()
        command = 'RunMessage'
        self._send_line(command)
        self._send_int(message_is_comment)
        self._send_line(message.replace('\r\n','<<br>>').replace('\n','<<br>>'))
        self._check_status()    

    def Render(self, always_render=False):
        """Display/render the scene: update the display. This function turns default rendering (rendering after any modification of the station unless always_render is set to true).
        Use Update to update the internal links of the complete station without rendering (when a robot or item has been moved).
        
        :param bool always_render: Set to True to update the screen every time the station is modified (default behavior when Render() is not used).
        
        .. seealso:: :func:`~robolink.Robolink.Update`
        """
        auto_render = not always_render;
        self._check_connection()
        command = 'Render'
        self._send_line(command)
        self._send_int(auto_render)
        self._check_status()
        
    def Update(self):
        """Update the screen. This updates the position of all robots and internal links according to previously set values. 
        This function is useful when Render is turned off (Example: "RDK.Render(False)"). Otherwise, by default RoboDK will update all links after any modification of the station (when robots or items are moved). 
        
        .. seealso:: :func:`~robolink.Robolink.Render`"""
        self._check_connection()
        command = 'Refresh'
        self._send_line(command)
        self._send_int(0)
        self._check_status()

    def IsInside(self, object_inside, object):
        """Return 1 (True) if object_inside is inside the object, otherwise, it returns 0 (False). Both objects must be of type :class:`.Item`"""
        self._check_connection()
        self._send_line('IsInside')
        self._send_item(object_inside)
        self._send_item(object)        
        inside = self._rec_int()
        self._check_status()
        return inside    
        
    def setCollisionActive(self, check_state = COLLISION_ON):
        """Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects (:class:`.Item`). This allows altering the collision map for Collision checking.
        
        .. seealso:: :func:`~robolink.Robolink.setCollisionActivePair`, :func:`~robolink.Item.Visible`
        """
        self._check_connection()
        command = 'Collision_SetState'
        self._send_line(command)
        self._send_int(check_state)
        ncollisions = self._rec_int()
        self._check_status()
        return ncollisions
        
    def setCollisionActivePair(self, check_state, item1, item2, id1=0, id2=0):
        """Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. Specify the link id for robots or moving mechanisms (id 0 is the base)
        Returns 1 if succeeded. Returns 0 if setting the pair failed (wrong id is provided)
        
        .. seealso:: :func:`~robolink.Robolink.setCollisionActive`, :func:`~robolink.Robolink.Collisions`, :func:`~robolink.Item.Visible`
        """
        self._check_connection()
        command = 'Collision_SetPair'
        self._send_line(command)
        self._send_item(item1)
        self._send_item(item2)
        self._send_int(id1)
        self._send_int(id2)
        self._send_int(check_state)
        success = self._rec_int()
        self._check_status()
        return success
        
    def Collisions(self):
        """Return the number of pairs of objects that are currently in a collision state.
        
        .. seealso:: :func:`~robolink.Robolink.setCollisionActive`, :func:`~robolink.Robolink.Collisions`, :func:`~robolink.Item.Visible`
        """
        self._check_connection()
        command = 'Collisions'
        self._send_line(command)
        ncollisions = self._rec_int()
        self._check_status()
        return ncollisions
        
    def Collision(self, item1, item2):
        """Returns 1 if item1 and item2 collided. Otherwise returns 0.
        
        .. seealso:: :func:`~robolink.Robolink.Collisions`, :func:`~robolink.Item.Visible`
        """
        self._check_connection()
        command = 'Collided'
        self._send_line(command)
        self._send_item(item1)
        self._send_item(item2)        
        ncollisions = self._rec_int()
        self._check_status()
        return ncollisions

    def setSimulationSpeed(self, speed):
        """Set the simulation speed. 
        A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.
        The slowest speed ratio allowed is 0.001. Set a large simmulation ratio (>100) for fast simulation results.
        
        :param speed: simulation ratio
        :type speed: float
        
        .. seealso:: :func:`~robolink.Robolink.SimulationSpeed`
        """ 
        self._check_connection()
        command = 'SimulateSpeed'
        self._send_line(command)
        self._send_int(speed*1000)
        self._check_status()
        
    def SimulationSpeed(self):
        """Return the simulation speed. A simulation speed of 1 means real-time simulation.
        A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.
        
        .. seealso:: :func:`~robolink.Robolink.setSimulationSpeed`
        """ 
        self._check_connection()
        command = 'GetSimulateSpeed'
        self._send_line(command)
        speed = self._rec_int()/1000.0
        self._check_status()
        return speed
    
    def setRunMode(self, run_mode=1):
        """Set the run mode (behavior) of the script, for either simulation, offline programming or online programming.
        By default, robodk shows the path simulation for movement instructions (run_mode=RUNMODE_SIMULATE).

        .. code-block:: python
            :caption: Available run modes
            
            RUNMODE_SIMULATE=1                      # performs the simulation moving the robot (default)
            RUNMODE_QUICKVALIDATE=2                 # performs a quick check to validate the robot movements
            RUNMODE_MAKE_ROBOTPROG=3                # makes the robot program
            RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD=4     # makes the robot program and updates it to the robot
            RUNMODE_MAKE_ROBOTPROG_AND_START=5      # makes the robot program and starts it on the robot (independently from the PC)
            RUNMODE_RUN_ROBOT=6                     # moves the real robot from the PC (PC is the client, the robot behaves like a server)
        
        The following calls will alter the current run mode:
        
        1- :func:`~robolink.Item.Connect` automatically sets RUNMODE_RUN_ROBOT. So it will use the robot driver together with the simulation.
        
        2- :func:`~robolink.Robolink.ProgramStart` automatically sets the mode to RUNMODE_MAKE_ROBOTPROG. So it will generate the program
                
        .. seealso:: :func:`~robolink.Robolink.RunMode`
        """
        self._check_connection()
        command = 'S_RunMode'
        self._send_line(command)
        self._send_int(run_mode)
        self._check_status()
        
    def RunMode(self):
        """Return the current run mode (behavior) of the script.
        By default, robodk simulates any movements requested from the API (such as prog.MoveL) simulation for movement instructions (run_mode=RUNMODE_SIMULATE).
        
        .. seealso:: :func:`~robolink.Robolink.setRunMode`
        """            
        self._check_connection()
        command = 'G_RunMode'
        self._send_line(command)
        runmode = self._rec_int()
        self._check_status()
        return runmode

    def getParams(self):
        """Get all the user parameters from the open RoboDK station.
        Station parameters can also be modified manually by right clicking the station item and selecting "Station parameters"
        :return: list of pairs of strings
        :rtype: list of str
        
        .. seealso:: :func:`~robolink.Robolink.getParam`, :func:`~robolink.Robolink.setParam`
        """    
        self._check_connection()
        command = 'G_Params'
        self._send_line(command)
        nparam = self._rec_int()
        params = []
        for i in range(nparam):
            param = self._rec_line()
            value = self._rec_line()
            try:
                value = float(value) # automatically convert int, long and float
            except ValueError:
                value = value
            params.append([param, value])
        self._check_status()
        return params
        
    def getParam(self, param='PATH_OPENSTATION'):
        """Get a global or a station parameter from the open RoboDK station.
        Station parameters can also be modified manually by right clicking the station item and selecting "Station parameters"
        
        :param str param: name of the parameter
        :return: value of the parameter.
        :rtype: str, float or None if the parameter is unknown
        
        .. code-block:: python
            :caption: Available global parameters
            
            PATH_OPENSTATION       # Full path of the current station (.rdk file)
            FILE_OPENSTATION       # File name of the current station (name of the .rdk file)
            PATH_DESKTOP           # Full path to the desktop folder
            
        .. seealso:: :func:`~robolink.Robolink.setParam`, :func:`~robolink.Robolink.getParams`
        """    
        self._check_connection()
        command = 'G_Param'
        self._send_line(command)
        self._send_line(param)
        value = self._rec_line()
        self._check_status()
        if value.startswith('UNKNOWN '):
            return None
        try:
            return float(value) # automatically convert int, long and float
        except ValueError:
            return value
        
    def setParam(self, param, value):
        """Set a station parameter. If the parameters exists, it will be updated. Otherwise, it will be added to the station.
        
        :param str param: name of the parameter
        :param str value: value of the parameter        
        
        .. seealso:: :func:`~robolink.Robolink.getParam`
        """    
        self._check_connection()
        command = 'S_Param'
        self._send_line(command)
        self._send_line(str(param))
        self._send_line(str(value).replace('\n',' '))
        self._check_status()

    def ShowSequence(self, matrix):
        """Display a sequence of joints given a list of joints as a matrix.
        This function can also display a sequence of instructions (RoKiSim format). 
        
        :param matrix: joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix
        :type matrix: :class:`.Mat`
        
        Tip: use :func:`~robolink.Item.InstructionList` to retrieve the instruction list in RoKiSim format.
        """
        Item(self, 0).ShowSequence(matrix)

    def LaserTracker_Measure(self, estimate=[0,0,0], search=False):
        """Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
        Returns the XYZ coordinates of target if it was found. Othewise it retuns None."""
        self._check_connection()
        command = 'MeasLT'
        self._send_line(command)
        self._send_xyz(estimate)
        self._send_int(1 if search else 0)
        xyz = self._rec_xyz()
        self._check_status()
        if xyz[0]*xyz[0] + xyz[1]*xyz[1] + xyz[2]*xyz[2] < 0.0001:
            return None
        
        return xyz        
        
    def StereoCamera_Measure(self):
        """Takes a measurement with the C-Track stereocamera.
        It returns two poses, the base reference frame and the measured object reference frame. Status is 0 if measurement succeeded."""
        self._check_connection()
        command = 'MeasPose'
        self._send_line(command)
        pose1 = self._rec_pose()
        pose2 = self._rec_pose()
        npoints1 = self._rec_int()
        npoints2 = self._rec_int()
        time = self._rec_int()
        status = self._rec_int()
        self._check_status()        
        return pose1, pose2, npoints1, npoints2, time, status
        
    def Collision_Line(self, p1, p2, ref=eye(4)):
        """Checks the collision between a line and any objects in the station. The line is composed by 2 points.
        
        :param p1: start point of the line
        :type p1: list of float [x,y,z]
        :param p2: end point of the line
        :type p2: list of float [x,y,z]
        :param ref: Reference of the two points with respect to the absolute station reference.
        :type ref: :class:`.Mat`
        :return: [collision (True or False), item (collided), point (point of collision with respect to the station)]
        :rtype: [bool, :class:`.Item`, list of float as xyz]
        """
        p1abs = ref*p1;
        p2abs = ref*p2;        
        self._check_connection()
        command = 'CollisionLine'
        self._send_line(command)
        self._send_xyz(p1abs)
        self._send_xyz(p2abs)
        itempicked = self._rec_item()
        xyz = self._rec_xyz()
        collision = itempicked.Valid()
        self._check_status()
        return collision, itempicked, xyz
        
    def setPoses(self, items, poses):
        """Sets the relative positions (poses) of a list of items with respect to their parent. For example, the position of an object/frame/target with respect to its parent.
        Use this function instead of setPose() for faster speed.        
        
        .. seealso:: :func:`~robolink.Item.setPose` (item), :func:`~robolink.Item.Pose` (item), :func:`~robolink.Robolink.setPosesAbs`
        """
        if len(items) != len(poses):
            raise Exception('The number of items must match the number of poses')
        
        if len(items) == 0:
            return
            
        self._check_connection()
        command = 'S_Hlocals'
        self._send_line(command)
        self._send_int(len(items))
        for i in range(len(items)):
            self._send_item(items[i])
            self._send_pose(poses[i])
        self._check_status()        
                
    def setPosesAbs(self, items, poses):
        """Set the absolute positions (poses) of a list of items with respect to the station reference. For example, the position of an object/frame/target with respect to its parent.
        Use this function instead of setPose() for faster speed.
        
        .. seealso:: :func:`~robolink.Item.setPoseAbs` (item), :func:`~robolink.Item.PoseAbs` (item), :func:`~robolink.Robolink.setPoses`
        """
        if len(items) != len(poses):
            raise Exception('The number of items must match the number of poses')
        
        if len(items) == 0:
            return
            
        self._check_connection()
        command = 'S_Hlocal_AbsS'
        self._send_line(command)
        self._send_int(len(items))
        for i in range(len(items)):
            self._send_item(items[i])
            self._send_pose(poses[i])
        self._check_status()
        
    def Joints(self, robot_item_list):
        """Return the current joints of a list of robots.
        
        .. seealso:: :func:`~robolink.Item.setJoints` (item), :func:`~robolink.Item.Joints` (item), :func:`~robolink.Robolink.setJoints`
        """
        self._check_connection()
        command = 'G_ThetasList'
        self._send_line(command)
        nrobs = len(robot_item_list)
        self._send_int(nrobs)
        joints_list = []
        for i in range(nrobs):
            self._send_item(robot_item_list[i])
            joints_i = self._rec_array()
            joints_list.append(joints_i)
        self._check_status()
        return joints_list

    def setJoints(self, robot_item_list, joints_list):
        """Sets the current robot joints for a list of robot items and a list joints.
        
        .. seealso:: :func:`~robolink.Item.setJoints` (item), :func:`~robolink.Item.Joints` (item), :func:`~robolink.Robolink.Joints`"""
        nrobs = len(robot_item_list)
        if nrobs != len(joints_list):
            raise Exception('The size of the robot list does not match the size of the joints list')
            
        self._check_connection()
        command = 'S_ThetasList'
        self._send_line(command)
        self._send_int(nrobs)
        for i in range(nrobs):
            self._send_item(robot_item_list[i])
            self._send_array(joints_list[i])
            
        self._check_status()
        
    def CalibrateTool(self, poses_xyzwpr, format=EULER_RX_RY_RZ, algorithm=CALIBRATE_TCP_BY_POINT, robot=None, tool=None):
        """Calibrate a TCP given a list of poses/joints and following a specific algorithm/method. 
        Tip: Provide the list of joints instead of poses to maximize accuracy for calibrated robots.
        
        :param poses_xyzwpr: List of points or a list of robot joints (matrix 3xN or nDOFsxN)
        :type poses_xyzwpr: :class:`.Mat` or a list of list of float
        :param int format: Euler format. Optionally, use JOINT_FORMAT and provide the robot.
        :param int algorithm: method/algorithm to use to calculate the new TCP. Tip: use CALIBRATE_TCP_...
        :param robot: the robot must be provided to calculate the reference frame by joints
        :type robot: :class:`.Item`
        :param tool: provide a tool item to store the calibration data with that tool (the TCP is not updated, only the calibration joints)
        :type tool: :class:`.Item`
        :return: \n
            [TCP, stats, errors]\n
            Out 1 (TCP) - the TCP as a list [x,y,z] with respect to the robot flange\n
            Out 2 (stats) - Statistics as [mean, standard deviation, max] - error stats summary\n
            Out 3 (errors) - errors for each pose (array 1xN)\n
        
        .. code-block:: python
            :caption: Available Tool Calibration Algorithms
            
            CALIBRATE_TCP_BY_POINT      # Take the same point using different orientations
            CALIBRATE_TCP_BY_PLANE      # Take the same point on a plane
            
        .. seealso:: :func:`~robolink.Robolink.CalibrateReference`
        """
        self._check_connection()
        command = 'CalibTCP3'
        self._send_line(command)
        self._send_matrix(poses_xyzwpr)
        self._send_int(format)
        if type(algorithm) != list:
            algorithm = [algorithm]
            
        self._send_array(algorithm)
        self._send_item(robot)
        self._send_item(tool)        
        self.COM.settimeout(3600)
        TCPxyz = self._rec_array()
        self.COM.settimeout(self.TIMEOUT)
        errorstats = self._rec_array()
        errors = self._rec_matrix()           
        self._check_status()
        errors = errors[:,1].tolist()
        return TCPxyz.tolist(), errorstats.tolist(), errors
        
    def CalibrateReference(self, joints_points, method=CALIBRATE_FRAME_3P_P1_ON_X, use_joints=False, robot=None):
        """Calibrate a reference frame given a number of points and following a specific algorithm/method. 
        Important: Provide the list of joints to maximize accuracy for calibrated robots.
        
        :param joints_points: List of points or a list of robot joints (matrix 3xN or nDOFsxN)
        :type joints_points: :class:`.Mat` or a list of list of float
        :param int method: method/algorithm to use to calculate the new TCP. Tip: use CALIBRATE_FRAME_...
        :param bool use_joints: use points or joint values (bool): Set to True if joints_points is a list of joints
        :param robot: the robot must be provided to calculate the reference frame by joints
        :type robot: :class:`.Item`
        :return: The pose of the reference frame with respect to the robot base frame
        :rtype: :class:`.Mat`
        
        .. code-block:: python
            :caption: Available Reference Frame Calibration Algorithms

            CALIBRATE_FRAME_3P_P1_ON_X = 0      # Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
            CALIBRATE_FRAME_3P_P1_ORIGIN = 1    # Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
            CALIBRATE_FRAME_6P = 2              # Calibrate by 6 points
            CALIBRATE_TURNTABLE = 3             # Calibrate turntable
            
        .. seealso:: :func:`~robolink.Robolink.CalibrateTool`        
        """
        self._check_connection()
        command = 'CalibFrame'
        self._send_line(command)
        self._send_matrix(joints_points)
        self._send_int(-1 if use_joints else 0)
        self._send_int(method)
        self._send_item(robot)
        reference_pose = self._rec_pose()
        errorstats = self._rec_array()
        self._check_status()
        return reference_pose        
        
    def ProgramStart(self, programname, folder='', postprocessor='', robot=None):
        """Defines the name of the program when the program is generated (offline programming). 
        It is also possible to specify the name of the post processor as well as the folder to save the program. 
        This method must be called before any program output is generated (before any robot movement or other instruction).
        
        :param str progname: name of the program
        :param str folder: folder to save the program, leave empty to use the default program folder
        :param str postprocessor: name of the post processor. For a post processor in C:/RoboDK/Posts/Fanuc_post.py, specify "Fanuc_post.py" or simply "Fanuc_post".
        :param robot: Robot to link
        :type robot: :class:`.Item`
        
        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # use the first available robot
            RDK.ProgramStart('Prog1','C:/MyProgramFolder/', "ABB_RAPID_IRC5", robot)  # specify the program name for program generation
            # RDK.setRunMode(RUNMODE_MAKE_ROBOTPROG) # redundant
            robot.MoveJ(target)                     # make a simulation
            ...
            RDK.Finish()                            # Provokes the program generation (disconnects the API)
            
        .. seealso:: :func:`~robolink.Robolink.setRunMode`, :func:`~robolink.Robolink.AddProgram`, :func:`~robolink.Robolink.Finish`
        """
        self._check_connection()
        command = 'ProgramStart'
        self._send_line(command)
        self._send_line(programname)
        self._send_line(folder)
        self._send_line(postprocessor)        
        if robot is None:
            self._send_item(Item(None))
        else:
            self._send_item(robot)        
        errors = self._rec_int()
        self._check_status()
        return errors
        
    #------------------------------------------------------------------
    #----------------------- CAMERA VIEWS ----------------------------
    def Cam2D_Add(self, item_object, cam_params=""):
        """Open a simulated 2D camera view. Returns a handle pointer that can be used in case more than one simulated view is used. 
        An example to use this option is available in the SetupCamera2D.py macro.
        
        :param item_object: object to attach the camera
        :type item_object: :class:`.Item`
        :param str cam_params: Camera parameters as a string. Add one or more of the following commands (in mm and degrees)
        
                        
        Example:
        
        .. code-block:: python
                    
            from robolink import *    # API to communicate with RoboDK
            RDK = Robolink()
            
            # Close any open 2D camera views
            RDK.Cam2D_Close()
            
            # Retrieve the camera reference frame
            camref = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)

            # set parameters in mm and degrees:
            # FOV: Field of view in degrees (atan(0.5*height/distance) of the sensor divided by
            # FOCAL_LENGHT: focal lenght in mm
            # FAR_LENGHT: maximum working distance (in mm)
            # SIZE: size of the sensor in pixels
            # DEPTH: Tag as depth to show the depth image in grey
            # BG_COLOR: background color (rgb color or named color: AARRGGBB)
            # LIGHT_AMBIENT: ambient color (rgb color or named color: AARRGGBB)
            # LIGHT_SPECULAR: specular color (rgb color or named color: AARRGGBB)
            # LIGHT_DIFFUSE: diffuse color (rgb color or named color: AARRGGBB)

            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=#FF00FF00 LIGHT_SPECULAR=black')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 DEPTH')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')

        .. seealso:: :func:`~robolink.Robolink.Cam2D_Snapshot`, :func:`~robolink.Robolink.Cam2D_Close`, :func:`~robolink.Robolink.Cam2D_SetParams`
        """
        self._check_connection()
        command = 'Cam2D_Add'
        self._send_line(command)
        self._send_item(item_object)
        self._send_line(cam_params)
        cam_handle = self._rec_ptr()
        self._check_status()
        return cam_handle
        
    def Cam2D_Snapshot(self, file_save_img, cam_handle=0):
        """Take a snapshot from a simulated camera view and save it to a file. Returns 1 if success, 0 otherwise.
        
        :param str file_save_img: file path to save. Formats supported include PNG, JPEG, TIFF, ...
        :param int cam_handle: camera handle (pointer returned by Cam2D_Add)
        
        .. seealso:: :func:`~robolink.Robolink.Cam2D_Add`, :func:`~robolink.Robolink.Cam2D_Close`
        """
        self._check_connection()
        command = 'Cam2D_Snapshot'
        self._send_line(command)
        self._send_ptr(int(cam_handle))
        self._send_line(file_save_img)        
        success = self._rec_int()
        self._check_status()
        return success
        
    def Cam2D_Close(self, cam_handle=0):
        """Closes all camera windows or one specific camera if the camera handle is provided. Returns 1 if success, 0 otherwise.
        
        :param cam_handle: camera handle (pointer returned by Cam2D_Add). Leave to 0 to close all simulated views.
        :type cam_handle: int
        
        .. seealso:: :func:`~robolink.Robolink.Cam2D_Add`, :func:`~robolink.Robolink.Cam2D_Snapshot`"""
        self._check_connection()
        if cam_handle == 0:
            command = 'Cam2D_CloseAll'
            self._send_line(command)
        else:
            command = 'Cam2D_Close'
            self._send_line(command)
            self._send_ptr(cam_handle)
        success = self._rec_int()
        self._check_status()
        return success
        
    def Cam2D_SetParams(self, params, cam_handle=0):
        """Set the parameters of the simulated camera.
        Returns 1 if success, 0 otherwise.
        
        :param str params: parameter settings according to the parameters supported by Cam2D_Add
        
        .. seealso:: :func:`~robolink.Robolink.Cam2D_Add`
        """
        self._check_connection()
        command = 'Cam2D_SetParams'
        self._send_line(command)
        self._send_ptr(int(cam_handle))
        self._send_line(params)        
        success = self._rec_int()
        self._check_status()
        return success
    
    #------------------------------------------------------------------
    #----------------------- SPRAY GUN SIMULATION ----------------------------
    def Spray_Add(self, item_tool=0, item_object=0, params="", points=None, geometry=None):
        """Add a simulated spray gun that allows projecting particles to a part. This is useful to simulate applications such as: 
        arc welding, spot welding, 3D printing, painting or inspection to verify the trace. The SprayOn.py macro shows an example to use this option.
        It returns a pointer that can be used later for other operations, such as turning the spray ON or OFF.
        
        :param str params: A string specifying the behavior of the simulated particles. The string can contain one or more of the following commands (separated by a space). See the allowed parameter options.
        :param points: provide the volume as a list of points as described in the sample macro SprayOn.py
        :type points: :class:`.Mat`
        :param geometry: (optional) provide a list of points describing triangles to define a specific particle geometry. Use this option instead of the PARTICLE command.
        :type geometry: :class:`.Mat`
                
        .. code-block:: python
            :caption: Allowed parameter options
            
            STEP=AxB: Defines the grid to be projected 1x1 means only one line of particle projection (for example, for welding)
            PARTICLE: Defines the shape and size of particle (sphere or particle), unless a specific geometry is provided:
                a- SPHERE(radius, facets)
                b- SPHERE(radius, facets, scalex, scaley, scalez)
                b- CUBE(sizex, sizey, sizez)
            RAND=factor: Defines a random factor factor 0 means that the particles are not deposited randomly
            ELLYPSE: defines the volume as an ellypse (default)
            RECTANGLE: defines the volume as a rectangle
            PROJECT: project the particles to the surface (default) (for welding, painting or scanning)
            NO_PROJECT: does not project the particles to the surface (for example, for 3D printing)
            
        .. seealso:: :func:`~robolink.Robolink.Spray_SetState`, :func:`~robolink.Robolink.Spray_GetStats`, :func:`~robolink.Robolink.Spray_Clear`
                
        Example:
        
        .. code-block:: python
            
            tool = 0    # auto detect active tool
            obj = 0     # auto detect object in active reference frame

            options_command = "ELLYPSE PROJECT PARTICLE=SPHERE(4,8,1,1,0.5) STEP=8x8 RAND=2"            

            # define the ellypse volume as p0, pA, pB, colorRGBA (close and far), in mm
            # coordinates must be provided with respect to the TCP
            close_p0 = [   0,   0, -200] # xyz in mm: Center of the conical ellypse (side 1)
            close_pA = [   5,   0, -200] # xyz in mm: First vertex of the conical ellypse (side 1)
            close_pB = [   0,  10, -200] # xyz in mm: Second vertex of the conical ellypse (side 1)
            close_color = [ 1, 0, 0, 1]  # RGBA (0-1)
            
            far_p0   = [   0,   0,  50] # xyz in mm: Center of the conical ellypse (side 2)
            far_pA   = [  60,   0,  50] # xyz in mm: First vertex of the conical ellypse (side 2)
            far_pB   = [   0, 120,  50] # xyz in mm: Second vertex of the conical ellypse (side 2)
            far_color   = [ 0, 0, 1, 0.2]  # RGBA (0-1)

            close_param = close_p0 + close_pA + close_pB + close_color
            far_param = far_p0 + far_pA + far_pB + far_color    
            volume = Mat([close_param, far_param]).tr()
            RDK.Spray_Add(tool, obj, options_command, volume)
            RDK.Spray_SetState(SPRAY_ON)
        
        """
        self._check_connection()
        command = 'Gun_Add'
        self._send_line(command)
        self._send_item(item_tool)
        self._send_item(item_object)        
        self._send_line(params)
        self._send_matrix(points)
        self._send_matrix(geometry)        
        id_spray = self._rec_int()
        self._check_status()
        return id_spray
        
    def Spray_SetState(self, state=SPRAY_ON, id_spray=-1):
        """Sets the state of a simulated spray gun (ON or OFF)
        
        :param int state: Set to ON or OFF. Use the defined constants: SPRAY_*
        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave to -1 to apply to all simulated sprays.
        
        .. seealso:: :func:`~robolink.Robolink.Spray_Add`, :func:`~robolink.Robolink.Spray_GetStats`, :func:`~robolink.Robolink.Spray_Clear`
        """
        self._check_connection()
        command = 'Gun_SetState'
        self._send_line(command)
        self._send_int(id_spray)
        self._send_int(state)        
        success = self._rec_int()
        self._check_status()
        return success
        
    def Spray_GetStats(self, id_spray=-1):
        """Gets statistics from all simulated spray guns or a specific spray gun.
        
        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave to -1 to apply to all simulated sprays.
        
        .. seealso:: :func:`~robolink.Robolink.Spray_Add`, :func:`~robolink.Robolink.Spray_SetState`, :func:`~robolink.Robolink.Spray_Clear`
        """
        self._check_connection()
        command = 'Gun_Stats'
        self._send_line(command)
        self._send_int(id_spray)
        info = self._rec_line()
        info.replace('<br>','\t')
        print(info)
        data = self._rec_matrix()
        self._check_status()
        return info, data
        
    def Spray_Clear(self, id_spray=-1):
        """Stops simulating a spray gun. This will clear the simulated particles.
        
        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave the default -1 to apply to all simulated sprays.
        
        .. seealso:: :func:`~robolink.Robolink.Spray_Add`, :func:`~robolink.Robolink.Spray_SetState`, :func:`~robolink.Robolink.Spray_GetStats`
        """
        self._check_connection()
        command = 'Gun_Clear'
        self._send_line(command)
        self._send_int(id_spray)
        success = self._rec_int()
        self._check_status()
        return success
        
    def License(self):
        """Get the license string"""
        self._check_connection()
        command = 'G_License'
        self._send_line(command)
        lic_name = self._rec_line()
        self._check_status()
        return lic_name
        
    def Selection(self):
        """Return the list of currently selected items
        
        :return: List of items
        :rtype: list of :class:`.Item`"""
        self._check_connection()
        command = 'G_Selection'
        self._send_line(command)
        nitems = self._rec_int()
        item_list = []
        for i in range(nitems):
            item_list.append(self._rec_item())
        self._check_status()
        return item_list
        
        
    
class Item():
    """The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the station tree.
    An item can also be seen as a node where other items can be attached to (child items).
    Every item has one parent item/node and can have one or more child items/nodes.
    
    RoboDK Items are automatically created and retrieved by generated by :class:`.Robolink` methods such as :func:`~robolink.Robolink.Item` and :func:`~robolink.Robolink.ItemUserPick`
        
    .. seealso:: :func:`~robolink.Robolink.Item`, :func:`~robolink.Robolink.ItemUserPick`
    
    .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                # Get an item named Tool (name in the RoboDK station tree)
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # Get the first available robot
            target = RDK.Item('Target 1', ITEM_TYPE_TARGET)   # Get a target called "Target 1"            
            frame = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)   # Promt the user to select a reference frame
            
            robot.setPoseFrame(frame)
            robot.setPoseTool(tool)            
            robot.MoveJ(target)             # Move the robot to the target using the selected reference frame   
    """
    
    def __init__(self, link, ptr_item=0, itemtype=-1):
        self.item = ptr_item
        self.link = link # it is recommended to keep the link as a reference and not a duplicate (otherwise it will establish a new connection at every call)
        self.type = itemtype

    def __repr__(self):
        if self.Valid():
            return ("RoboDK item (%i) of type %i" % (self.item, int(self.type)))
        else:
            return "RoboDK item (INVALID)"
            
    def __cmp__(self, item2):
        return self.item - item2.item
    
    def equals(self, item2):
        """Returns True if an item is the same as this item :class:`.Item`
        
        :param item2: item to compare
        :type item2: :class:`.Item`
        """
        return self.item == item2.item
    
    def RDK(self):
        """Returns the RoboDK link Robolink(). It is important to have different links (Robolink) for multithreaded applications.
        
        .. seealso:: :func:`~robolink.Robolink.Finish`
        """
        return self.link
    
    #"""Generic item calls"""
    def Type(self):
        """Return the type of the item (robot, object, tool, frame, ...).
        Tip: Compare the returned value against ITEM_TYPE_* variables
        
        .. seealso:: :func:`~robolink.Robolink.Item`        
        """
        self.link._check_connection()
        command = 'G_Item_Type'
        self.link._send_line(command)
        self.link._send_item(self)
        itemtype = self.link._rec_int()
        self.link._check_status()
        return itemtype
        
    def Copy(self):
        """Copy the item to the clipboard (same as Ctrl+C). Use together with Paste() to duplicate items.
        
        .. seealso:: :func:`~robolink.Robolink.Copy`, :func:`~robolink.Item.Paste`
        """
        self.link.Copy(self.item)
        
    def Paste(self):
        """Paste the copied :class:`.Item` from the clipboard as a child of this item (same as Ctrl+V)
        Returns the new item created (pasted)
        
        .. seealso:: :func:`~robolink.Robolink.Copy`, :func:`~robolink.Item.Copy`, :func:`~robolink.Item.Paste`
        """
        return self.link.Paste(self.item)
        
    def AddFile(self, filename):
        """Adds an object attached to this object
        
        :param str filename: file path
        
        .. seealso:: :func:`~robolink.Robolink.AddFile`, :func:`~robolink.Item.Save`
        """
        return self.link.AddFile(filename, self.item)
        
    def Save(self, filename):
        """Save a station or object to a file
        
        :param str filename: file to save. Use *.rdk name for RoboDK stations, *.stl file for objects, *.robot file for robots, ...
        
        .. seealso:: :func:`~robolink.Robolink.AddFile`, :func:`~robolink.Item.AddFile`        
        """
        self.link.Save(filename, self.item)
        
    def Collision(self, item_check):
        """Returns True if this item is in a collision state with another :class:`.Item`, otherwise it returns False.
        
        :param item_check: item to check for collisions
        :type item_check: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.Collision`
        """
        return self.link.Collision(self.item, item_check)
        
    def IsInside(self, object):
        """Return True if the object is inside the provided object
        
        :param object: object to check
        :type object: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.IsInside`
        """
        return self.link.IsInside(self.item, object)

    def AddGeometry(self, fromitem, pose):
        """Makes a copy of the geometry fromitem adding it at a given position (pose), relative to this item."""
        self.link._check_connection()
        command = 'CopyFaces'
        self.link._send_line(command)
        self.link._send_item(fromitem)
        self.link._send_item(self)
        self.link._send_pose(pose)        
        self.link._check_status()
        
    def Delete(self):
        """Remove this item and all its children from the station.
        
        .. seealso:: :func:`~robolink.Robolink.AddFile`, :func:`~robolink.Robolink.Item`
        """
        self.link._check_connection()
        command = 'Remove'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
        self.item = 0

    def Valid(self):
        """Checks if the item is valid.
        Returns True if the item is valid or False if the item is not valid.
        An invalid item will be returned by an unsuccessful function call (wrong name or because an item was deleted)
        
        .. seealso:: :func:`~robolink.Robolink.Item`
        
        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                # Retrieve an item named tool
            if not tool.Valid():
                print("The tool item does not exist!")
                quit()
        """
        if self.item == 0: return False
        return True
    
    def setParent(self, parent):
        """Attaches the item to a new parent while maintaining the relative position with its parent.
        The absolute position is changed.
        
        :param parent: parent to attach the item
        :type parent: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.setParentStatic`
        """
        self.link._check_connection()
        command = 'S_Parent'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_item(parent)
        self.link._check_status()
        
    def setParentStatic(self, parent):
        """Attaches the item to another parent while maintaining the current absolute position in the station.
        The relationship between this item and its parent is changed to maintain the abosolute position.
        
        :param parent: parent to attach the item
        :type parent: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.setParent`
        """
        self.link._check_connection()
        command = 'S_Parent_Static'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_item(parent)
        self.link._check_status()

    def AttachClosest(self):
        """Attach the closest object to the tool.
        Returns the item that was attached.
        Use item.Valid() to check if an object was attached to the tool.
        
        .. seealso:: :func:`~robolink.Item.setParentStatic`
        """
        self.link._check_connection()
        command = 'Attach_Closest'
        self.link._send_line(command)
        self.link._send_item(self)
        item_attached = self.link._rec_item()
        self.link._check_status()
        return item_attached

    def DetachClosest(self, parent=0):
        """Detach the closest object attached to the tool (see also: setParentStatic).
        
        :param parent: New parent item to attach, such as a reference frame (optional). If not provided, the items held by the tool will be placed at the station root.
        :type parent: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.setParentStatic`
        """
        self.link._check_connection()
        command = 'Detach_Closest'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_item(parent)
        item_detached = self.link._rec_item()
        self.link._check_status()
        return item_detached        

    def DetachAll(self, parent=0):
        """Detaches any object attached to a tool.
        
        :param parent: New parent item to attach, such as a reference frame (optional). If not provided, the items held by the tool will be placed at the station root.
        :type parent: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.setParentStatic`
        """
        self.link._check_connection()
        command = 'Detach_All'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_item(parent)
        self.link._check_status()

    def Parent(self):
        """Return the parent item of this item (:class:`.Item`)
        
        .. seealso:: :func:`~robolink.Item.Childs`
        """
        self.link._check_connection()
        command = 'G_Parent'
        self.link._send_line(command)
        self.link._send_item(self)
        parent = self.link._rec_item()
        self.link._check_status()
        return parent

    def Childs(self):
        """Return a list of the childs items (list of :class:`.Item`) that are attached to this item.
        
        .. seealso:: :func:`~robolink.Item.Parent`
        """
        self.link._check_connection()
        command = 'G_Childs'
        self.link._send_line(command)
        self.link._send_item(self)
        nitems = self.link._rec_int()
        itemlist = []
        for i in range(nitems):
            itemlist.append(self.link._rec_item())
        self.link._check_status()
        return itemlist

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def Visible(self):
        """Returns 1 if the item is visible, otherwise it returns 0.
        
        .. seealso:: :func:`~robolink.Item.setVisible`
        """
        self.link._check_connection()
        command = 'G_Visible'
        self.link._send_line(command)
        self.link._send_item(self)
        visible = self.link._rec_int()
        self.link._check_status()
        return visible

    def setVisible(self, visible, visible_frame=None):
        """Sets the item visiblity
        
        :param visible: Set the object as visible (1/True) or invisible (0/False)
        :type visible: bool
        :param visible_frame: Set the reference frame as visible (1/True ) or invisible (0/False)
        :type visible_frame: bool
        
        .. seealso:: :func:`~robolink.Item.Visible`
        """        
        if visible_frame is None: visible_frame = visible
        self.link._check_connection()
        command = 'S_Visible'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(visible)
        self.link._send_int(visible_frame)
        self.link._check_status()

    def Name(self):
        """Returns the item name. The name of the item is always displayed in the RoboDK station tree. 
        Returns the name as a string (str)
        
        :return: New item name
        :rtype: str
        
        .. seealso:: :func:`~robolink.Item.setName`
        """
        self.link._check_connection()
        command = 'G_Name'
        self.link._send_line(command)
        self.link._send_item(self)
        name = self.link._rec_line()
        self.link._check_status()
        return name

    def setName(self, name):
        """Set the name of the item. The name of the item will be displayed in the station tree. 
        
        :param str name: New item name
        
        .. seealso:: :func:`~robolink.Item.Name`
        """
        self.link._check_connection()
        command = 'S_Name'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(name)
        self.link._check_status()
        
    def setValue(self, varname, value):
        """Set a specific property name to a given value. This is reserved for internal purposes and future compatibility.
        
        :param str varname: property name
        :param str value: property value
        """
        self.link._check_connection()
        if isinstance(value, Mat):
            command = 'S_Gen_Mat'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(varname)
            self.link._send_matrix(value)
        elif isinstance(value,str):
            command = 'S_Gen_Str'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(varname)
            self.link._send_line(value)
        else:
            raise Exception("Unsupported value type")
        self.link._check_status()
        
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def setPose(self, pose):
        """Set the position (pose) of the item with respect to its parent (item it is attached to).
        For example, the position of an object, frame or target with respect to its parent reference frame.
        
        :param pose: pose of the item with respect to its parent
        :type pose: :class:`.Mat`
        
        .. seealso:: :func:`~robolink.Item.Pose`, :func:`~robolink.Item.setPoseTool`, :func:`~robolink.Item.setPoseFrame`, :func:`~robolink.Robolink.Item`
        """
        self.link._check_connection()
        command = 'S_Hlocal'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_pose(pose)
        self.link._check_status()

    def Pose(self):
        """Returns the relative position (pose) of an object, target or reference frame. For example, the position of an object, target or reference frame with respect to its parent.
        If a robot is provided, it will provide the pose of the end efector with respect to the robot base (same as PoseTool())
        Returns the pose as :class:`.Mat`. 
        
        Tip: Use a Pose_2_* function from the robodk module (such as :class:`robodk.Pose_2_KUKA`) to convert the pose to XYZABC (XYZ position in mm and ABC orientation in degrees), specific to a robot brand.
        
        Example: :ref:`weldexample`
        
        .. seealso:: :func:`~robolink.Item.Pose`, :func:`~robolink.Item.PoseTool`, :func:`~robolink.Item.PoseFrame`, :func:`~robolink.Robolink.Item`
        """
        self.link._check_connection()
        command = 'G_Hlocal'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose
        
    def setGeometryPose(self, pose):
        """Set the position (pose) the object geometry with respect to its own reference frame. This can be applied to tools and objects.
        The pose must be a :class:`.Mat`"""
        self.link._check_connection()
        command = 'S_Hgeom'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_pose(pose)
        self.link._check_status()

    def GeometryPose(self):
        """Returns the position (pose as :class:`.Mat`) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        """
        self.link._check_connection()
        command = 'G_Hgeom'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose

    def setPoseAbs(self, pose):
        """Sets the position of the item given the pose (:class:`.Mat`) with respect to the absolute reference frame (station reference)
        
        :param pose: pose of the item with respect to the station reference
        :type pose: :class:`.Mat`
        
        .. seealso:: :func:`~robolink.Item.PoseAbs`, :func:`~robolink.Item.setPose`
        """
        self.link._check_connection()
        command = 'S_Hlocal_Abs'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_pose(pose)
        self.link._check_status()

    def PoseAbs(self):
        """Return the position (:class:`.Mat`) of this item given the pose with respect to the absolute reference frame (station reference)
        For example, the position of an object/frame/target with respect to the origin of the station.
        
        .. seealso:: :func:`~robolink.Item.setPoseAbs`, :func:`~robolink.Item.Pose`
        """
        self.link._check_connection()
        command = 'G_Hlocal_Abs'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose

    def Recolor(self, tocolor, fromcolor=None, tolerance=None):
        """Changes the color of an :class:`.Item` (object, tool or robot).
        Colors must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.

        :param tocolor: color to set
        :type tocolor: list of float
        :param fromcolor: color to change
        :type fromcolor: list of float
        :param tolerance: tolerance to replace colors (set to 0 for exact match)
        :type tolerance: float (defaults to 0.1)
        
        .. seealso:: :func:`~robolink.Item.setColor`
        """
        self.link._check_connection()
        if not fromcolor:
            fromcolor = [0,0,0,0]
            tolerance = 2
        elif not tolerance:
            tolerance= 0.1
        if not (isinstance(tolerance,int) or isinstance(tolerance,float)):
            raise Exception("tolerance must be a scalar")
            
        tocolor = self.link._check_color(tocolor)
        fromcolor = self.link._check_color(fromcolor)
        command = 'Recolor'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array([tolerance] + fromcolor + tocolor)
        self.link._check_status()
        
    def setColor(self, tocolor):
        """Set the color of an object, tool or robot. 
        A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        
        :param tocolor: color to set
        :type tocolor: list of float
        
        .. seealso:: :func:`~robolink.Item.Color`, :func:`~robolink.Item.Recolor`
        """
        self.link._check_connection()            
        tocolor = self.link._check_color(tocolor)
        command = 'S_Color'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array(tocolor)
        self.link._check_status()
        
    def Color(self):
        """Return the color of an :class:`.Item` (object, tool or robot). If the item has multiple colors it returns the first color available). 
        A color is in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        
        .. seealso:: :func:`~robolink.Item.setColor`, :func:`~robolink.Item.Recolor`
        """
        self.link._check_connection()            
        command = 'G_Color'
        self.link._send_line(command)
        self.link._send_item(self)
        color = self.link._rec_array()
        self.link._check_status()
        return color.tolist()
    
    def Scale(self, scale):
        """Apply a scale to an object to make it bigger or smaller.
        The scale can be uniform (if scale is a float value) or per axis (if scale is an array/list [scale_x, scale_y, scale_z]).
        
        :param scale: scale parameter (1 means no change)
        :type scale: float or list of 3 float [scale_x, scale_y, scale_z]"""
        self.link._check_connection()
        if isinstance(scale,float) or isinstance(scale,int):
            scale = [scale, scale, scale]
        elif len(scale) > 3:
            scale = scale[:3]
        elif len(scale) < 3:
            raise Exception("scale must be a single value or a 3-vector value")
        command = 'Scale'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array(scale)
        self.link._check_status()
        
    #"""Object specific calls"""
    def AddShape(self, triangle_points):
        """Adds a shape to the object provided some triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be optionally provided.
        
        .. seealso:: :func:`~robolink.Robolink.AddShape`
        """
        return self.link.AddShape(triangle_points, self)
    
    def AddCurve(self, curve_points, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        
        .. seealso:: :func:`~robolink.Robolink.AddCurve`
        """
        return self.link.AddCurve(curve_points, self, add_to_ref, projection_type)        
    
    def AddPoints(self, points, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.

        .. seealso:: :func:`~robolink.Robolink.AddPoints`
        """
        return self.link.AddPoints(points, self, add_to_ref, projection_type)        
        
    def ProjectPoints(self, points, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Projects a point or a list of points to the object given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
        
        .. seealso:: :func:`~robolink.Robolink.ProjectPoints`
        """
        return self.link.ProjectPoints(points, self, projection_type)
        
            
    def SelectedFeature(self):
        """Retrieve the currently selected feature for this object.
        
        .. seealso:: :func:`~robolink.Robolink.GetPoints`
        
        Example:
        
        .. code-block:: python
            
            # Show the point selected
            object = RDK.Item('Object', ITEM_TYPE_OBJECT)
            is_selected, feature_type, feature_id = OBJECT.SelectedFeature()
            
            points, name_selected = object.GetPoints(feature_type, feature_id)
            point = None
            if len(points) > 1:
                point = points[feature_id]
            else:
                point = points[0]
                
            RDK.ShowMessage("Selected Point: %s = [%.3f, %.3f, %.3f]" % (name_selected, point[0], point[1], point[2]))

        """
        self.link._check_connection()
        command = 'G_ObjSelection'
        self.link._send_line(command)
        self.link._send_item(self)        
        is_selected = self.link._rec_int()
        feature_type = self.link._rec_int()
        feature_id = self.link._rec_int()
        self.link._check_status()
        return is_selected, feature_type, feature_id
        
    def GetPoints(self, feature_type=FEATURE_SURFACE, feature_id=0):
        """Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format, where the XYZ is the point coordinate and ijk is the surface normal.
        
        :param int feature_type: set to FEATURE_SURFACE to retrieve the point under the mouse cursor, FEATURE_CURVE to retrieve the list of points for that wire, or FEATURE_POINT to retrieve the list of points.
        :param int feature_id:  used only if FEATURE_CURVE is specified, it allows retrieving the appropriate curve id of an object
        
        :return: List of points
        
        .. seealso:: :func:`~robolink.Item.SelectedFeature`
        """
        self.link._check_connection()
        command = 'G_ObjPoint'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(feature_type)
        self.link._send_int(feature_id)        
        points = self.link._rec_matrix()
        feature_name = self.link._rec_line()
        self.link._check_status()
        return points.tr().rows, feature_name
   
    def setMillingParameters(self, ncfile='', part=0, params=''):
        """Adds a new robot machining project. Machining projects can also be used for 3D printing, curve following and point following.
        It returns the new project item created and the status.
        
        :param str ncfile: path to the NC file to loaded
        :param part: object holding curves or points to automatically set up a curve/point follow project
        :type part: :class:`.Item`
        :param params: Additional options
        
        .. seealso:: :func:`~robolink.Robolink.AddMillingProject`, :func:`~robolink.Item.Joints`, :func:`~robolink.Item.getLink`, :func:`~robolink.Item.setJoints`, :func:`~robolink.Item.setToolPose`, :func:`~robolink.Item.setFramePose`
        
        Example:
        
        .. code-block:: python
        
            object_curve = RDK.AddCurve(POINTS)
            object_curve.setName('AutoPoints n%i' % NUM_POINTS)
            path_settings = RDK.AddMillingProject("AutoCurveFollow settings")
            prog, status = path_settings.setMillingParameters(part=object_curve)
        
        """
        self.link._check_connection()
        command = 'S_MachiningParams'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(ncfile)
        self.link._send_item(part)
        self.link._send_line(params)
        self.link.COM.settimeout(3600)
        newprog = self.link._rec_item()
        self.link.COM.settimeout(self.link.TIMEOUT)
        status = self.link._rec_int()/1000.0
        self.link._check_status()
        return newprog, status
        
    #"""Target item calls"""
    def setAsCartesianTarget(self):
        """Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
        
        .. seealso:: :func:`~robolink.Robolink.AddTarget`, :func:`~robolink.Item.setPose`, :func:`~robolink.Robolink.setAsJointTarget`
        """
        self.link._check_connection()
        command = 'S_Target_As_RT'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
    
    def setAsJointTarget(self):
        """Sets a target as a joint target. A joint target moves to the joint position without taking into account the cartesian coordinates.
        
        .. seealso:: :func:`~robolink.Robolink.AddTarget`, :func:`~robolink.Item.setPose`, :func:`~robolink.Robolink.setAsCartesianTarget`
        """
        self.link._check_connection()
        command = 'S_Target_As_JT'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
    
    #"""Robot item calls"""
    def Joints(self):
        """Return the current joint position as a :class:`.Mat` of a robot or the joints of a target. 
        If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
        
        .. seealso:: :func:`~robolink.Item.setJoints`, :func:`~robolink.Item.MoveJ`
        
        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started)
            tool  = RDK.Item('', ITEM_TYPE_ROBOT)   # Retrieve the robot
            joints = robot.Joints().list()          # retrieve the current robot joints as a list
            joints[5] = 0                           # set joint 6 to 0 deg
            robot.MoveJ(joints)                     # move the robot to the new joint position
            
        """
        self.link._check_connection()
        command = 'G_Thetas'
        self.link._send_line(command)
        self.link._send_item(self)
        joints = self.link._rec_array()
        self.link._check_status()
        return joints
        
    def SimulatorJoints(self):
        """Return the current joint position of a robot (only from the simulator, never from the real robot).
        This should be used only when RoboDK is connected to the real robot and only the simulated robot needs to be retrieved (for example, if we want to move the robot using a spacemouse).
        
        Note: Use robot.Joints() instead to retrieve the simulated and real robot position when connected.
        
        .. seealso:: :func:`~robolink.Item.Joints`
        """
        self.link._check_connection()
        command = 'G_Thetas_Sim'
        self.link._send_line(command)
        self.link._send_item(self)
        joints = self.link._rec_array()
        self.link._check_status()
        return joints.list()
        
    def JointPoses(self, joints = None):
        """Returns the positions of the joint links for a provided robot configuration (joints). If no joints are provided it will return the poses for the current robot position.
        Out 1 : 4x4 x n -> array of 4x4 homogeneous matrices. Index 0 is the base frame reference (it never moves when the joints move).
        """
        self.link._check_connection()
        command = 'G_LinkPoses'
        self.link._send_line(command)
        self.link._send_item(self)
        if joints is None:
            self.link._send_array([])
        else:
            self.link._send_array(joints)
            
        nlinks = self.link._rec_int()
        poses = []
        for i in range(nlinks):
            poses.append(self.link._rec_pose())
            
        self.link._check_status()
        return poses
    
    def JointsHome(self):
        """Return the home joints of a robot. 
        The home joints can be manually set in the robot "Parameters" menu of the robot panel in RoboDK, then select "Set home position".
        
        .. seealso:: :func:`~robolink.Item.Joints`
        """
        self.link._check_connection()
        command = 'G_Home'
        self.link._send_line(command)
        self.link._send_item(self)
        joints = self.link._rec_array()
        self.link._check_status()
        return joints
        
    def ObjectLink(self, link_id=0):
        """Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.
        
        :param int link_id: link index (0 for the robot base, 1 for the first link, ...)        
        """
        self.link._check_connection()
        command = 'G_LinkObjId'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(link_id)
        item = self.link._rec_item()
        self.link._check_status()
        return item
        
    def getLink(self, type_linked=ITEM_TYPE_ROBOT):
        """Returns an item pointer (:class:`.Item`) to a robot, object, tool or program. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
        
        :param int type_linked: type of linked object to retrieve
        
        """
        self.link._check_connection()
        command = 'G_LinkType'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(type_linked)
        item = self.link._rec_item()
        self.link._check_status()
        return item
    
    def setJoints(self, joints):
        """Set the current joints of a robot or a target. If robot joints are set, the robot position will be updated on the screen.        
        
        :param joints: robot joints
        :type joints: list of float or :class:`.Mat`
        
        .. seealso:: :func:`~robolink.Item.Joints`
        """
        self.link._check_connection()
        command = 'S_Thetas'
        self.link._send_line(command)
        self.link._send_array(joints)
        self.link._send_item(self)
        self.link._check_status()
        
    def JointLimits(self):
        """Retrieve the joint limits of a robot. Returns (lower limits, upper limits, joint type).
        
        .. seealso:: :func:`~robolink.Item.setJointLimits`
        """
        self.link._check_connection()
        command = 'G_RobLimits'
        self.link._send_line(command)
        self.link._send_item(self)
        lim_inf = self.link._rec_array()
        lim_sup = self.link._rec_array()        
        joints_type = self.link._rec_int()/1000.0
        self.link._check_status()
        return lim_inf, lim_sup, joints_type
        
    def setJointLimits(self, lower_limit, upper_limit):
        """Update the robot joint limits
        
        :param lower_limit: lower joint limits
        :type lower_limit: list of float
        :param upper_limit: upper joint limits
        :type upper_limit: list of float
        
        .. seealso:: :func:`~robolink.Item.JointLimits`
        """
        self.link._check_connection()
        command = 'S_RobLimits'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array(lower_limit)
        self.link._send_array(upper_limit)        
        self.link._check_status()
            
    def setRobot(self, robot=None):
        """Assigns a specific robot to a program, target or robot machining project. 
        
        :param robot: robot to link
        :type robot: :class:`.Item`
        """
        if robot is None:
            robot = Item(self.link)
        self.link._check_connection()
        command = 'S_Robot'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_item(robot)
        self.link._check_status()
        
    def setPoseFrame(self, frame):
        """Sets the reference frame of a robot (user frame). The frame can be an item or a 4x4 Matrix
        
        :param frame: robot reference frame as an item, or a pose
        :type frame: :class:`.Mat` or :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.PoseFrame`, :func:`~robolink.Item.setPose`, :func:`~robolink.Item.setPoseTool`
        """
        self.link._check_connection()
        if isinstance(frame,Item):
            command = 'S_Frame_ptr'
            self.link._send_line(command)
            self.link._send_item(frame)
        else:
            command = 'S_Frame'
            self.link._send_line(command)
            self.link._send_pose(frame)
        self.link._send_item(self)
        self.link._check_status()
        
    def setPoseTool(self, tool):
        """Set the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
        
        :param tool: robot tool as an item, or a pose
        :type tool: :class:`.Mat` or :class:`.Item`
        
        .. seealso:: :func:`~robolink.Item.PoseTool`, :func:`~robolink.Item.setPose`, :func:`~robolink.Item.setPoseFrame`"""
        self.link._check_connection()
        if isinstance(tool,Item):
            command = 'S_Tool_ptr'
            self.link._send_line(command)
            self.link._send_item(tool)
        else:
            command = 'S_Tool'
            self.link._send_line(command)
            self.link._send_pose(tool)        
        self.link._send_item(self)
        self.link._check_status()
        
    def PoseTool(self):
        """Returns the pose (:class:`.Mat`) of the robot tool (TCP) with respect to the robot flange
        
        .. seealso:: :func:`~robolink.Item.setPoseTool`, :func:`~robolink.Item.Pose`, :func:`~robolink.Item.PoseFrame`
        """
        self.link._check_connection()
        command = 'G_Tool'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose
        
    def PoseFrame(self):
        """Returns the pose (:class:`.Mat`) of the robot reference frame with respect to the robot base
        
        .. seealso:: :func:`~robolink.Item.setPoseFrame`, :func:`~robolink.Item.Pose`, :func:`~robolink.Item.PoseTool`
        """
        self.link._check_connection()
        command = 'G_Frame'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose    
        
    # Obsolete methods -----------------------   
    def Htool(self):
        """Obsolete. Use :func:`~robolink.Item.PoseTool` instead. Returns the pose (:class:`.Mat`) of the robot tool (TCP) with respect to the robot flange"""
        return self.PoseTool()
        
    def Tool(self):
        """Obsolete. Use :func:`~robolink.Item.PoseTool` instead. Returns the pose (:class:`.Mat`) of the robot tool (TCP) with respect to the robot flange"""
        return self.PoseTool()
        
    def Frame(self):
        """Obsolete. Use :func:`~robolink.Item.PoseFrame` instead. Returns the pose (:class:`.Mat`) of the robot reference frame with respect to the robot base"""
        return self.PoseFrame()
        
    def setHtool(self, tool):
        """Obsolete. :func:`~robolink.Item.setPoseTool` instead. Sets the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
        """
        self.setPoseTool(tool)
    
    def setTool(self, tool):
        """Obsolete. Use :func:`~robolink.Item.setPoseTool` instead. Sets the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
        """
        self.setPoseTool(tool)
        
    def setFrame(self, frame):
        """Obsolete. Use :func:`~robolink.Item.setPoseFrame` instead. Sets the reference frame of a robot (user frame). The frame can be an item or a 4x4 Matrix
        """
        self.setPoseFrame(frame)
    # -----------------------
     
    def AddTool(self, tool_pose, tool_name = 'New TCP'):
        """Add a tool to a robot given the tool pose and the tool name. It returns the tool as an :class:`.Item`.
        
        :param tool_pose: Tool pose (TCP) of the tool with respect to the robot flange
        :type tool_pose: :class:`.Mat`
        :param str tool_name: name of the tool
        
        .. seealso:: :func:`~robolink.Item.AddFrame`, :func:`~robolink.Item.PoseTool`, :func:`~robolink.Item.setPoseTool`
        """
        self.link._check_connection()
        command = 'AddToolEmpty'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_pose(tool_pose)
        self.link._send_line(tool_name)
        newtool = self.link._rec_item()
        self.link._check_status()
        return newtool
    
    def SolveFK(self, joints):
        """Calculate the forward kinematics of the robot for the provided joints.
        Returns the pose of the robot flange with respect to the robot base reference (:class:`.Mat`).
        
        :param joints: robot joints
        :type joints: list of float or :class:`.Mat`
        
        .. seealso:: :func:`~robolink.Item.SolveIK`, :func:`~robolink.Item.SolveIK_All`, :func:`~robolink.Item.JointsConfig`
        
        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library        
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            robot  = RDK.Item('', ITEM_TYPE_ROBOT)  # Retrieve the robot
            
            # get the current robot joints
            robot_joints = robot.Joints()

            # get the robot position from the joints (calculate forward kinematics)
            robot_position = robot.SolveFK(robot_joints)

            # get the robot configuration (robot joint state)
            robot_config = robot.JointsConfig(robot_joints)

            # calculate the new robot position
            new_robot_position = transl([x_move,y_move,z_move])*robot_position

            # calculate the new robot joints
            new_robot_joints = robot.SolveIK(new_robot_position)
            if len(new_robot_joints.tolist()) < 6:
                print("No robot solution!! The new position is too far, out of reach or close to a singularity")
                continue

            # calculate the robot configuration for the new joints
            new_robot_config = robot.JointsConfig(new_robot_joints)

            if robot_config[0] != new_robot_config[0] or robot_config[1] != new_robot_config[1] or robot_config[2] != new_robot_config[2]:
                print("Warning! Robot configuration changed: this may lead to unextected movements!")
                print(robot_config)
                print(new_robot_config)

            # move the robot to the new position
            robot.MoveJ(new_robot_joints)
            #robot.MoveL(new_robot_joints)
        """
        self.link._check_connection()
        command = 'G_FK'
        self.link._send_line(command)
        self.link._send_array(joints)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose
    
    def JointsConfig(self, joints):
        """Returns the robot configuration state for a set of robot joints. 
        The configuration state is defined as: [REAR, LOWERARM, FLIP]
        
        :param joints: robot joints
        :type joints: list of float
        
        .. seealso:: :func:`~robolink.Item.SolveFK`, :func:`~robolink.Item.SolveIK`
        """
        self.link._check_connection()
        command = 'G_Thetas_Config'
        self.link._send_line(command)
        self.link._send_array(joints)
        self.link._send_item(self)
        config = self.link._rec_array()
        self.link._check_status()
        return config
    
    def SolveIK(self, pose, joints_approx = None):
        """Calculates the inverse kinematics for the specified pose. 
        It returns the joints solution as a list of floats which are the closest match to the current robot configuration (see SolveIK_All()).
        Optionally, specify a preferred robot position using the parameter joints_approx.
        
        :param pose: pose of the robot flange with respect to the robot base frame
        :type pose: :class:`.Mat`
        :param joints_approx: approximate solution. Leave blank to return the closest match to the current robot position.
        :type joints_approx: list of float
        
        .. seealso:: :func:`~robolink.Item.SolveFK`, :func:`~robolink.Item.SolveIK_All`, :func:`~robolink.Item.JointsConfig`
        """
        self.link._check_connection()
        if joints_approx is None:
            command = 'G_IK'
            self.link._send_line(command)
            self.link._send_pose(pose)
            self.link._send_item(self)
            joints = self.link._rec_array()
        else:
            command = 'G_IK_jnts'
            self.link._send_line(command)
            self.link._send_pose(pose)
            self.link._send_array(joints_approx)
            self.link._send_item(self)
            joints = self.link._rec_array()        
        self.link._check_status()
        return joints
    
    def SolveIK_All(self, pose):
        """Calculates the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
        Returns a list of joints as a 2D matrix (float x n x m)
        
        :param pose: pose of the robot flange with respect to the robot base frame
        :type pose: :class:`.Mat`
        
        .. seealso:: :func:`~robolink.Item.SolveFK`, :func:`~robolink.Item.SolveIK`, :func:`~robolink.Item.JointsConfig`"""
        self.link._check_connection()
        command = 'G_IK_cmpl'
        self.link._send_line(command)
        self.link._send_pose(pose)
        self.link._send_item(self)
        joints_list = self.link._rec_matrix()
        self.link._check_status()
        return joints_list
        
    def FilterTarget(self, pose, joints_approx=None):
        """Filters a target to improve accuracy. This option requires a calibrated robot.
        :param pose: pose of the robot TCP with respect to the robot reference frame
        :type pose: :class:`.Mat`
        :param joints_approx: approximated desired joints to define the preferred configuration
        :type joints_approx: list of float or :class:`.Mat`"""
        self.link._check_connection()
        command = 'FilterTarget'
        self.link._send_line(command)
        self.link._send_pose(pose)
        if joints_approx is None:
            joints_approx = [0,0,0,0,0,0]
        self.link._send_array(joints_approx)
        self.link._send_item(self)
        pose_filtered = self.link._rec_pose()
        joints_filtered = self.link._rec_array()
        self.link._check_status()
        return pose_filtered, joints_filtered
    
    def Connect(self, robot_ip = ''):
        """Connect to a real robot and wait for a connection to succeed. Returns 1 if connection succeeded, or 0 if it failed.
        
        :param robot_ip: Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
        :type robot_ip: str
        
        .. seealso:: :func:`~robolink.Item.ConnectSafe`, :func:`~robolink.Item.ConnectedState`, :func:`~robolink.Item.Disconnect`, :func:`~robolink.Robolink.setRunMode`
        """
        self.link._check_connection()
        command = 'Connect'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(robot_ip)        
        status = self.link._rec_int()
        self.link._check_status()
        return status
        
    def ConnectSafe(self, robot_ip = '', max_attempts=5, wait_connection=4):
        """Connect to a real robot and wait for a connection to succeed. Returns 1 if connection succeeded 0 if it failed.
        
        :param robot_ip: Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
        :type robot_ip: str
        :param max_attempts: maximum connection attemps before reporting an unsuccessful connection
        :type max_attempts: int
        :param wait_connection: time to wait in seconds between connection attempts
        :type wait_connection: float
        
        .. seealso:: :func:`~robolink.Item.Connect`, :func:`~robolink.Item.ConnectedState`, :func:`~robolink.Robolink.setRunMode`
        """    
        trycount = 0
        refresh_rate = 0.5
        self.Connect()
        tic()
        timer1 = toc()
        pause(refresh_rate)
        while True:
            con_status, status_msg = self.ConnectedState()
            print(status_msg)
            if con_status == ROBOTCOM_READY:
                print(status_msg)
                break
            elif con_status == ROBOTCOM_DISCONNECTED:
                print('Trying to reconnect...')
                self.Connect()
            if toc() - timer1 > wait_connection:
                timer1 = toc()
                self.Disconnect()
                trycount = trycount + 1
                if trycount >= max_attempts:
                    print('Failed to connect: Timed out')
                    break
                print('Retrying connection...')
            pause(refresh_rate)
        return con_status

        
    def ConnectionParams(self):
        """Returns the robot connection parameters
        :return: [robotIP (str), port (int), remote_path (str), FTP_user (str), FTP_pass (str)]
        
        .. seealso:: :func:`~robolink.Item.setConnectionParams`, :func:`~robolink.Item.Connect`, :func:`~robolink.Item.ConnectSafe`
        """
        self.link._check_connection()
        command = 'ConnectParams'
        self.link._send_line(command)
        self.link._send_item(self)
        robot_ip = self.link._rec_line()
        port = self.link._rec_int()
        remote_path = self.link._rec_line()
        ftp_user = self.link._rec_line()
        ftp_pass = self.link._rec_line()
        self.link._check_status()
        return robot_ip, port, remote_path, ftp_user, ftp_pass
        
    def setConnectionParams(self, robot_ip, port, remote_path, ftp_user, ftp_pass):
        """Retrieve robot connection parameters
        
        :param robot_ip: robot IP
        :type robot_ip: str
        :param port: robot communication port
        :type port: int
        :param remote_path: path to transfer files on the robot controller
        :type remote_path: str
        :param ftp_user: user name for the FTP connection
        :type ftp_user: str
        :param ftp_pass: password credential for the FTP connection
        :type ftp_pass: str
        
        .. seealso:: :func:`~robolink.Item.ConnectionParams`, :func:`~robolink.Item.Connect`, :func:`~robolink.Item.ConnectSafe`
        """
        self.link._check_connection()
        command = 'setConnectParams'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(robot_ip)
        self.link._send_int(port)
        self.link._send_line(remote_path)
        self.link._send_line(ftp_user)
        self.link._send_line(ftp_pass)
        self.link._check_status()
        
    def ConnectedState(self):
        """Check connection status with a real robobt
        Out 1 : status code -> (int) ROBOTCOM_READY if the robot is ready to move, otherwise, status message will provide more information about the issue
        Out 2 : status message -> Message description of the robot status
        
        .. seealso:: :func:`~robolink.Item.ConnectionParams`, :func:`~robolink.Item.Connect`, :func:`~robolink.Item.ConnectSafe`

        Example:
        
        .. code-block:: python
            
            from robolink import *                  # import the robolink library
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # Get the first robot available
            state = robot.Connect()
            print(state)
            
            # Check the connection status and message
            state, msg = robot.ConnectedState()
            print(state)
            print(msg)
            if state != ROBOTCOM_READY:
                print('Problems connecting: ' + robot.Name() + ': ' + msg)
                quit()

            # Move the robot (real robot if we are connected)
            robot.MoveJ(jnts, False)            
        
        """
        self.link._check_connection()
        command = 'ConnectedState'
        self.link._send_line(command)
        self.link._send_item(self)
        robotcom_status = self.link._rec_int()
        status_msg = self.link._rec_line()        
        self.link._check_status()
        return robotcom_status, status_msg
        
    def Disconnect(self):
        """Disconnect from a real robot (when the robot driver is used)
        Returns 1 if it disconnected successfully, 0 if it failed. It can fail if it was previously disconnected manually for example.
        
        .. seealso:: :func:`~robolink.Item.Connect`, :func:`~robolink.Item.ConnectedState`
        """
        self.link._check_connection()
        command = 'Disconnect'
        self.link._send_line(command)
        self.link._send_item(self)
        status = self.link._rec_int()
        self.link._check_status()
        return status
    
    def MoveJ(self, target, blocking=True):
        """Move a robot to a specific target ("Move Joint" mode). This function waits (blocks) until the robot finishes its movements.
        
        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool
        
        .. seealso:: :func:`~robolink.Item.MoveL`, :func:`~robolink.Item.MoveC`, :func:`~robolink.Item.SearchL`
        """
        self.link._moveX(target, self, 1, blocking)
    
    def MoveL(self, target, blocking=True):
        """Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements.
        
        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool
        
        .. seealso:: :func:`~robolink.Item.MoveJ`, :func:`~robolink.Item.MoveC`, :func:`~robolink.Item.SearchL`
        """
        self.link._moveX(target, self, 2, blocking)
        
    def SearchL(self, target, blocking=True):
        """Moves a robot to a specific target and stops when a specific input switch is detected ("Search Linear" mode). This function waits (blocks) until the robot finishes its movements.
        
        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool
        
        .. seealso:: :func:`~robolink.Item.MoveJ`, :func:`~robolink.Item.MoveL`, :func:`~robolink.Item.MoveC`
        """
        self.link._moveX(target, self, 5, blocking)
        return self.SimulatorJoints()
        
    def MoveC(self, target1, target2, blocking=True):
        """Move a robot to a specific target ("Move Circular" mode). By default, this procedure waits (blocks) until the robot finishes the movement.
    
        :param target1: pose along the cicle movement
        :type target1: :class:`.Mat`, list of joints or :class:`.Item`
        :param target2: final circle target
        :type target2: :class:`.Mat`, list of joints or :class:`.Item`
        :param blocking: True if the instruction should wait until the robot finished the movement (default=True)
        :type blocking: bool
        
        .. seealso:: :func:`~robolink.Item.MoveL`, :func:`~robolink.Item.MoveC`, :func:`~robolink.Item.SearchL`
        """
        self.link.MoveC(target1, target2, self, blocking)
    
    def MoveJ_Test(self, j1, j2, minstep_deg=-1):
        """Checks if a joint movement is feasible and free of collision (if collision checking is activated).
        
        :param j1: start joints
        :type j1: list of float
        :param j2: end joints
        :type j2: list of float
        :param float minstep_deg: joint step in degrees
        :return: returns 0 if the movement is free of collision or any other issues. Otherwise it returns the number of pairs of objects that collided if there was a collision.
        :rtype: int

        .. seealso:: :func:`~robolink.Item.MoveL_Test`, :func:`~robolink.Robolink.setCollisionActive`, :func:`~robolink.Item.MoveJ`
        """
        self.link._check_connection()
        command = 'CollisionMove'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array(j1)
        self.link._send_array(j2)        
        self.link._send_int(minstep_deg*1000)
        self.link.COM.settimeout(3600) # wait up to 1 hour  
        collision = self.link._rec_int()
        self.link.COM.settimeout(self.link.TIMEOUT)
        self.link._check_status()
        return collision
    
    def MoveL_Test(self, j1, pose, minstep_mm=-1):
        """Checks if a linear movement is feasible and free of collision (if collision checking is activated).
        
        :param j1: start joints
        :type j1: list of float
        :param pose: end pose (position of the active tool with respect to the active reference frame)
        :type pose: :class:`.Mat`
        :param float minstep_mm: linear step in mm
        :return: returns 0 if the movement is free of collision or any other issues.
        :rtype: int
        
        If the robot can not reach the target pose it returns -2. If the robot can reach the target but it can not make a linear movement it returns -1.
        
        .. seealso:: :func:`~robolink.Item.MoveJ_Test`, :func:`~robolink.Item.setFramePose`, :func:`~robolink.Item.setToolPose`, :func:`~robolink.Robolink.setCollisionActive`, :func:`~robolink.Item.MoveL`
        """
        self.link._check_connection()
        command = 'CollisionMoveL'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array(j1)
        self.link._send_pose(pose)        
        self.link._send_int(minstep_mm*1000)
        self.link.COM.settimeout(3600) # wait up to 1 hour  
        collision = self.link._rec_int()
        self.link.COM.settimeout(self.link.TIMEOUT)
        self.link._check_status()
        return collision
    
    def setSpeed(self, speed_linear, speed_joints=-1, accel_linear=-1, accel_joints=-1):
        """Sets the linear speed of a robot. Additional arguments can be provided to set linear acceleration or joint speed and acceleration.
        
        :param float speed_linear: linear speed -> speed in mm/s (-1 = no change)
        :param float speed_joints: joint speed (optional) -> acceleration in mm/s2 (-1 = no change)
        :param float accel_linear: linear acceleration (optional) -> acceleration in mm/s2 (-1 = no change)
        :param float accel_joints: joint acceleration (optional) -> acceleration in deg/s2 (-1 = no change)
        
        .. seealso:: :func:`~robolink.Item.setAcceleration`, :func:`~robolink.Item.setSpeedJoints`, :func:`~robolink.Item.setAccelerationJoints`
        """
        self.link._check_connection()
        command = 'S_Speed4'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array([float(speed_linear), float(speed_joints), float(accel_linear), float(accel_joints)])
        self.link._check_status()
    
    def setAcceleration(self, accel_linear):
        """Sets the linear acceleration of a robot in mm/s2
        
        :param float accel_linear: acceleration in mm/s2
        
        .. seealso:: :func:`~robolink.Item.setSpeed`, :func:`~robolink.Item.setSpeedJoints`, :func:`~robolink.Item.setAccelerationJoints`
        """
        self.setSpeed(-1,accel_linear,-1,-1)
    
    def setSpeedJoints(self, speed_joints):
        """Sets the joint speed of a robot in deg/s for rotary joints and mm/s for linear joints
        
        :param float speed_joints: speed in deg/s for rotary joints and mm/s for linear joints
        
        .. seealso:: :func:`~robolink.Item.setSpeed`, :func:`~robolink.Item.setAcceleration`, :func:`~robolink.Item.setAccelerationJoints`
        """
        self.setSpeed(-1,-1,speed_joints,-1)
    
    def setAccelerationJoints(self, accel_joints):
        """Sets the joint acceleration of a robot
        
        :param float accel_joints: acceleration in deg/s2 for rotary joints and mm/s2 for linear joints
        
        .. seealso:: :func:`~robolink.Item.setSpeed`, :func:`~robolink.Item.setAcceleration`, :func:`~robolink.Item.setSpeedJoints`
        """
        self.setSpeed(-1,-1,-1,accel_joints)   
    
    def setRounding(self, rounding_mm):
        """Sets the rounding accuracy to smooth the edges of corners. In general, it is recommended to allow a small approximation near the corners to maintain a constant speed. 
        Setting a rounding values greater than 0 helps avoiding jerky movements caused by constant acceleration and decelerations.
        
        :param float rounding_mm: rounding accuracy in mm. Set to -1 (default) for best accuracy and to have point to point movements (might have a jerky behavior)
        
        This rounding parameter is also known as ZoneData (ABB), CNT (Fanuc), C_DIS/ADVANCE (KUKA), cornering (Mecademic) or blending (Universal Robots)
        
        .. seealso:: :func:`~robolink.Item.setSpeed`
        """
        self.link._check_connection()
        command = 'S_ZoneData'
        self.link._send_line(command)
        self.link._send_int(rounding_mm*1000);
        self.link._send_item(self)
        self.link._check_status()
    
    def setZoneData(self, zonedata):
        """Obsolete. Use :func:`~robolink.Item.setRounding` instead."""
        self.setRounding(zonedata)
    
    def ShowSequence(self, matrix):
        """Displays a sequence of joints in RoboDK and displays a slider.
        
        :param matrix: list of joints as a matrix or as a list of joint arrays. An sequence of instructions is also supported (same sequence that was supported with RoKiSim).
        :type matrix: list of list of float or a matrix of joints as a :class:`.Mat`"""
        self.link._check_connection()
        command = 'Show_Seq'
        self.link._send_line(command)
        self.link._send_matrix(matrix);
        self.link._send_item(self)
        self.link._check_status()
    
    def Busy(self):
        """Checks if a robot or program is currently running (busy or moving).
        Returns a busy status (1=moving, 0=stopped)
        
        .. seealso:: :func:`~robolink.Item.WaitMove`, :func:`~robolink.Item.RunProgram`, :func:`~robolink.Item.RunCodeCustom`
        
        Example:
        
        .. code-block:: python
            
            from robolink import *      # import the robolink library            
            RDK = Robolink()            # Connect to the RoboDK API
            prog = RDK.Item('MainProgram', ITEM_TYPE_PROGRAM)
            prog.RunProgram()
            while prog.Busy():
                pause(0.1)
            
            print("Program done") 

        """
        self.link._check_connection()
        command = 'IsBusy'
        self.link._send_line(command)
        self.link._send_item(self)
        busy = self.link._rec_int()
        self.link._check_status()
        return busy
            
    def Stop(self):
        """Stop a program or a robot
        
        .. seealso:: :func:`~robolink.Item.RunProgram`, :func:`~robolink.Item.MoveJ`
        """
        self.link._check_connection()
        command = 'Stop'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
    
    def WaitMove(self, timeout=300):
        """Waits (blocks) until the robot finishes its movement.
        
        :param float timeout: Maximum time to wait for robot to finish its movement (in seconds)
        
        .. seealso:: :func:`~robolink.Item.Busy`, :func:`~robolink.Item.MoveJ`
        """
        self.link._check_connection()
        command = 'WaitMove'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
        self.link.COM.settimeout(timeout)
        self.link._check_status()#will wait here
        self.link.COM.settimeout(self.link.TIMEOUT)
        #busy = self.link.Is_Busy(self.item)
        #while busy:
        #    busy = self.link.Is_Busy(self.item)        
        
    def WaitFinished(self):
        """Wait until a program finishes or a robot completes its movement
        
        .. seealso:: :func:`~robolink.Item.Busy`
        """
        while self.Busy():
            pause(0.05)
    
    def ProgramStart(self, programname, folder='', postprocessor=''):
        """Defines the name of the program when a program must be generated. 
        It is possible to specify the name of the post processor as well as the folder to save the program. 
        This method must be called before any program output is generated (before any robot movement or other program instructions).
        
        :param str progname: name of the program
        :param str folder: folder to save the program, leave empty to use the default program folder
        :param str postprocessor: name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post")
        
        .. seealso:: :func:`~robolink.Robolink.setRunMode`
        """
        return self.link.ProgramStart(programname, folder, postprocessor, self)    
    
    def setAccuracyActive(self, accurate = 1):
        """Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.
        
        :param int accurate: set to 1 to use the accurate model or 0 to use the nominal model
        
        """
        self.link._check_connection()
        command = 'S_AbsAccOn'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(accurate)
        self.link._check_status()
    
    def FilterProgram(self, filestr):
        """Filter a program file to improve accuracy for a specific robot. The robot must have been previously calibrated.
        It returns 0 if the filter succeeded, or a negative value if there are filtering problems. It also returns a summary of the filtering.
        
        :param str filestr: File path of the program. Formats supported include: JBI (Motoman), SRC (KUKA), MOD (ABB), PRG (ABB), LS (FANUC).
        """
        self.link._check_connection()
        command = 'FilterProg2'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(filestr)
        filter_status = self.link._rec_int()
        filter_msg = self.link._rec_line()        
        self.link._check_status()
        return filter_status, filter_msg
    
    #"""Program item calls"""    
    def MakeProgram(self, filestr='', run_mode = RUNMODE_MAKE_ROBOTPROG):
        """Generate the program file. Returns True if the program was successfully generated.
        
        :param str filestr: File path of the program. It can be left empty to use the default action (promt to user or rewrite file)
        :param run_mode: RUNMODE_MAKE_ROBOTPROG to generate the program file. Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.
        :return: [success (True or False), log (str), transfer_succeeded (True/False)]
        
        Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)
        
        .. seealso:: :func:`~robolink.Robolink.setRunMode`      
        """
        self.link._check_connection()
        command = 'MakeProg2'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(filestr)
        self.link._send_int(run_mode)        
        prog_status = self.link._rec_int()
        prog_log_str = self.link._rec_line()
        transfer_status = self.link._rec_int()
        self.link._check_status()
        success = False
        if prog_status > 0:
            success = True
        transfer_ok = False
        if transfer_status > 0:
            transfer_ok = True
            
        return success, prog_log_str, transfer_ok
    
    def setRunType(self, program_run_type):
        """Set the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).
        
        :param int program_run_type: Use "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot
        
        .. seealso:: :func:`~robolink.Robolink.setRunMode`
        """
        self.link._check_connection()
        command = 'S_ProgRunType'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(program_run_type)
        self.link._check_status()
    
    def RunProgram(self, prog_parameters=None):
        """Obsolete. Use :func:`~robolink.Item.RunCode` instead. RunProgram is available for backwards compatibility."""
        return self.RunCode(prog_parameters)
        
    def RunCode(self, prog_parameters=None):
        """Run a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        This is a non-blocking call. Use program.Busy() to check if the program execution finished, or program.WaitFinished() to wait until the program finishes.
       
        :param prog_parameters: Program parameters can be provided for Python programs as a string
        :type prog_parameters: list of str
        
        .. seealso:: :func:`~robolink.Item.RunCodeCustom`, :func:`~robolink.Item.Busy`, :func:`~robolink.Robolink.AddProgram`
        
        If setRunMode(RUNMODE_SIMULATE) is used: the program will be simulated (default run mode)
        
        If setRunMode(RUNMODE_RUN_ROBOT) is used: the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)
        
        If setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
                
        """
        self.link._check_connection()
        if type(prog_parameters) == list:
            command = 'RunProgParam'
            self.link._send_line(command)
            self.link._send_item(self)
            parameters = ''
            if type(prog_parameters) is list:
                parameters = '<br>'.join(str(param_i) for param_i in prog_parameters)
            else:
                parameters = str(prog_parameters)
            self.link._send_line(parameters)
        else:
            command = 'RunProg'
            self.link._send_line(command)
            self.link._send_item(self)
        prog_status = self.link._rec_int()
        self.link._check_status()
        return prog_status
        
    def RunCodeCustom(self, code, run_type=INSTRUCTION_CALL_PROGRAM):
        """Adds a program call, code, message or comment to the program. Returns 0 if succeeded.
        
        :param str code: The code to insert, program to run, or comment to add.
        :param int run_type: Use INSTRUCTION_* variable to specify if the code is a program call or just a raw code insert. For example, to add a line of customized code use:
        
        .. code-block:: python
            :caption: Available Instruction Types
            
            INSTRUCTION_CALL_PROGRAM = 0        # Program call
            INSTRUCTION_INSERT_CODE = 1         # Insert raw code in the generated program
            INSTRUCTION_START_THREAD = 2        # Start a new process
            INSTRUCTION_COMMENT = 3             # Add a comment in the code
        
        .. seealso:: :func:`~robolink.Item.RunCode`, :func:`~robolink.Robolink.AddProgram`
        
        Example:
        
        .. code-block:: python
            
            program.RunCodeCustom('Setting the spindle speed', INSTRUCTION_COMMENT)
            program.RunCodeCustom('SetRPM(25000)', INSTRUCTION_INSERT_CODE)
            program.RunCodeCustom('Program1', INSTRUCTION_CALL_PROGRAM)      
        
        """
        self.link._check_connection()
        command = 'RunCode2'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(code.replace('\r\n','<<br>>').replace('\n','<<br>>'))
        self.link._send_int(run_type)        
        prog_status = self.link._rec_int()
        self.link._check_status()
        return prog_status
        
    def Pause(self, time_ms = -1):
        """Pause instruction for a robot or insert a pause instruction to a program (when generating code offline -offline programming- or when connected to the robot -online programming-).
        
        :param float time_ms: time in miliseconds. Do not provide a value (leave the default -1) to pause until the user desires to resume the execution of a program.
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'RunPause'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(time_ms*1000.0)
        self.link._check_status()
        
    def setDO(self, io_var, io_value):
        """Set a digital output to a given value. This can also be used to set any variables to a desired value.
        
        :param io_var: digital output (string or number)
        :type io_var: str or int
        :param io_value: value
        :type io_value: str, int or float
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'setDO'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(str(io_var))
        self.link._send_line(str(io_value))
        self.link._check_status()
    
    def waitDI(self, io_var, io_value, timeout_ms=-1):
        """Wait for an digital input io_var to attain a given value io_value. Optionally, a timeout can be provided.
        
        :param io_var: digital input (string or number)
        :type io_var: str or int
        :param io_value: value
        :type io_value: str, int or float
        :param timeout_ms: timeout in milliseconds
        :type timeout_ms: int or float
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'waitDI'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(str(io_var))
        self.link._send_line(str(io_value))
        self.link._send_int(timeout_ms*1000)
        self.link._check_status()
        
    def customInstruction(self, name, path_run, path_icon="", blocking=1, cmd_run_on_robot=""):
        """Add a custom instruction. This instruction will execute a Python file or an executable file.
        
        :param name: digital input (string or number)
        :type name: str or int
        :param path_run: path to run (relative to RoboDK/bin folder or absolute path)
        :type path_run: str
        :param path_icon: icon path (relative to RoboDK/bin folder or absolute path)
        :type path_icon: str        
        :param blocking: 1 if blocking, 0 if it is a non blocking executable trigger
        :type blocking: int
        :param cmd_run_on_robot: Command to run through the driver when connected to the robot
        :type cmd_run_on_robot: str
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'InsCustom2'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_line(name)
        self.link._send_line(path_run)
        self.link._send_line(path_icon)
        self.link._send_line(cmd_run_on_robot)        
        self.link._send_int(blocking)
        self.link._check_status()
    
    def addMoveJ(self, itemtarget):
        """Adds a new robot joint move instruction to a program.
        
        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Add_INSMOVE'
        self.link._send_line(command)
        self.link._send_item(itemtarget)
        self.link._send_item(self)
        self.link._send_int(1)
        self.link._check_status()
    
    def addMoveL(self, itemtarget):
        """Adds a new robot linear move instruction to a program.
        
        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Add_INSMOVE'
        self.link._send_line(command)
        self.link._send_item(itemtarget)
        self.link._send_item(self)
        self.link._send_int(2)
        self.link._check_status()
        
    def ShowInstructions(self, show=True):
        """Show or hide instruction items of a program in the RoboDK tree
        
        :param show: Set to True to show the instruction nodes, otherwise, set to False
        :type show: bool
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Prog_ShowIns'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(1 if show else 0)        
        self.link._check_status()
        
    def ShowTargets(self, show=True):
        """Show or hide targets of a program in the RoboDK tree
        
        :param show: Set to False to remove the target item (the target is not deleted as it remains inside the program), otherwise, set to True to show the targets
        :type show: bool
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Prog_ShowTargets'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(1 if show else 0)        
        self.link._check_status()
        
    def InstructionCount(self):
        """Return the number of instructions of a program.
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Prog_Nins'
        self.link._send_line(command)
        self.link._send_item(self)
        nins = self.link._rec_int()
        self.link._check_status()
        return nins
    
    def Instruction(self, ins_id=-1):
        """Return the current program instruction or the instruction given the instruction id (if provided).
        It returns the following information about an instruction:
        name: name of the instruction (displayed in the RoboDK tree)
        instype: instruction type (INS_TYPE_*). For example, INS_TYPE_MOVE for a movement instruction.
        movetype: type of movement for INS_TYPE_MOVE instructions: MOVE_TYPE_JOINT for joint moves, or MOVE_TYPE_LINEAR for linear moves
        isjointtarget: 1 if the target is specified in the joint space, otherwise, the target is specified in the cartesian space (by the pose)
        target: pose of the target as :class:`.Item`
        joints: robot joints for that target        
        
        :param ins_id: instruction id to return
        :type ins_id: int
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`, :func:`~robolink.Robolink.setInstruction`
        """
        self.link._check_connection()
        command = 'Prog_GIns'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(ins_id)
        name = self.link._rec_line()
        instype = self.link._rec_int()
        movetype = None
        isjointtarget = None
        target = None
        joints = None
        if instype == INS_TYPE_MOVE:
            movetype = self.link._rec_int()
            isjointtarget = self.link._rec_int()
            target = self.link._rec_pose()
            joints = self.link._rec_array()
        self.link._check_status()
        return name, instype, movetype, isjointtarget, target, joints
        
    def setInstruction(self, ins_id, name, instype, movetype, isjointtarget, target, joints):
        """Update a program instruction.
        
        :param ins_id: index of the instruction (0 for the first instruction, 1 for the second, and so on)
        :type ins_id: int
        :param name: Name of the instruction (displayed in the RoboDK tree)
        :type name: str
        :param instype: Type of instruction. INS_TYPE_*
        :type instype: int
        :param movetype: Type of movement if the instruction is a movement (MOVE_TYPE_JOINT or MOVE_TYPE_LINEAR)
        :type movetype: int
        :param isjointtarget: 1 if the target is defined in the joint space, otherwise it means it is defined in the cartesian space (by the pose)
        :type isjointtarget: int
        :param target: target pose
        :type target: :class:`.Mat`
        :param joints: robot joints for the target
        :type joints: list of float
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`, :func:`~robolink.Robolink.Instruction`
        """
        self.link._check_connection()
        command = 'Prog_SIns'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_int(ins_id)
        self.link._send_line(name)
        self.link._send_int(instype)
        if instype == INS_TYPE_MOVE:
            self.link._send_int(movetype)
            self.link._send_int(isjointtarget)
            self.link._send_pose(target)
            self.link._send_array(joints)
        self.link._check_status()
           
    def Update(self, check_collisions=COLLISION_OFF, timeout_sec = 3600, mm_step=-1, deg_step=-1):
        """Updates a program and returns the estimated time and the number of valid instructions.
        An update can also be applied to a robot machining project. The update is performed on the generated program.
        
        :param int check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)
        :param int timeout_sec: Maximum time to wait for the update to complete (in seconds)
        :param float mm_step: Step in mm to split the program (-1 means default, as specified in Tools-Options-Motion)
        :param float deg_step: Step in deg to split the program (-1 means default, as specified in Tools-Options-Motion)        
        
        :return: [valid_instructions, program_time, program_distance, valid_ratio, readable_msg]
        
        valid_instructions: The number of valid instructions
        
        program_time: Estimated cycle time (in seconds)
        
        program_distance: Estimated distance that the robot TCP will travel (in mm)
        
        valid_ratio: This is a ratio from [0.00 to 1.00] showing if the path can be fully completed without any problems (1.0 means the path 100% feasible) or 
        valid_ratio is <1.0 if there were problems along the path.
        
        readable_msg: a readable message as a string
        
        .. seealso:: :func:`~robolink.Robolink.AddProgram`
        """
        self.link._check_connection()
        command = 'Update2'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array([check_collisions, mm_step, deg_step])
        self.link.COM.settimeout(timeout_sec) # wait up to 1 hour user to hit OK
        values = self.link._rec_array().tolist()
        self.link.COM.settimeout(self.link.TIMEOUT)
        readable_msg = self.link._rec_line()
        self.link._check_status()
        valid_instructions = values[0]
        program_time = values[1]
        program_distance = values[2]
        valid_program = values[3]
        return valid_instructions, program_time, program_distance, valid_program, readable_msg
        
    def InstructionList(self):
        """Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes. This is the equivalent sequence that used to be supported by RoKiSim.
        Tip: Use RDK.ShowSequence(matrix) to dipslay a joint list or a RoKiSim sequence of instructions.
        
        Out 1: Returns the matrix
        
        Out 2: Returns 0 if the program has no issues
        
        .. seealso:: :func:`~robolink.Robolink.ShowSequence`, :func:`~robolink.Robolink.InstructionListJoints`
        """
        self.link._check_connection()
        command = 'G_ProgInsList'
        self.link._send_line(command)
        self.link._send_item(self)
        insmat = self.link._rec_matrix()
        errors = self.link._rec_int()
        self.link._check_status()
        return insmat, errors
          
    def InstructionListJoints(self, mm_step=10, deg_step=5, save_to_file = None, collision_check = COLLISION_OFF, reserved_flags = 0):
        """Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.
        
        :param float mm_step: step in mm to split the linear movements
        :param float deg_step: step in deg to split the joint movements
        :param str save_to_file: (optional) save the result to a file as Comma Separated Values (CSV). If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.
        :param int collision_check: (optional) check for collisions
        :param int reserved_flags: (optional) parameters reserved for future compatibility
        :return: [message (str), list of joints, 0 if success]
        
        Returns a human readable error message (if any)
        
        It also returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] or the file name if a file path is provided to save the result
                
        .. seealso:: :func:`~robolink.Robolink.ShowSequence`, :func:`~robolink.Robolink.InstructionListJoints`
        """
        self.link._check_connection()
        command = 'G_ProgJointList'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._send_array([mm_step, deg_step, float(collision_check), float(reserved_flags)])
        joint_list = save_to_file   
        if save_to_file is None:
            self.link._send_line('')
            joint_list = self.link._rec_matrix()
        else:
            self.link._send_line(save_to_file)
        error_code = self.link._rec_int()
        error_msg = self.link._rec_line()
        self.link._check_status()
        return error_msg, joint_list, error_code

