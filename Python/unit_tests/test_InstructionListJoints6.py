"""Test RoboDK InstructionListJoints() for robot with 6 axes"""

import unittest
from path_simulation import *


def get_test_program_with_one_stop_point():
    """Test program to simulate stop points"""
    jointpos1 = [85.313866, -54.353057, 109.847412, 90.670697, -90.461034, 55.497054]
    framepos1 = [267.800000, -875.699998, 529.200000, -0.000000, 0.000000, -84.500000]
    framepos2 = [267.800000, -875.699998, 509.200000, -0.000000, 0.000000, -84.500000]
    framepos3 = [267.800000, -880.699998, 509.200000, -0.000000, 0.000000, -84.500000]
    framepos4 = [267.800000, -880.699998, 489.200000, -0.000000, 0.000000, -84.500000]
    framepos5 = [267.800000, -697.899998, 489.200000, -0.000000, 0.000000, -84.500000]
    jointpos2 = [65.489465, -60.520188, 93.790655, 50.917749, 22.204378, 23.388239]
    framepos6 = [267.800005, -886.682405, 541.603646, 45.000000, 0.000000, 180.000000]
    framepos7 = [267.800000, -900.824545, 555.745785, 45.000000, 0.000000, 180.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, jointpos1, 10, 0, 0),
        Step("2", MoveType.Frame, 0, framepos1, 10, 0, 0),
        Step("3", MoveType.Frame, 0, framepos2, 10, 0, 0),
        Step("4", MoveType.Frame, 0, framepos3, 10, 0, 0),
        Step("5", MoveType.Frame, 0, framepos4, 10, 0, 0),
        Step("6", MoveType.Frame, 0, framepos5, 10, 0, 0),
        Step("7", MoveType.Joint, 0, jointpos2, 10, 0, 0),
        Step("8", MoveType.Frame, 0, framepos6, 10, 0, 0),
        Step("9", MoveType.Frame, 0, framepos7, 10, 0, 0),
    ]
    steps[2].blending = 0
    return Program("Move to stop point", steps, 0.002)  # 0.055


def get_test_program_with_two_stop_points():
    program = get_test_program_with_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    program.step_time = 0.033
    return program


def get_test_program_with_three_stop_points():
    program = get_test_program_with_one_stop_point()
    steps = program.steps
    steps[2].blending = 0
    steps[3].blending = 0
    steps[4].blending = 0
    program.step_time = 0.077
    return program


##
# Robot rotates around a point.
# framepos2 - framepos3: rotate robot axis. Cartesian coordinates stay constant
##
def get_test_program_rotate():
    """Test program to simulate rotation around point"""
    jointpos1 = [89.032848, -66.822879, 113.889182, 89.929968, -106.519502, -17.840590]
    framepos1 = [230.864307, -923.444947, 581.390218, 45.000000, 0.000000, -72.810208]
    framepos2 = [230.864307, -923.444947, 601.390218, 45.000000, -0.000000, -72.810208]
    framepos3 = [230.864307, -923.444947, 601.390218, 64.173180, 5.801359, -73.790852]
    framepos4 = [230.864307, -665.477946, 601.390218, 64.173180, 5.801359, -73.790852]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, jointpos1, 0, 0, 0),
        Step("2", MoveType.Frame, 0, framepos1, 0, 0, 0),
        Step("3", MoveType.Frame, 0, framepos2, 0, 0, 0),
        Step("4", MoveType.Frame, 0, framepos3, 0, 0, 0),
        Step("5", MoveType.Frame, 0, framepos4, 0, 0, 0),
    ]
    return Program("Rotate Robot Axis", steps, 0.002)  # 0.02


def get_test_program_near_singularity():
    """Test program to simulate near singularity"""
    jointpos1 = [84.042754, -57.261200, 115.707342, 78.814999, -83.206905, 59.112086]
    framepos1 = [267.800000, -697.899998, 489.200000, -0.000000, -0.000000, -97.106527]
    framepos2 = [267.800000, -886.682410, 541.603649, 45.000000, 0.000000, 180.000000]
    framepos3 = [267.800000, -900.824545, 555.745785, 45.000000, 0.000000, 180.000000]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, jointpos1, 10, 0, 0),
        Step("2", MoveType.Frame, 0, framepos1, 10, 0, 0),
        Step("3", MoveType.Frame, 0, framepos2, 10, 0, 0),
        Step("4", MoveType.Frame, 0, framepos3, 0, 0, 0),
    ]
    return Program("Near Singularity", steps, 0.04)


