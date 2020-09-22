"""Test RoboDK InstructionListJoints() for robot with 6 axes"""

from parameterized import parameterized_class
from path_simulation import *
import test_RobotSimBase


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
    return Program("Move to stop point", steps)


def get_program_two_step_points():
    program = get_program_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    return program


def get_program_three_stop_points():
    program = get_program_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    steps[4].blending = 0
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
    return Program("Rotate Robot Axis", steps)


def get_program_kinematic_path_limit():
    """Test program to simulate a path which is near kinematic limits"""
    j1 = [-124.574187, -103.845852, 105.005701, 36.135749, 64.419738, 141.994562]
    f2 = [-331.304132, 504.922772, 657.678757, -179.352793, -74.861742, -129.551949]
    f3 = [-306.399431, 504.846666, 664.415974, -179.352793, -74.861742, -129.551949]
    f4 = [-284.734545, 535.609932, 572.673677, -179.924808, -74.974404, 134.877210]
    f5 = [-309.652446, 535.618709, 565.985019, -179.924808, -74.974404, 134.877210]
    f6 = [-307.385836, 535.371153, 595.898247, -179.924808, -74.974404, 134.877210]
    f7 = [-257.440848, 534.015376, 755.909684, -179.924808, -74.974404, 134.877210]
    j8 = [-106.722253, -86.501522, 133.588205, -1.536958, -90.366601, 202.291369]
    j9 = [-13.025748, -109.978175, 108.893260, -49.847042, -86.956596, -214.386461]
    j10 = [73.561315, -112.163318, 75.775272, 85.295770, -23.438906, -249.258227]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, 10, 0, 0),
        Step("2", MoveType.Frame, 0, f2, 0, 0, 0),
        Step("3", MoveType.Frame, 0, f3, 1, 0, 0),
        Step("4", MoveType.Frame, 0, f4, 1, 0, 0),
        Step("5", MoveType.Frame, 0, f5, 0, 0, 0),
        Step("6", MoveType.Frame, 0, f6, 1, 0, 0),
        Step("7", MoveType.Frame, 0, f7, 1, 0, 0),
        Step("8", MoveType.Joint, 0, j8, 10, 0, 0),
        Step("9", MoveType.Joint, 0, j9, 10, 0, 0),
        Step("10", MoveType.Joint, 0, j10, 10, 0, 0),
    ]
    return Program("Kinematic Path Limit", steps)


def get_program_RDK_90():
    """Test program was previously crashing during path simulation."""
    j1 = [-0.000000, -110.000000, 120.000000, -0.000000, 30.000000, -90.000000]
    j2 = [-30.188110, -65.220803, 95.184225, -101.467343, 61.477418, 16.537955]
    j3 = [-33.299586, -77.893652, 117.376522, -150.782405, 28.335008, 59.561379]
    f4 = [   531.542045,   473.107081,   430.414010,   175.000001,   -15.000001,  -136.838065 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0),
        Step("J2", MoveType.Joint, 0, j2, 0, 0, 0),
        Step("J3", MoveType.Joint, 0, j3, 10, 0, 0),
        Step("F4", MoveType.Frame, 0, f4, 1, 0, 0),
    ]
    return Program("RDK-90", steps)
    
    
def get_program_Arc_ValidMove():
    """Test program was previously crashing during path simulation."""
    j1 = [85.313866, -54.353057, 109.847412, 90.670697, -90.461034, 55.497054]
    f1 = [   252.127218,  -530.131963,   529.199999,   -84.500000,    -0.000001,    -0.000000 ]
    f2 = [   384.041242,  -453.856457,   529.200000,   -84.500000,    -0.000001,    -0.000000 ]
    f3 = [   289.724650,  -298.049571,   529.200000,   -84.500000,    -0.000001,    -0.000000 ]

    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("J1", MoveType.Joint, 0, j1, 0, 0, 0),
        Step("F1", MoveType.Frame, 0, f1, 0, 0, 0),
        Step("F2", MoveType.Arc, 0, f2, 0, 0, 0, PathErrorFlags.NoError, f3),
    ]
    return Program("ValidArcMove", steps)



@parameterized_class(
    ("test_name", "sim_type", "sim_step_mm", "sim_step_deg", "sim_step_time"), [
        (f"PosBased({test_RobotSimBase.sim_step_mm_S:0.1f}mm,{test_RobotSimBase.sim_step_deg_S:0.1f}deg)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.Position, test_RobotSimBase.sim_step_mm_S, test_RobotSimBase.sim_step_deg_S, None),
        (f"PosBased({test_RobotSimBase.sim_step_mm_L:0.1f}mm,{test_RobotSimBase.sim_step_deg_L:0.1f}deg)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.Position, test_RobotSimBase.sim_step_mm_L, test_RobotSimBase.sim_step_deg_L, None),
        (f"TimeBased({test_RobotSimBase.step_time_S:0.4f}ms)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_S),
        (f"TimeBased({test_RobotSimBase.step_time_M:0.4f}ms)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_M),
        (f"TimeBased({test_RobotSimBase.step_time_L:0.4f}ms)".replace(".", test_RobotSimBase.dot_repr),
         InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_L)
    ])
class TestRobotSim6Axes(test_RobotSimBase.TestRobotSimBase):

    def load_robot_cell(self):
        """Load RobotCell. called from test_RobotSimBase.setUp()"""
        self.robot, self.tools = load_file(r"Robot_2TCP.rdk")

    def test_one_stop_point(self):
        """Test program with one stop point"""
        self.program = get_program_one_stop_point()
        self._test_program(verbose=False)

    def test_two_stop_points(self):
        """Test program with 2 adjacent stop points"""
        self.program = get_program_two_step_points()
        self._test_program(verbose=False)

    def test_three_stop_points(self):
        """Test program with 3 adjacent stop points"""
        self.program = get_program_three_stop_points()
        self._test_program(verbose=False)

    def test_rotate_in_place(self):
        """Test rotation around a const cartesian coordinate"""
        self.program = get_program_rotate_in_place()
        self._test_program(verbose=False)
        self._test_if_cartesian_coordinates_const(2)

    def test_kinematic_path_limit(self):
        """Test KinematicPathLimit"""
        if self.sim_type == InstructionListJointsFlags.TimeBased and self.sim_step_time >= 0.02:
            #simulation not possible with simulation time step > 20[ms]
            return
        self.program = get_program_kinematic_path_limit()
        self._test_program(verbose=False)

    def test_kinematic_RDK_90(self):
        """Test RDK-90"""
        self.program = get_program_RDK_90()
        self._test_program(verbose=False)
        
    def test_kinematic_Arc_ValidMove(self):
        """Test RDK-90"""
        self.program = get_program_Arc_ValidMove()
        self._test_program(verbose=False)       
        

if __name__ == '__main__':
    unittest.main()
