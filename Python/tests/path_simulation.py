import sys
import time
from enum import Enum
import os


sys.path.insert(0, "..")
robolink_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.insert(0, robolink_path)

from robodk.robolink import *
from robodk.robomath import *

import_install("parameterized")


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

    set_robodk_option("AutoRenderDelay", 50)
    set_robodk_option("AutoRenderDelayMax", 300)
    rdk.Render(False)

    set_robodk_option("CollisionMap", "None")
    rdk.setCollisionActive(COLLISION_OFF)

    set_robodk_option("ToleranceSingularityWrist", 2.0)  # Threshold angle to avoid singularity for joint 5 (deg)
    set_robodk_option("ToleranceSingularityElbow", 3.0)  # Threshold angle to avoid singularity for joint 3 (deg)
    set_robodk_option("ToleranceSingularityBack", 20.0) # Wrist is close to Axis 1  [mm]
    set_robodk_option("ToleranceSmoothKinematic", 25)  # 25 deg
    set_robodk_option("ToleranceTurn180", 0.5)  # 25 deg

    return rdk

def set_robodk_option(option, value):
    valueAsString = str(value)
    result = rdk.Command(option, valueAsString)
    if result.lower() != "ok" :
        sys.exit(f"failed to set roboDK option {option} value {valueAsString}. Got return value: {result} instead of 'ok'")

def load_file(filename):
    """Load a RoboDK RDK file, get robot and return robot and tool item

    Args:
        filename (string): filename of a RoboDK rdk file

    Returns:
        IItem: robot
        IItem: tool
    """
    global robot
    global tools

    rdk.CloseStation()
    rdk.AddFile(os.path.realpath("./tests/"+filename))
    robot = rdk.Item("", ITEM_TYPE_ROBOT_ARM)
    tools = rdk.ItemList(ITEM_TYPE_TOOL)

    return robot, tools


def reset_robodk_state():
    if rdk is not None:
        items = rdk.ItemList(ITEM_TYPE_TARGET)
        for item in items:
            item.Delete()
        items = rdk.ItemList(ITEM_TYPE_PROGRAM)
        for item in items:
            item.Delete()
        robot.setJoints(robot.JointsHome())


def print_info():
    print()
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
        n_joints, _ = robot.Joints().size()
        if n_joints == 1:
            n_joints = 7  # this is needed because the 1-axis linear robot is returned when actually we want the 7-axis robot
        sequence = self.joints[:n_joints, :]
        robot.ShowSequence(sequence)

    def print(self):
        print("---- InstructionListJointsResult ------------------------")
        print(" > Error Msg:  ", self.message)
        print(" > Error Code: ", self.error)
        print(" > Joints:")
        print(self.joints.tr())


class PlaybackFrame():
    def __init__(self, joints, coords, move_id, error, mm_step, deg_step, time_step, speeds, accels):
        self.joints = joints
        self.coords = coords
        self.move_id = move_id
        self.error = error
        self.mm_step = mm_step
        self.deg_step = deg_step
        self.time_step = time_step
        self.speeds = speeds
        self.accels = accels
        self.error_string = str(ConvertErrorCodeToJointErrorType(self.error))
        self.error_flags = ConvertErrorCodeToJointErrorType(self.error)

    def print(self):
        joint_string = ", ".join([f"{j[0]:>7.2f}" for j in self.joints.rows])
        coord_string = ", ".join([f"{c[0]:>7.2f}" for c in self.coords.rows])
        speed_string = ", ".join([f"{s[0]:>7.2f}" for s in self.speeds.rows]) if self.speeds is not None else "-"
        accel_string = ", ".join([f"{a[0]:>7.2f}" for a in self.accels.rows]) if self.accels is not None else "-"
        print(f" > PlaybackFrame | moveid:{self.move_id:2.0f}",
              f"| error:{self.error}, dtime:{self.time_step:>6.3f}, dmm:{self.mm_step:>6.2f}, ddeg:{self.deg_step:>6.2f}",
              f"||| joints: {joint_string}",
              f"\n\t\t coords: {coord_string}",
              f"\n\t\t speeds: {speed_string}",
              f"\n\t\t accels: {accel_string}")


MoveType = Enum('MoveType', 'Joint Frame Arc')


class Step():
    def __init__(self, name, move_type, tcp, pose, blending, speed, accel, expected_error_flags=PathErrorFlags.NoError, pose2=None):
        self.name = name
        self.move_type = move_type
        self.tcp = tcp
        self.pose = pose
        self.pose2 = pose2 # for arc moves
        self.speed = speed
        self.accel = accel
        self.blending = blending
        self.tcp_item = tools[tcp]
        self.tcp_name = tools[tcp].Name()
        self.playback_frames = []
        self.expected_error_flags = expected_error_flags

    def print(self):
        print(f"Step '{self.name}' ({self.move_type}) ::: ",
              f"tcp: {self.tcp_name}, blending: {self.blending}, speed: {self.speed:.3f}, accel: {self.accel:.3f}")
        for f in self.playback_frames:
            f.print()
        print()


def get_frame_pose(step, playback_frame):
    robot.setPoseTool(step.tcp_item)
    robot.setJoints(playback_frame.joints)
    joints = robot.Pose()
    framePose = Pose_2_Staubli(joints)
    return framePose


