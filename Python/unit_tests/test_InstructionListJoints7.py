"""Test RoboDK InstructionListJoints() for robot with 7 axes"""

from path_simulation import *
from base_tests import TestInstructionListJoints


def get_program_joint_no7(blending):
    """Test program with joint moves only and no move on axis 7"""
    j1 = [79.010000, -81.410000, 121.990000, 0.000000, -41.410000, 81.340000, -349.000000]
    j2 = [114.930000, -81.410000, 86.030000, 0.000000, 32.960000, 81.340000, -349.000000]
    j3 = [74.230000, -11.720000, -70.440000, -91.200000, -79.440000, -175.000000, -349.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Joint, 0, j2, blending, 0, 0),
        Step("3", MoveType.Joint, 0, j3, blending, 0, 0),
        Step("4", MoveType.Joint, 0, j1, blending, 0, 0),
    ]
    return Program("Joint moves no axis 7", steps, 0.002)


def get_program_joint(blending):
    """Test program with joint moves only and move on axis 7"""
    j1 = [79.010000, -81.410000, 121.990000, 0.000000, -41.410000, 81.340000, 0]
    j2 = [114.930000, -81.410000, 86.030000, 0.000000, 32.960000, 81.340000, -500]
    j3 = [74.230000, -11.720000, -70.440000, -91.200000, -79.440000, -175.000000, 500]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Joint, 0, j2, blending, 0, 0),
        Step("3", MoveType.Joint, 0, j3, blending, 0, 0),
        Step("4", MoveType.Joint, 0, j1, blending, 0, 0),
    ]
    return Program("Joint moves no axis 7", steps, 0.002)


def get_program_frame_no7(blending):
    """Test program with frame moves only and no move on axis 7"""
    j1 = [93.159617, -88.450272, 102.407047, 40.002728, -3.531006, 222.007079, -349.000000]
    f2 = [-327.415069, -740.090696, 758.628268, -168.883590, 8.659084, 0.839570]
    f3 = [-451.065405, -763.715914, 784.890641, -168.883590, 8.659084, 0.839570]
    f4 = [-518.379616, -778.795337, 648.891752, -168.883590, 8.659084, 0.839570]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Frame, 0, f2, blending, 0, 0),
        Step("3", MoveType.Frame, 0, f3, blending, 0, 0),
        Step("4", MoveType.Frame, 0, f4, blending, 0, 0),
    ]
    return Program("Frame moves no axis 7", steps, 0.002)


class TestInstructionListJoints7(TestInstructionListJoints):

    def load_robot_cell(self):
        self.robot, self.tools = load_file(r"Robot7_2TCP.rdk")

    def test_joint_no7_noBlending(self):
        """Test program with joint moves only, no moves on axis 7, no blending"""
        self.program = get_program_joint_no7(blending=0)
        self._test_program(verbose=False)

    def test_joint_no7_withBlending(self):
        """Test program with joint moves only, no moves on axis 7, blending"""
        self.program = get_program_joint_no7(blending=100)
        self._test_program(verbose=False)

    def test_joint_with7_noBlending(self):
        """Test program with joint moves only, moves on axis 7, no blending"""
        self.program = get_program_joint(blending=0)
        self._test_program(verbose=False)

    def test_joint_with7_withBlending(self):
        """Test program with joint moves only, moves on axis 7, blending"""
        self.program = get_program_joint(blending=100)
        self._test_program(verbose=False)

    def test_frame_no7_noBlending(self):
        """Test program with frame moves, no moves on axis 7, no blending"""
        self.program = get_program_frame_no7(blending=0)
        self._test_program(verbose=False)

    def test_frame_no7_withBlending(self):
        """Test program with frame moves, no moves on axis 7, blending"""
        self.program = get_program_frame_no7(blending=100)
        self._test_program(verbose=False)


if __name__ == '__main__':
    unittest.main()
