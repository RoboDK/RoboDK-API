from enum import Enum
from robolink import *

JOINT_SPEED = 225  # [deg/s]
JOINT_ACCEL = 400  # [deg/s^2]
FRAME_SPEED = 2000  # [mm/s]
FRAME_ACCEL = 2000  # [mm/s^2]

tools = None
rdk = None
robot = None


def init_robodk():
    global rdk

    rdk = Robolink(close_std_out=True)

    rdk.Command("AutoRenderDelay", 50)
    rdk.Command("AutoRenderDelayMax", 300)
    rdk.Render(False)

    rdk.Command("CollisionMap", "None")
    rdk.setCollisionActive(COLLISION_OFF)

    rdk.Command("ToleranceSingularityWrist ", 2.0)  # 2.0    Threshold angle to avoid singularity for joint 5 (deg)
    rdk.Command("ToleranceSingularityElbow ", 3.0)  # 3.0    Threshold angle to avoid singularity for joint 3 (deg)
    rdk.Command("ToleranceSmoothKinematic", 25)  # 25 deg
    return rdk


def load_file(filename, load_new=False):
    global robot
    global tools
    robot = rdk.Item("", ITEM_TYPE_ROBOT)
    tools = rdk.ItemList(ITEM_TYPE_TOOL)
    if not robot.Valid() or load_new:
        print("Add New")
        rdk.AddFile(os.path.realpath(filename))
        robot = rdk.Item("", ITEM_TYPE_ROBOT)
        tools = rdk.ItemList(ITEM_TYPE_TOOL)
    return robot, tools


def clean_robodk():
    if rdk is not None:
        items = rdk.ItemList(ITEM_TYPE_TARGET)
        for item in items:
            item.Delete()
        items = rdk.ItemList(ITEM_TYPE_PROGRAM)
        for item in items:
            item.Delete()


def print_info():
    print("RoboDK Version: ", rdk.Version())
    print("Robot and TCP Setup:")
    print(robot.Name())
    for tool in tools:
        print(tool.Name(), tool)
    print()


class InstructionListJointsResult:
    def __init__(self, error, message, joints):
        self.error = error
        self.message = message
        self.playback_frames = []
        self.joints = joints

    def add_playback_frame(self, playback_frame):
        self.playback_frames.append(playback_frame)

    def get_playback_frames_for_move(self, move_id):
        result = []
        for f in self.playback_frames:
            if f.move_id == move_id:
                result.append(f)
        return result

    def add_to_robodk(self):
        rdk.Command("Trace", "Reset")
        robot.ShowSequence(self.joints[:6, :])

    def print(self):
        print("InstructionListJointsResult:")
        print(" > Error Msg:  ", self.message)
        print(" > Error Code: ", self.error)
        print(self.joints.tr())


class PlaybackFrame():
    def __init__(self, pose, move_id, speed, accel, error, time_step):
        self.pose = pose
        self.move_id = move_id
        self.speed = speed
        self.accel = accel
        self.error = error
        self.errorString = str(ConvertErrorCodeToJointErrorType(self.error))
        self.errorFlags = ConvertErrorCodeToJointErrorType(self.error)
        self.time_step = time_step

    def print(self):
        print(
            f" > PlaybackFrame id:{self.move_id:2.0f} err:{self.error:.0f} t:{self.time_step:1.3f} v:{self.speed:-3.3f} a:{self.accel:-3.3f} ")


MoveType = Enum('MoveType', 'Joint Frame')


class Step():
    def __init__(self, name, move_type, tcp, pose, blending, speed, accel):
        self.name = name
        self.move_type = move_type
        self.tcp = tcp
        self.pose = pose
        self.speed = speed
        self.accel = accel
        self.blending = blending
        self.tcpItem = tools[tcp]
        self.tcpName = tools[tcp].Name()
        self.playback_frames = []

    def print(self):
        print(f"Step {self.name}: {self.move_type}")
        for f in self.playback_frames:
            f.print()
        print()


class Program():
    def __init__(self, name, steps, step_time, step_mm=1, step_deg=1):
        self.name = name
        self.steps = steps
        self.step_time = step_time
        self.step_mm = step_mm
        self.step_deg = step_deg
        self.simulation_result = None
        self.robodk_program = None

    def load_to_robodk(self):
        clean_robodk()
        self.robodk_program = rdk.AddProgram("Prg", robot)
        for s in self.steps:
            self._add_step(s)

    def _add_step(self, step: Step):
        self.robodk_program.setPoseTool(step.tcpItem)
        self.robodk_program.setRounding(step.blending)

        target = rdk.AddTarget("Target_" + step.name + "_" + str(step.move_type), 0, robot)
        target.setVisible(False)

        if step.move_type == MoveType.Joint:
            target.setJoints(step.pose)
            target.setAsJointTarget()
            speed = step.speed if step.speed > 0 else JOINT_SPEED
            accel = step.accel if step.accel > 0 else JOINT_ACCEL
            self.robodk_program.setSpeed(-1, speed, -1, accel)
            self.robodk_program.MoveJ(target)

        if step.move_type == MoveType.Frame:
            target.setPose(xyzrp2ToPose(step.pose))
            target.setAsCartesianTarget()
            speed = step.speed if step.speed > 0 else FRAME_SPEED
            accel = step.accel if step.accel > 0 else FRAME_ACCEL
            self.robodk_program.setSpeed(speed, -1, accel, -1)
            self.robodk_program.MoveL(target)

    def simulate(self):
        self.simulation_result = self._get_simulation_result()
        move_id = 1
        for s in self.steps:
            s.playback_frames = self.simulation_result.get_playback_frames_for_move(move_id)
            move_id = move_id + 1

    def _get_simulation_result(self):
        flags = InstructionListJointsFlags.TimeBased
        error_msg, joint_list, error_code = self.robodk_program.InstructionListJoints(
            self.step_mm, self.step_deg, None, COLLISION_OFF, flags, self.step_time)
        result = InstructionListJointsResult(error_code, error_msg, joint_list)
        joints = self.robodk_program.getLink().Joints()
        n_joints, dummy = joints.size()
        _, rows = joint_list.size()
        errorIdx = n_joints
        speedIdx = n_joints + 1
        accelIdx = n_joints + 2
        idIdx = n_joints + 3
        timeIdx = n_joints + 4
        for i in range(rows):
            # def __init__(self, move_id, speed, accel, error, time_step):
            pose = []
            for j in range(n_joints):
                pose.append(joint_list[j, i])
            result.add_playback_frame(PlaybackFrame(
                pose, joint_list[idIdx, i], joint_list[speedIdx, i], joint_list[accelIdx, i], joint_list[errorIdx, i], joint_list[timeIdx, i]))
        return result

    def print(self):
        print(f"Program {self.name}:")
        for s in self.steps:
            s.print()
        print()


# ---------------- Convert Frame (x,y,z,rx,ry,rz) to a RoboDK Matrix ----------------------
def xyzrp2ToPose(pose):
    return Pose(pose[0], pose[1], pose[2], pose[3], pose[4], pose[5])