class TestInstructionListJoints(unittest.TestCase):
    rdk = None
    robot = None
    tools = None

    def setUp(self):
        self.program = None
        self.rdk = init_robodk()
        self.robot, self.tools = load_file(r"Robot_2TCP.rdk")
        clean_robodk()

    def tearDown(self):
        if self.rdk is not None:
            self.rdk.Disconnect()

    def get_frame_pose(self, step, frame):
        self.robot.setPoseTool(step.tcpItem)
        self.robot.setJoints(frame.pose)
        joints = self.robot.Pose()
        framePose = Pose_2_Staubli(joints)
        return framePose

    def _test_result_message(self):
        """Test if return message of InstructionListJoints() is 'success' """
        result = self.program.simulation_result
        self.assertEqual(
            result.message.lower(),
            "success",
            f"Step {self.program.name} InstructionJointList result: {result.message}")

    def _test_for_missing_move_ids(self):
        """For each Step we should have at least one playback frame"""
        steps = self.program.steps
        move_id = 0
        for s in steps:
            move_id = move_id + 1
            msg = f"Step {s.name} has no playbackFrames. Move Id {move_id} is missing"
            self.assertNotEqual(len(s.playback_frames), 0, msg)

    def _test_for_valid_move_ids(self):
        """Each Frame must have a valid move id > 0"""
        playback_frames = self.program.simulation_result.playback_frames
        maxmove_id = len(self.program.steps)
        for idx, f in enumerate(playback_frames):
            msg = f"Frame {idx} has invalid move id {f.move_id}. Move id must be between 1 and {maxmove_id}"
            self.assertGreaterEqual(f.move_id, 1, msg)
            self.assertLessEqual(f.move_id, maxmove_id, msg)

    def _test_for_playback_frame_errors(self):
        """Check all playback frames for each step for errors"""
        steps = self.program.steps
        for s in steps:
            for idx, f in enumerate(s.playback_frames):
                resultMessage = self.program.simulation_result.message.lower()
                if resultMessage == "success":
                    msg = f"Step {s.name} frame number {idx} has a simulation error: {f.errorString} but program result is: {self.program.simulation_result.message}"
                else:
                    msg = f"Step {s.name} frame number {idx} has a simulation error: {f.errorString}"
                self.assertEqual(f.error, 0, msg)

    def _test_if_target_reached(self):
        steps = self.program.steps
        for s in steps:
            if s.blending == 0:
                lastFrame = s.playback_frames[-1]
                expectedFramePose = self.get_frame_pose(s, lastFrame)
                delta = 1e-06
                msg = f"Step {s.name} is a stop point. Exact target position should be reached"
                if(s.move_type == MoveType.Frame):
                    for idx, value in enumerate(expectedFramePose):
                        self.assertAlmostEqual(s.pose[idx], value, msg=msg, delta=delta)

    def _test_if_cartesian_coordinates_const(self, stepIdx):
        steps = self.program.steps
        startStep = steps[stepIdx]
        playbackFrame = startStep.playback_frames[-1]
        refFramePose = self.get_frame_pose(startStep, playbackFrame)
        endStep = steps[stepIdx + 1]
        for index, playbackFrame in enumerate(endStep.playback_frames):
            framePose = self.get_frame_pose(endStep, playbackFrame)
            delta = 1e-06
            for i in range(3):
                msg = f"step {endStep.name} playback frame {index},{i} has not the same position. refFrame{refFramePose[:3]}, step frame {framePose[:3]}"
                self.assertAlmostEqual(framePose[i], refFramePose[i], msg=msg, delta=delta)

    def _test_program_with_stop_points(self):
        self.program.load_to_robodk()
        self.program.simulate()
        self._test_for_valid_move_ids()
        self._test_for_playback_frame_errors()
        self._test_result_message()
        self._test_for_missing_move_ids()
        self._test_if_target_reached()

    def test_prgoramWithOneStopPoint(self):
        """Test Robot Program with one stop points"""
        self.program = get_test_program_with_one_stop_point()
        self._test_program_with_stop_points()

    def test_prgoramWithTwoStopPoints(self):
        """Test Robot Program with 2 adjacent stop points"""
        self.program = get_test_program_with_two_stop_points()
        self._test_program_with_stop_points()

    def test_prgoramWithThreeStopPoints(self):
        """Test Robot Program with 3 adjacent stop points"""
        self.program = get_test_program_with_three_stop_points()
        self._test_program_with_stop_points()

    def test_programRotate(self):
        """Test Rotation around a const cartesian coordinate"""
        self.program = get_test_program_rotate()
        self.program.load_to_robodk()
        self.program.simulate()
        # self.program.simulation_result.print()
        # self.program.simulation_result.add_to_robodk()
        self._test_for_valid_move_ids()
        self._test_for_playback_frame_errors()
        self._test_result_message()
        self._test_for_missing_move_ids()
        self._test_if_target_reached()
        self._test_if_cartesian_coordinates_const(2)

    def test_nearSingularity1(self):
        """Test Case Singularity with STEP_MM=1, STEP_DEG=1"""
        self.program = get_test_program_near_singularity()
        self.program.load_to_robodk()
        self.program.simulate()
        # self.program.simulation_result.print()
        # self.program.simulation_result.add_to_robodk()
        self._test_for_valid_move_ids()
        self._test_for_playback_frame_errors()
        self._test_result_message()
        self._test_for_missing_move_ids()

    def test_nearSingularity2(self):
        """Test Case Singularity with STEP_MM=10, STEP_DEG=10"""
        self.program = get_test_program_near_singularity()
        self.program.step_mm = 10
        self.program.step_deg = 10
        self.program.load_to_robodk()
        self.program.simulate()
        # self.program.simulation_result.print()
        # self.program.simulation_result.add_to_robodk()
        self._test_for_valid_move_ids()
        self._test_for_playback_frame_errors()
        self._test_result_message()
        self._test_for_missing_move_ids()


if __name__ == '__main__':
    unittest.main()
