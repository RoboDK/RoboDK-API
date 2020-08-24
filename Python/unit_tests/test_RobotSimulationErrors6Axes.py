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


def get_program_RDK_91():
    """Test program simulation error should not return success message."""
    j1 = [-124.420433, -100.220908, 123.962337, 23.242314, 63.944991, 137.508752]
    f2 = [  -278.518943,   436.007618,   547.030830,   179.789916,   -74.994562,   -47.567604 ]
    f3 = [  -303.439195,   435.983125,   540.350978,   179.789916,   -74.994562,   -47.567604 ]
    f4 = [  -301.172585,   435.735568,   570.264206,   179.789916,   -74.994562,   -47.567604 ]
    f5 = [  -231.253202,   513.686454,   655.467183,   179.789916,   -74.994562,  -118.578163 ]
    j6 = [-116.562035, -101.182577, 117.673968, 29.901480, 56.537640, 144.298732]
    j7 = [-69.323892, -117.000000, 116.917103, 3.454614, 34.862541, -15.159028]
    j8 = [69.928026, -109.590561, 148.647412, -21.437124, -0.098633, -8.370814]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("J1", MoveType.Joint, 0, j1, 10, 0, 0),
        Step("F2", MoveType.Frame, 0, f2, 1, 0, 0),
        Step("F3", MoveType.Frame, 0, f3, 0, 0, 0),
        Step("F4", MoveType.Frame, 0, f4, 1, 0, 0),
        Step("F5", MoveType.Frame, 0, f5, 1, 0, 0),
        Step("J6", MoveType.Joint, 0, j6, 10, 0, 0),
        Step("J7", MoveType.Joint, 0, j7, 10, 0, 0),
        Step("J8", MoveType.Joint, 0, j8, 10, 0, 0, 1000),
    ]
    return Program("RDK-91", steps)

def get_program_RDK_93_target_can_not_be_reached():
    """Target StepId 65 can not be reached"""
    j1 = [-121.962375, -102.168116, 105.538444, 18.089514, 86.239362, 148.055458]

    f2 = [  -307.346432,   439.570058,   576.803381,  -179.352794,   -74.861742,   -99.294176 ]
    f3 = [  -282.441732,   439.493952,   583.540599,  -179.352794,   -74.861742,   -99.294176 ]
    f4 = [  -267.103305,   434.010573,   516.128581,   179.777317,   -74.944947,   -33.895889 ]
    f5 = [  -292.017764,   433.984527,   509.427158,   179.777317,   -74.944947,   -33.895889 ]
    f6 = [  -289.751154,   433.736971,   539.340385,   179.777317,   -74.944947,   -33.895889 ]
    f7 = [  -239.806166,   432.381194,   699.351823,   179.777317,   -74.944947,   -33.895889 ]
    j8 = [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]
    j9 = [79.238350, -54.625500, 102.860318, -115.621424, 68.885526, -126.911760]
    f10 = [   312.309807,  -910.024549,   574.500010,    -0.000000,     0.000000,  -111.978180 ]


    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("StepId 61", MoveType.Joint, 0, j1, 10, 0, 0),
        Step("StepId 58", MoveType.Frame, 0, f2, 0, 0, 0),
        Step("StepId 62", MoveType.Frame, 0, f3, 10, 0, 0),
        Step("StepId 63", MoveType.Frame, 0, f4, 10, 0, 0),
        Step("StepId 60", MoveType.Frame, 0, f5, 0, 0, 0),
        Step("StepId 64", MoveType.Frame, 0, f6, 10, 0, 0),
        Step("StepId 65", MoveType.Frame, 0, f7, 10, 0, 0, 1000000),  ## TODO: Add expected simulation Error code for target not reachable.
        Step("StepId 66", MoveType.Joint, 0, j8, 10, 0, 0, 0),
        Step("StepId 81", MoveType.Joint, 0, j9, 10, 0, 0, 0),
        Step("StepId 83", MoveType.Frame, 0, f10, 1, 0, 0, 0),
    ]
    return Program("target_StepId65_can_not_be_reached", steps)

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

    def test_program_rdk_91(self):
        """Test singularity error"""
        self.program = get_program_RDK_91()
        self._test_program(verbose=False)

    def test_program_rdk_93(self):
        """One or more targets are not reachable or missing."""
        self.program = get_program_RDK_93_target_can_not_be_reached()
        self._test_program(verbose=False)
       

if __name__ == '__main__':
    unittest.main()
