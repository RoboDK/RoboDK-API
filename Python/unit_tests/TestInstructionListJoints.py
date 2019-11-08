##
## Test RoboDK InstructionListJoints().
## 

import unittest
import time
from path_simulation import *


## Setup RoboDK and load rdk test file
##RDK, robot, tools = setupRoboDK(r"Robot_2TCP.rdk")
##RDK, robot, tools = setupRoboDK(r"CombiGripper-Robot.rdk")
## Print some info about the loaded rdk file
##PrintInfo()

##
## Test Program to simulate stop points 
def GetTestProgramOneStopPoint():
    jointpos1 = [85.313866, -54.353057, 109.847412, 90.670697, -90.461034, 55.497054]
    framepos1 =[     267.800000,    -875.699998,     529.200000,        -0.000000,         0.000000,     -84.500000 ]
    framepos2 =[     267.800000,    -875.699998,     509.200000,        -0.000000,         0.000000,     -84.500000 ]
    framepos3 =[     267.800000,    -880.699998,     509.200000,        -0.000000,         0.000000,     -84.500000 ]
    framepos4 =[     267.800000,    -880.699998,     489.200000,        -0.000000,         0.000000,     -84.500000 ]
    framepos5 =[     267.800000,    -697.899998,     489.200000,        -0.000000,         0.000000,     -84.500000 ]
    jointpos2 = [65.489465, -60.520188, 93.790655, 50.917749, 22.204378, 23.388239]
    framepos6 = [     267.800005,    -886.682405,     541.603646,        45.000000,        0.000000,    180.000000 ]
    framepos7 = [     267.800000,    -900.824545,     555.745785,        45.000000,        0.000000,    180.000000 ]

    stepList = [
            ## Step: name, moveType, tcp, pose, blending, speed, accel):
            Step("1", MoveType.Joint, 0, jointpos1, 10, 0, 0),
            Step("2", MoveType.Frame, 0, framepos1, 10, 0, 0),
            Step("3", MoveType.Frame, 0, framepos2, 10, 0, 0),
            Step("4", MoveType.Frame, 0, framepos3, 10,    0, 0),
            Step("5", MoveType.Frame, 0, framepos4, 10, 0, 0),
            Step("6", MoveType.Frame, 0, framepos5, 10, 0, 0),
            Step("7", MoveType.Joint, 0, jointpos2, 10, 0, 0),
            Step("8", MoveType.Frame, 0, framepos6, 10, 0, 0),
            Step("9", MoveType.Frame, 0, framepos7, 10,    0, 0),
     ]

    stepList[2].blending = 0
    return Program("Move to stop point", stepList, 0.002)# 0.055

def GetTestProgramTwoStopPoints():
    program = GetTestProgramOneStopPoint()
    stepList = program.stepList
    stepList[2].blending = 0
    stepList[3].blending = 0
    program.stepTime = 0.033
    return program

def GetTestProgramThreeStopPoints():
    program = GetTestProgramOneStopPoint()
    stepList = program.stepList
    stepList[2].blending = 0
    stepList[3].blending = 0
    stepList[4].blending = 0
    program.stepTime = 0.077
    return program
    
##
## Test Program 2
## Robot rotates around a point.
## framepos2 - framepos3: rotate robot axis. Cartesian coordinates stay constant
##
def GetTestProgramRotate():
    jointpos1 = [89.032848, -66.822879, 113.889182, 89.929968, -106.519502, -17.840590]
    framepos1 = [     230.864307,    -923.444947,     581.390218,        45.000000,         0.000000,     -72.810208 ]
    framepos2 = [     230.864307,    -923.444947,     601.390218,        45.000000,        -0.000000,     -72.810208 ]
    framepos3 = [     230.864307,    -923.444947,     601.390218,        64.173180,         5.801359,     -73.790852 ]
    framepos4 = [     230.864307,    -665.477946,     601.390218,        64.173180,         5.801359,     -73.790852 ]
    stepList = [
                ## Step: name, moveType, tcp, pose, blending, speed, accel):
                Step("1", MoveType.Joint, 0, jointpos1, 0, 0, 0),
                Step("2", MoveType.Frame, 0, framepos1, 0, 0, 0),
                Step("3", MoveType.Frame, 0, framepos2, 0, 0, 0),
                Step("4", MoveType.Frame, 0, framepos3, 0,    0, 0),
                Step("5", MoveType.Frame, 0, framepos4, 0, 0, 0),
            ]
    return Program("Rotate Robot Axis", stepList, 0.002) # 0.02



