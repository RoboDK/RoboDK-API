"""Test RoboDK InstructionListJoints() with expected simulation errors for robot with 6 axes"""

from parameterized import parameterized_class
from path_simulation import *
import test_RobotSimBase


def get_program_near_singularity():
    """Test program to simulate near singularity"""
    j1 = [84.042754, -57.261200, 115.707342, 78.814999, -83.206905, 59.112086]
    f2 = [267.800000, -697.899998, 489.200000, -0.000000, -0.000000, -97.106527]
    f3 = [267.800000, -886.682410, 541.603649, 45.000000, 0.000000, 180.000000]
    f4 = [267.800000, -900.824545, 555.745785, 45.000000, 0.000000, 180.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("1", MoveType.Joint, 0, j1, 10, 0, 0, 0),
        Step("2", MoveType.Frame, 0, f2, 10, 0, 0, 0),
        Step("3", MoveType.Frame, 0, f3, 10, 0, 0, [110,1000]), # Wrist singularity (could be 1000 or 100)
        Step("4", MoveType.Frame, 0, f4, 0, 0, 0, 0), # Wrist singularity (could be 1000 or 100)
    ]
    return Program("Near Singularity", steps)


def get_program_moveId0():
    """Test program to simulate a path which is near kinematic limits"""
    j1 = [ 58.871249, -78.599411,  143.944527, 173.481676, 65.485694,   -87.285718]
    f2 = [247.580323, -793.574636, 574.200001, 0.000000,   -0.000000,  -154.799784]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0, [110,1000]), # Wrist singularity (could be 1000 or 100)
    ]
    return Program("MoveId0", steps)


def get_program_180degree_rotation_error():
    """180 degree rotation error. Test PathFlipAxis Error."""
    j1 = [ 62.800000, -58.000000, 114.300000, -31.700000, -60.300000, 107.000000]
    f2 = [   247.718647,  -776.118962,   544.157022,     0.122916,     0.048975,  -179.957772 ]
    f3 = [   334.584051,  -775.717015,   386.683215,  -179.877084,    -0.048975,    -0.042228 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0, 0),
        Step("F3", MoveType.Frame, 0, f3, 1, 0, 0, 2000), # Elbow singularity
    ]
    return Program("180 degree rotation error", steps)

def get_program_axis_limit_error():
    """Axis limit error: joint 5 crosses 0 degrees -> singularity"""
    j1 = [ 86.567590, -60.878784, 114.472076, -92.763651, 87.963609, -126.357581]
    f2 = [   247.500000,  -869.864902,   574.200001,     0.000001,     0.000000,   -90.000000 ]
    f3 = [   247.500000,  -869.864902,   554.200001,     0.000001,     0.000000,   -90.000000 ]
    f4 = [   247.500000,  -874.864902,   554.200001,     0.000001,     0.000000,   -90.000000 ]
    f5 = [   247.500000,  -874.864902,   545.600001,     0.000001,     0.000000,   -90.000000 ]
    f6 = [   271.556017,  -835.575197,   545.600001,     0.000001,     0.000000,   148.521999 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0, 0),
        Step("F3", MoveType.Frame, 0, f3, 1, 0, 0, 0),
        Step("F4", MoveType.Frame, 0, f4, 1, 0, 0, 0),
        Step("F5", MoveType.Frame, 0, f5, 1, 0, 0, 0),  
        Step("F6", MoveType.Frame, 0, f6, 1, 0, 0, [110, 10]), # Wrist singularity (could be 1000 or 100), step too high is 10
    ]
    return Program("axis_limit_error", steps)

def get_program_smooth_kinematic_error():
    """To large movement in short time. Crossing ToleranceSmoothKinematic limit"""
    j1 = [ -121.731234, -105.839164, 118.925433, 44.376981, 49.562618, 133.063482]
    f2 = [  -305.479377,   506.206249,   561.080615,  -179.352790,   -74.861742,  -134.816977 ]
    f3 = [  -280.574677,   506.130142,   567.817833,  -179.352790,   -74.861742,  -134.816977 ]
    f4 = [  -277.584253,   506.915648,   544.586082,   179.947088,   -75.021714,   -45.217495 ]
    f5 = [  -302.700873,   506.909442,   537.866308,   179.947088,   -75.021714,   -45.217495 ]
    f6 = [  -300.434263,   506.661885,   567.779535,   179.947088,   -75.021714,   -45.217495 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0, 0),
        Step("F3", MoveType.Frame, 0, f3, 1, 0, 0, 0),
        Step("F4", MoveType.Frame, 0, f4, 1, 0, 0, 10),  # Control Step exceeded
        Step("F5", MoveType.Frame, 0, f5, 1, 0, 0, 0),  
        Step("F6", MoveType.Frame, 0, f6, 1, 0, 0, 0),
    ]
    return Program("smooth kinematic limit error", steps)

def get_program_front_back_singularity_wrist_close_to_axis_1():
    """The robot is too close to the front/back singularity (wrist to close to axis 1)"""
    j1 = [ 106.000000, -52.000000, -79.000000, -81.000000, 58.000000, -47.000000]
    f2 = [   681.000000,  -417.900000,  1063.200000,    -0.000000,   -77.000000,   180.000000 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel, expected_error):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0, [10,4000]),  # Front/back singularity is 4000
    ]
    return Program("singularity (wrist to close to axis 1) error", steps)


@parameterized_class(
    ("test_name", "sim_type", "sim_step_mm", "sim_step_deg", "sim_step_time"), [
        (f"TimeBasedX({test_RobotSimBase.step_time_RM:0.4f}ms)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_RM)
    ])
class TestRobotSimulationError6Axes(test_RobotSimBase.TestRobotSimBase):

    def load_robot_cell(self):
        self.robot, self.tools = load_file(r"Robot_2TCP.rdk")

    def test_moveId0(self):
        """Test program move ID0"""
        self.program = get_program_moveId0()
        self._test_program(verbose=False)

    def test_180degree_rotation_error(self):
        """Test program move ID0"""
        self.program = get_program_180degree_rotation_error()
        self._test_program(verbose=False)

    def test_near_singularity(self):
        """Test program near singulary error"""
        self.program = get_program_near_singularity()
        self._test_program(verbose=False)

    def test_axis_limit_error(self):
        """Test axis limit error: singularity"""
        self.program = get_program_axis_limit_error()
        self._test_program(verbose=False)

    def test_smooth_kinematic_error(self):
        """Test smoothe kinematic error (axis movement to large in one step)"""
        self.program = get_program_smooth_kinematic_error()
        self._test_program(verbose=False)

    def test_wrist_close_to_axis_1_error(self):
        """Test smoothe kinematic error (axis movement to large in one step)"""
        self.program = get_program_front_back_singularity_wrist_close_to_axis_1()
        self._test_program(verbose=False)


if __name__ == '__main__':
    unittest.main()