class Program():
    def __init__(self, name, steps, max_time_step=0.02, max_mm_step=1, max_deg_step=1,
                 simulation_type=InstructionListJointsFlags.TimeBased):
        self.name = name
        self.steps = steps
        self.max_time_step = max_time_step
        self.max_mm_step = max_mm_step
        self.max_deg_step = max_deg_step
        self.simulation_type = simulation_type
        self.simulation_result = None
        self.robodk_program = None
        self.calc_time = None

    def load_to_robodk(self):
        self.robodk_program = rdk.AddProgram("Prg", robot)
        for s in self.steps:
            self._add_step(s)

    def _add_step(self, step: Step):
        self.robodk_program.setPoseTool(step.tcp_item)
        self.robodk_program.setRounding(step.blending)

        target = rdk.AddTarget("Target_" + step.name + "_" + str(step.move_type), 0, robot)
        target.setVisible(False)

        if step.move_type == MoveType.Joint:
            target.setJoints(step.pose)
            target.setAsJointTarget()
            speed = step.speed if step.speed > 0.0 else JOINT_SPEED
            accel = step.accel if step.accel > 0.0 else JOINT_ACCEL
            self.robodk_program.setSpeed(-1, speed, -1, accel)
            self.robodk_program.MoveJ(target)

        if step.move_type == MoveType.Frame:
            target.setPose(xyzrp2ToPose(step.pose[:6]))
            if len(step.pose) == 7:
                axis7 = step.pose[6]
                target.setJoints([0, 0, 0, 0, 0, 0, axis7])
            target.setAsCartesianTarget()
            speed = step.speed if step.speed > 0.0 else FRAME_SPEED
            accel = step.accel if step.accel > 0.0 else FRAME_ACCEL
            self.robodk_program.setSpeed(speed, -1, accel, -1)
            self.robodk_program.MoveL(target)
            
        if step.move_type == MoveType.Arc:
            target.setPose(xyzrp2ToPose(step.pose[:6]))
            if len(step.pose) == 7:
                axis7 = step.pose[6]
                target.setJoints([0, 0, 0, 0, 0, 0, axis7])
            target.setAsCartesianTarget()
            
            target2 = rdk.AddTarget("Target_" + step.name + "_" + str(step.move_type) + "_2", 0, robot)
            target2.setVisible(False)
            target2.setPose(xyzrp2ToPose(step.pose2[:6]))
            if len(step.pose2) == 7:
                axis7 = step.pose2[6]
                target2.setJoints([0, 0, 0, 0, 0, 0, axis7])
            target2.setAsCartesianTarget()           
            
            speed = step.speed if step.speed > 0.0 else FRAME_SPEED
            accel = step.accel if step.accel > 0.0 else FRAME_ACCEL
            self.robodk_program.setSpeed(speed, -1, accel, -1)
            self.robodk_program.MoveC(target, target2)

    def simulate(self):
        self.simulation_result = self._get_simulation_result()
        move_id = 1
        for s in self.steps:
            s.playback_frames = self.simulation_result.get_playback_frames_for_move(move_id)
            move_id = move_id + 1

    def _get_simulation_result(self):
        flag = InstructionListJointsFlags.TimeBased

        t_start = time.time()
        error_msg, joint_list, error_code = self.robodk_program.InstructionListJoints(
            mm_step=self.max_mm_step,
            deg_step=self.max_deg_step,
            time_step=self.max_time_step,
            collision_check=COLLISION_OFF,
            flags=self.simulation_type)

        self.calc_time = time.time() - t_start

        result = InstructionListJointsResult(error_code, error_msg, joint_list)

        joints = self.robodk_program.getLink().Joints()
        n_joints, _ = joints.size()
        _, rows = joint_list.size()

        joints = joint_list[:n_joints]
        errors = joint_list[n_joints]
        mm_steps = joint_list[n_joints + 1]
        deg_steps = joint_list[n_joints + 2]
        move_ids = joint_list[n_joints + 3]
        time_steps = joint_list[n_joints + 4]
        coords = joint_list[(n_joints + 5):(n_joints + 8)]

        speeds = None
        accels = None

        if flag.value >= 2:
            i_from = n_joints + 8
            i_to = i_from + n_joints
            speeds = joint_list[i_from:i_to]

        if flag.value >= 3:
            i_from = n_joints + 8 + n_joints
            i_to = i_from + n_joints
            accels = joint_list[i_from:i_to]

        for i in range(rows):
            result.add_playback_frame(
                PlaybackFrame(
                    joints=joints[:, i],
                    coords=coords[:, i],
                    move_id=move_ids[0, i],
                    error=errors[0, i],
                    mm_step=mm_steps[0, i],
                    deg_step=deg_steps[0, i],
                    time_step=time_steps[0, i],
                    speeds=speeds[:, i] if speeds else None,
                    accels=accels[:, i] if accels else None
                )
            )
        return result

    def print(self):
        print(f"\n\n-------------------------------------------------")
        print(f"\tProgram '{self.name}'")
        if self.simulation_type == InstructionListJointsFlags.Position:
            print(f"\t > Position Based (Max mm step: {self.max_mm_step}, Max deg step: {self.max_deg_step})")
        elif self.simulation_type == InstructionListJointsFlags.TimeBased:
            print(f"\t > Time Based (Max time step: {self.max_time_step})")
        else:
            print(f"\t > Simulation Type: {self.simulation_type}")
        print(f"\t > Steps:\n")
        for s in self.steps:
            s.print()
        print()


# ---------------- Convert Frame (x,y,z,rx,ry,rz) to a RoboDK Matrix ----------------------
def xyzrp2ToPose(pose):
    #from robodk.robomath import Pose
    return Pose(pose[0], pose[1], pose[2], pose[3], pose[4], pose[5])