##
## Test near Singularity
##
def GetTestProgramNearSingularity():
    jointpos1 = [     84.042754, -57.261200, 115.707342, 78.814999, -83.206905, 59.112086 ]
    framepos1 = [     267.800000,    -697.899998,     489.200000,        -0.000000,        -0.000000,     -97.106527 ]
    framepos2 = [     267.800000,    -886.682410,     541.603649,        45.000000,         0.000000,     180.000000 ]
    framepos3 = [     267.800000,    -900.824545,     555.745785,        45.000000,         0.000000,     180.000000 ]
    stepList = [
                ## Step: name, moveType, tcp, pose, blending, speed, accel):
                Step("1", MoveType.Joint, 0, jointpos1, 10, 0, 0),
                Step("2", MoveType.Frame, 0, framepos1, 10, 0, 0),
                Step("3", MoveType.Frame, 0, framepos2, 10, 0, 0),
                Step("4", MoveType.Frame, 0, framepos3, 0,    0, 0),
            ]
    return Program("Near Singularity", stepList, 0.04)



class TestInstructionListJoints(unittest.TestCase):
    def setUp(self):
        self.program = None
        DeleteProgramAndTargets()
        RDK, robot, tools = setupRoboDK(r"Robot_2TCP.rdk")

    def tearDown(self):
        if self.program != None:
            ##print("tearDown")
            ##AddJointListResultToRoboDK(self.program)
            pass

    def GetFramePose(self, step, frame):
        robot.setPoseTool(step.tcpItem)
        robot.setJoints(frame.pose)
        joints = robot.Pose()
        framePose = Pose_2_Staubli(joints)
        return framePose

    def TestResultMessage(self, program):
        """Test if return message of InstructionListJoints() is 'success' """
        result = program.result
        self.assertEqual(result.message.lower(), "success", f"Step {program.name} InstructionJointList result: {result.message}")


    def TestForMissingMoveIds(self, program):
        """For each Step we should have at least one playback frame"""
        stepList = program.stepList
        moveId = 0
        for s in stepList:
                moveId = moveId + 1
                msg = f"Step {s.name} has no playbackFrames. Move Id {moveId} is missing"
                self.assertNotEqual(len(s.frameList) , 0, msg)

    def TestForValidMoveIds(self, program):
        """Each Frame must have a valid move id > 0"""
        frameList = program.result.playbackFrameList
        maxMoveId = len(program.stepList)
        for idx, f in enumerate(frameList):
            msg = f"Frame {idx} has invalid moveId {f.moveId}. MoveId must be between 1 and {maxMoveId}"
            self.assertGreaterEqual(f.moveId, 1, msg)
            self.assertLessEqual(f.moveId, maxMoveId, msg)
                        
    def TestForPlaybackFrameErrors(self, program):
        """Check all playback frames for each step for errors"""
        stepList = program.stepList
        moveId = 0
        for s in stepList:
                for idx, f in enumerate(s.frameList):
                        resultMessage = program.result.message.lower()
                        if resultMessage == "success":
                                msg = f"Step {s.name} frame number {idx} has a simulation error: {f.errorString} but program result is: {program.result.message}"
                        else:
                                msg = f"Step {s.name} frame number {idx} has a simulation error: {f.errorString}"
                        self.assertEqual(f.error , 0, msg)

    def TestStepTime1(self, program):
        stepList = program.stepList
        for s in stepList:
            if s.blending == 0:
                lastFrame = s.frameList[-1]
                msg = f"Step {s.name} has blending set to 0. Expected Stop Point with timeStep = 0"
                self.assertEqual(lastFrame.timeStep , 0, msg)
    
    def TestIfTargetReached(self, program):
        stepList = program.stepList
        for s in stepList:
            if s.blending == 0:
                lastFrame = s.frameList[-1]
                expectedFramePose = self.GetFramePose(s, lastFrame)
                delta = 1e-06
                msg = f"step {s.name} is a stop point. Exact target position should be reached"
                if( s.moveType == MoveType.Frame ):
                    for idx, value in enumerate(expectedFramePose):
                        self.assertAlmostEqual(s.pose[idx], value, msg=msg, delta=delta)

    
    def TestIfCartesianCoordinatesAreConst(self, program, stepIdx):
        stepList = program.stepList
        startStep = stepList[stepIdx]
        playbackFrame = startStep.frameList[-1]
        refFramePose = self.GetFramePose(startStep, playbackFrame)
        print("refFramePose:", refFramePose[:3])
        
        endStep = stepList[stepIdx+1]
        for index, playbackFrame in enumerate(endStep.frameList):
            framePose = self.GetFramePose(endStep, playbackFrame)
            ##print(framePose[:3])
            delta = 1e-06
            for i in range(3):
                msg = f"step {endStep.name} playback frame {index},{i} has not the same position. refFrame{refFramePose[:3]}, step frame {framePose[:3]}"
                self.assertAlmostEqual(framePose[i], refFramePose[i], msg=msg, delta=delta)
                

    def TestProgramWithStopPoints(self, prgoram):
        program = self.program
        CreateProgram( program )
        SimulateProgram( program )
        ##PrintInstructionListJointsResult(program)
        self.TestForValidMoveIds(program)
        self.TestForPlaybackFrameErrors(program)
        self.TestResultMessage(program)
        self.TestForMissingMoveIds(program)
        self.TestIfTargetReached(program)
        ##self.TestStepTime1(program)

    def xxtest_prgoramWithOneStopPoint(self):
        """Test Robot Program with one stop points"""
        self.program = GetTestProgramOneStopPoint()
        self.TestProgramWithStopPoints(self.program)

    def xxtest_prgoramWithTwoStopPoints(self):
        """Test Robot Program with 2 adjacent stop points"""
        self.program = GetTestProgramTwoStopPoints()
        self.TestProgramWithStopPoints(self.program)
        
    def xxtest_prgoramWithThreeStopPoints(self):
        """Test Robot Program with 3 adjacent stop points"""
        self.program = GetTestProgramThreeStopPoints()
        self.TestProgramWithStopPoints(self.program)
        
    def xxtest_programRotate(self):
        """Test Rotation around a const cartesian coordinate"""
        self.program = GetTestProgramRotate()
        program = self.program
        CreateProgram( program )
        SimulateProgram( program )
        ##PrintInstructionListJointsResult(program)
        self.TestForValidMoveIds(program)
        self.TestForPlaybackFrameErrors(program)
        self.TestResultMessage(program)
        self.TestForMissingMoveIds(program)
        self.TestIfTargetReached(program)
        self.TestIfCartesianCoordinatesAreConst(program, 2)

    def xxtest_nearSingularity1(self):
        """Test Case Singularity with STEP_MM=1, STEP_DEG=1"""
        self.program = GetTestProgramNearSingularity()
        program = self.program
        CreateProgram( program )
        SimulateProgram( program )
        ##PrintInstructionListJointsResult(program)
        self.TestForValidMoveIds(program)
        self.TestForPlaybackFrameErrors(program)
        self.TestResultMessage(program)
        self.TestForMissingMoveIds(program)
        ##AddJointListResultToRoboDK(self.program)

    def xxtest_nearSingularity2(self):
        """Test Case Singularity with STEP_MM=10, STEP_DEG=10"""
        self.program = GetTestProgramNearSingularity()
        program = self.program
        program.STEP_MM = 10
        program.STEP_DEG = 10
        CreateProgram( program )
        SimulateProgram( program )
        ##PrintInstructionListJointsResult(program)
        self.TestForValidMoveIds(program)
        self.TestForPlaybackFrameErrors(program)
        self.TestResultMessage(program)
        self.TestForMissingMoveIds(program)
        ##AddJointListResultToRoboDK(self.program)
        
    def test_foo(self):        
        print("")
        
if __name__ == '__main__':
    unittest.main()
