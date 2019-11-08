import sys

sys.path.insert(0, "..")
from robolink import *     
from enum import Enum

#---------------- Default Speed and Acceleration ----------------------    
jointSpeed = 225  #[deg/s]
jointAccel = 400  #[deg/s^2]
frameSpeed = 2000 #[mm/s]
frameAccel = 2000 #[mm/s^2]

tools = None
RDK = None
robot = None


def setupRoboDK(robotFile):
#---------------- Load RoboDK ----------------------
    global tools
    global RDK
    global robot
    # Link to the RoboDK API
    ##def __init__(self, robodk_ip='localhost', port=None, args=[], robodk_path=None):
    RDK = Robolink()

    #---------------- Configure RoboDK ----------------------    
    print("RoboDK Version: ", RDK.Version())
    RDK.Command("AutoRenderDelay", 50);
    RDK.Command("AutoRenderDelayMax", 300);
    RDK.Render(False);

    RDK.Command("CollisionMap", "None");
    RDK.setCollisionActive(COLLISION_OFF)

    RDK.Command("ToleranceSingularityWrist ", 2.0); # 2.0    Threshold angle to avoid singularity for joint 5 (deg)
    RDK.Command("ToleranceSingularityElbow ", 3.0); # 3.0    Threshold angle to avoid singularity for joint 3 (deg)
    RDK.Command("ToleranceSmoothKinematic", 25 );    # 25 deg


    #---------------- Load Sample Robot with CombiGripper ----------------------    
    robotFile = os.path.realpath(robotFile)

    # Get the robot linked to the program
    robot = RDK.Item("", ITEM_TYPE_ROBOT)
    if not robot.Valid():
        RDK.AddFile(robotFile)
        robot = RDK.Item("", ITEM_TYPE_ROBOT)
    tools = RDK.ItemList(ITEM_TYPE_TOOL)
    return RDK, robot, tools

def PrintInfo():
    print("Robot and TCP Setup:")    
    print(robot.Name())
    for tool in tools:
        print(tool.Name(), tool)
    print()


#---------------- InstructionListJointsResult ----------------------    
class InstructionListJointsResult():
    "Program Step"
    def __init__(self, error, message, jointList):
        self.error = error
        self.message = message
        self.playbackFrameList = []
        self.jointList = jointList

    def AddPlaybackFrame(self, playbackFrame):
        self.playbackFrameList.append(playbackFrame)

    def Print(self):
        print("error:", self.error, " -> ", self.message)
        prevMoveId = 0
        for f in self.playbackFrameList:
            if prevMoveId != f.moveId:
                prevMoveId = f.moveId
                print()
            f.Print()

    def GetFramesForMoveId(self, moveId):
        result = []
        for f in self.playbackFrameList:
            if f.moveId == moveId:
                result.append(f)
        return result
    
class PlaybackFrame():
    def __init__(self, pose, moveId, speed, accel, error, timeStep):
        self.pose = pose
        self.moveId = moveId
        self.speed = speed
        self.accel = accel
        self.error = error
        self.errorString = str(ConvertErrorCodeToJointErrorType(self.error))
        self.errorFlags = ConvertErrorCodeToJointErrorType(self.error)
        self.timeStep = timeStep
    
    def Print(self):
        #print(self.moveId, self.error, self.timeStep, self.speed, self.accel)
        print(f"id:{self.moveId:2.0f} err:{self.error:.0f} t:{self.timeStep:1.3f} v:{self.speed:-3.3f} a:{self.accel:-3.3f} ")
        
#---------------- Program Step ----------------------    
MoveType = Enum('MoveType', 'Joint Frame')
class Step():
    "Program Step"
    def __init__(self, name, moveType, tcp, pose, blending, speed, accel):
         self.name = name
         self.moveType = moveType
         self.tcp = tcp
         self.pose = pose
         self.speed = speed
         self.accel = accel
         self.blending = blending
         self.tcpItem = tools[tcp]
         self.tcpName = tools[tcp].Name()
         self.frameList = []
          
    def AddFrameList(self, frames):
        self.frameList = frames

    def Print(self):
        print(f"Step {self.name}: {self.moveType}")
        for f in self.frameList:
            f.Print()
        print()

#---------------- Program ----------------------
class Program():
    def __init__(self, name, steps, stepTime, stepMM=1, stepDeg=1):
        self.name = name
        self.stepList = steps
        self.stepTime = stepTime
        self.result = []
        self.program = []
        self.STEP_MM = stepMM
        self.STEP_DEG = stepDeg


    def SetResult(self, result):
        self.result = result

    def SetProgram(self, program):
        self.program = program
        

#---------------- Convert Frame (x,y,z,rx,ry,rz) to a RoboDK Matrix ----------------------    
def xyzrp2ToPose(pose):
    return Pose(pose[0], pose[1], pose[2], pose[3], pose[4], pose[5])


