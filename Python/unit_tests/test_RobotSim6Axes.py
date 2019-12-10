"""Test RoboDK InstructionListJoints() for robot with 6 axes"""

from parameterized import parameterized_class
from path_simulation import *
from test_RobotSimBase import TestRobotSimBase


def get_program_one_stop_point():
    """Test program to simulate stop points"""
    j1 = [85.313866, -54.353057, 109.847412, 90.670697, -90.461034, 55.497054]
    f2 = [267.800000, -875.699998, 529.200000, -0.000000, 0.000000, -84.500000]
    f3 = [267.800000, -875.699998, 509.200000, -0.000000, 0.000000, -84.500000]
    f4 = [267.800000, -880.699998, 509.200000, -0.000000, 0.000000, -84.500000]
    f5 = [267.800000, -880.699998, 489.200000, -0.000000, 0.000000, -84.500000]
    f6 = [267.800000, -697.899998, 489.200000, -0.000000, 0.000000, -84.500000]
    j7 = [65.489465, -60.520188, 93.790655, 50.917749, 22.204378, 23.388239]
    f8 = [267.800005, -886.682405, 541.603646, 45.000000, 0.000000, 180.000000]
    f9 = [267.800000, -900.824545, 555.745785, 45.000000, 0.000000, 180.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, 10, 0, 0),
        Step("2", MoveType.Frame, 0, f2, 10, 0, 0),
        Step("3", MoveType.Frame, 0, f3, 10, 0, 0),
        Step("4", MoveType.Frame, 0, f4, 10, 0, 0),
        Step("5", MoveType.Frame, 0, f5, 10, 0, 0),
        Step("6", MoveType.Frame, 0, f6, 10, 0, 0),
        Step("7", MoveType.Joint, 0, j7, 10, 0, 0),
        Step("8", MoveType.Frame, 0, f8, 10, 0, 0),
        Step("9", MoveType.Frame, 0, f9, 10, 0, 0),
    ]
    steps[2].blending = 0
    return Program("Move to stop point", steps, 0.002)  # 0.055


def get_program_two_step_points():
    program = get_program_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    program.step_time = 0.033
    return program


def get_program_three_stop_points():
    program = get_program_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    steps[4].blending = 0
    program.step_time = 0.077
    return program


def get_program_rotate_in_place():
    """Test program to simulate rotation around point. Cartesian coordinates stay constant from f3 to f4."""

    j1 = [89.032848, -66.822879, 113.889182, 89.929968, -106.519502, -17.840590]
    f2 = [230.864307, -923.444947, 581.390218, 45.000000, 0.000000, -72.810208]
    f3 = [230.864307, -923.444947, 601.390218, 45.000000, -0.000000, -72.810208]
    f4 = [230.864307, -923.444947, 601.390218, 64.173180, 5.801359, -73.790852]
    f5 = [230.864307, -665.477946, 601.390218, 64.173180, 5.801359, -73.790852]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, 0, 0, 0),
        Step("2", MoveType.Frame, 0, f2, 0, 0, 0),
        Step("3", MoveType.Frame, 0, f3, 0, 0, 0),
        Step("4", MoveType.Frame, 0, f4, 0, 0, 0),
        Step("5", MoveType.Frame, 0, f5, 0, 0, 0),
    ]
    return Program("Rotate Robot Axis", steps, 0.002)  # 0.02


def get_program_near_singularity():
    """Test program to simulate near singularity"""
    j1 = [84.042754, -57.261200, 115.707342, 78.814999, -83.206905, 59.112086]
    f2 = [267.800000, -697.899998, 489.200000, -0.000000, -0.000000, -97.106527]
    f3 = [267.800000, -886.682410, 541.603649, 45.000000, 0.000000, 180.000000]
    f4 = [267.800000, -900.824545, 555.745785, 45.000000, 0.000000, 180.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, 10, 0, 0),
        Step("2", MoveType.Frame, 0, f2, 10, 0, 0),
        Step("3", MoveType.Frame, 0, f3, 10, 0, 0),
        Step("4", MoveType.Frame, 0, f4, 0, 0, 0),
    ]
    return Program("Near Singularity", steps, 0.04)


@parameterized_class(
    ("test_name", "sim_type"), [
        ("PosBased", InstructionListJointsFlags.Position),
        ("TimeBased", InstructionListJointsFlags.TimeBased)
    ])
class TestRobotSim6Axes(TestRobotSimBase):
    sim_type = None

    def load_robot_cell(self):
        self.robot, self.tools = load_file(r"Robot_2TCP.rdk")

    def test_one_stop_point(self):
        """Test program with one stop point"""
        self.program = get_program_one_stop_point()
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)

    def test_two_stop_points(self):
        """Test program with 2 adjacent stop points"""
        self.program = get_program_two_step_points()
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)

    def test_three_stop_points(self):
        """Test program with 3 adjacent stop points"""
        self.program = get_program_three_stop_points()
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)

    def test_rotate_in_place(self):
        """Test rotation around a const cartesian coordinate"""
        self.program = get_program_rotate_in_place()
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)
        self._test_if_cartesian_coordinates_const(2)

    def test_near_singularity1(self):
        """Test near singularity with STEP_MM=1, STEP_DEG=1"""
        self.program = get_program_near_singularity()
        self.program.simulation_type = self.sim_type
        self.program.step_mm = 1
        self.program.step_deg = 1
        self._test_program(verbose=False)

    def test_near_singularity2(self):
        """Test near singularity with STEP_MM=10, STEP_DEG=10"""
        self.program = get_program_near_singularity()
        self.program.simulation_type = self.sim_type
        self.program.step_mm = 10
        self.program.step_deg = 10
        self._test_program(verbose=False)


if __name__ == '__main__':
    unittest.main()
