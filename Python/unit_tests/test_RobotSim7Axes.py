"""Test RoboDK InstructionListJoints() for robot with 7 axes"""

from parameterized import parameterized_class
from path_simulation import *
from test_RobotSimBase import TestRobotSimBase


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
    return Program("Joint moves with axis 7", steps, 0.002)


def get_program_frame_no7(blending):
    """Test program with frame moves only and no need for move on axis 7"""
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


def get_program_frame_needs7(blending):
    """Test program with frame moves only and need for move on axis 7"""
    j1 = [93.159617, -88.450272, 102.407047, 40.002728, -3.531006, 222.007079, -349.000000]
    f2 = [-1182.036279, -765.087880, 701.262027, -168.883590, 8.659084, 0.839570]
    f3 = [1269.233826, -677.676136, 689.591527, -168.881372, 8.670023, 0.845444]
    f4 = [-518.379616, -778.795337, 648.891752, -168.883590, 8.659084, 0.839570]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Frame, 0, f2, blending, 0, 0),
        Step("3", MoveType.Frame, 0, f3, blending, 0, 0),
        Step("4", MoveType.Frame, 0, f4, blending, 0, 0),
    ]
    return Program("Frame moves with axis 7", steps, 0.002)


@parameterized_class(
    ("test_name", "sim_type", "blending"), [
        ("PosBased_NoBlending", InstructionListJointsFlags.Position, 0),
        ("PosBased_WithBlending", InstructionListJointsFlags.Position, 10),
        ("TimeBased_NoBlending", InstructionListJointsFlags.TimeBased, 0),
        ("TimeBased_WithBlending", InstructionListJointsFlags.TimeBased, 10)
    ])
class TestRobotSim7Axes(TestRobotSimBase):
    blending = None
    sim_type = None

    def _test_axis7_not_moving(self):
        steps = self.program.steps
        initial_position = steps[0].pose[6]
        for step in self.program.steps:
            for index, pb_frame in enumerate(step.playback_frames):
                msg = f"Step {step.name} playback frame {index}, axis 7 moved"
                self.assertEqual(pb_frame.joints[6, 0], initial_position, msg)

    def load_robot_cell(self):
        self.robot, self.tools = load_file(r"Robot7_2TCP.rdk")

    def test_joint_no7(self):
        """Test program with joint moves only, no moves on axis 7 needed"""
        self.program = get_program_joint_no7(self.blending)
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)
        self._test_axis7_not_moving()

    def test_joint_with7(self):
        """Test program with joint moves only, moves on axis 7 needed"""
        self.program = get_program_joint(self.blending)
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)

    def test_frame_no7(self):
        """Test program with frame moves, no moves on axis 7 needed"""
        self.program = get_program_frame_no7(self.blending)
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)
        self._test_axis7_not_moving()

    def test_frame_with7(self):
        """Test program with frame moves, moves on axis 7 needed"""
        self.program = get_program_frame_needs7(self.blending)
        self.program.simulation_type = self.sim_type
        self._test_program(verbose=False)


if __name__ == '__main__':
    unittest.main()