#---------------- Delete All Targets and RoboDK Program ----------------------
def DeleteProgramAndTargets():
    if RDK is None:
        return
    items = RDK.ItemList(ITEM_TYPE_TARGET)
    for item in items:
        item.Delete()
    items = RDK.ItemList(ITEM_TYPE_PROGRAM)
    for item in items:
        item.Delete()
    
#---------------- Generate Program for one Step ----------------------    
def AddStepToProgram(prg, robot, step):
    #print("AddStepToProgram:", step.moveType, step.tcpName)

    # Set Robot TCP and Pose
    robot.setPoseTool(step.tcpItem)
    if step.moveType == MoveType.Joint:
        robot.setJoints(step.pose)
        
    target = RDK.AddTarget("Target_" + step.name + "_" + str(step.moveType), 0, robot)

    robot.setPoseTool(step.tcpItem)
    prg.setPoseTool(step.tcpItem)
    prg.setRounding(step.blending)
    
    target.setVisible(False)

    speed = jointSpeed
    if step.speed > 0:
        speed = step.speed
    accel = jointAccel
    if step.accel > 0:
        accel = step.accel

    if( step.moveType == MoveType.Joint ):
        target.setJoints(step.pose)
        target.setAsJointTarget()
        speed = jointSpeed
        if step.speed > 0:
            speed = step.speed
        accel = jointAccel
        if step.accel > 0:
            accel = step.accel
        prg.setSpeed(-1,speed, -1, accel)
        prg.MoveJ(target);
        
    if( step.moveType == MoveType.Frame ):
        #target.setPose(transl([step.pose[0],step.pose[1],step.pose[2]]) * roty(step.pose[3]) * rotx(step.pose[4]) * rotz(step.pose[5]))
        #target.setPose(xyzrpw_2_pose(step.pose))
        target.setPose(xyzrp2ToPose(step.pose))
        target.setAsCartesianTarget()
        speed = frameSpeed
        if step.speed > 0:
            speed = step.speed
        accel = frameAccel
        if step.accel > 0:
            accel = step.accel
        prg.setSpeed(speed, -1, accel, -1)
        prg.MoveL(target);
        

#---------------- Simulate Program ----------------------
        


        
def GetPlaybackFrames(program):
    STEP_MM = program.STEP_MM
    STEP_DEG = program.STEP_DEG
    STEP_TIME = program.stepTime
    #STEP_TIME = 0.002
    programItem = program.program
    flags = InstructionListJointsFlags.TimeBased
    error_msg, joint_list, error_code = programItem.InstructionListJoints(STEP_MM, STEP_DEG,None, COLLISION_OFF, flags, STEP_TIME)
    result = InstructionListJointsResult(error_code, error_msg, joint_list)
    joints = programItem.getLink().Joints()
    numberOfJoints, dummy = joints.size()
    cols, rows =  joint_list.size()
    errorIdx = numberOfJoints
    speedIdx = numberOfJoints + 1
    accelIdx = numberOfJoints + 2
    idIdx = numberOfJoints + 3
    timeIdx = numberOfJoints + 4
    for i in range(rows):
        #def __init__(self, moveId, speed, accel, error, timeStep):
        pose = []
        for j in range(numberOfJoints):
            pose.append( joint_list[j, i] )
        result.AddPlaybackFrame(PlaybackFrame(pose, joint_list[idIdx, i], joint_list[speedIdx, i], joint_list[accelIdx, i], joint_list[errorIdx, i], joint_list[timeIdx, i]))
    return result


def PrintInstructionListJointsResult(program):
    result = program.result
    print("PrintInstructionListJointsResult")
    error_msg = result.message
    joint_list = result.jointList
    error_code = result.error
    
    # Display error messages (if any)
    print("Error Msg : ", error_msg)
    print("Error Code: ", error_code)

    # Display the result
    print(joint_list.tr())


def AddJointListResultToRoboDK(program):
    result = program.result
    RDK.Command("Trace", "Reset")
    # Show the sequence in RoboDK
    joint_list = result.jointList
    # print('Showing joint sequencence in RoboDK')
    robot.ShowSequence(joint_list[:6,:])


#---------------- Generate and Tet Program  ----------------------

def CreateProgram( program ):
    DeleteProgramAndTargets()
    #print("Create Program", program.name)
    prg = RDK.AddProgram("Prg", robot)
    program.SetProgram(prg)
    for s in program.stepList:
        AddStepToProgram(prg, robot, s)
    print()    

def SimulateProgram( program ):
    #def GetPlaybackFrames(program, stepMM=1, stepDEG=1, stepTime=0.1):
    result = GetPlaybackFrames(program)
    program.SetResult(result)
    id = 1
    for s in program.stepList:
        frames = result.GetFramesForMoveId(id)
        id = id + 1
        s.AddFrameList(frames)



