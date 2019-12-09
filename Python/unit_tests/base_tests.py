import unittest
from path_simulation import *


class TestInstructionListJoints(unittest.TestCase):
    """Base test class for InstructionListJoints tests"""
    rdk = None
    robot = None
    tools = None
    program = None

    def load_robot_cell(self):
        raise NotImplementedError

    def setUp(self):
        self.rdk = init_robodk()
        self.load_robot_cell()
        clean_robodk()

    def tearDown(self):
        if self.rdk is not None:
            self.rdk.Disconnect()

    def _test_if_result_message_is_success(self):
        """Test if return message of InstructionListJoints() is 'success' """
        result = self.program.simulation_result
        self.assertEqual(result.message.lower(), "success",
                         f"Step {self.program.name} InstructionJointList result: {result.message}")

    def _test_for_missing_move_ids(self):
        """For each Step we should have at least one playback frame"""
        move_id = 0
        for s in self.program.steps:
            move_id += 1
            self.assertNotEqual(len(s.playback_frames), 0,
                                f"Step {s.name} has no playbackFrames. Move Id {move_id} is missing")

    def _test_for_valid_move_ids(self):
        """Each Frame must have a valid move id > 0"""
        playback_frames = self.program.simulation_result.playback_frames
        max_move_id = len(self.program.steps)
        for index, pb_frame in enumerate(playback_frames):
            msg = f"Frame {index} has invalid move id {pb_frame.move_id}. Move id must be between 1 and {max_move_id}"
            self.assertGreaterEqual(pb_frame.move_id, 1, msg)
            self.assertLessEqual(pb_frame.move_id, max_move_id, msg)

    def _test_for_playback_frame_errors(self):
        """Check all playback frames for each step for errors"""
        steps = self.program.steps
        for s in steps:
            for index, pb_frame in enumerate(s.playback_frames):
                self.assertEqual(pb_frame.error, 0,
                                 f"Step {s.name} frame number {index} has a simulation error: {pb_frame.error_string}")

    def _test_if_target_reached(self):
        for s in self.program.steps:
            if s.blending == 0:
                lastFrame = s.playback_frames[-1]
                expectedFramePose = get_frame_pose(s, lastFrame)
                delta = 1e-06
                msg = f"Step {s.name} is a stop point. Exact target position should be reached"
                if s.move_type == MoveType.Frame:
                    for index, value in enumerate(expectedFramePose):
                        self.assertAlmostEqual(s.pose[index], value, msg=msg, delta=delta)

    def _test_if_cartesian_coordinates_const(self, stepindex):
        steps = self.program.steps
        startStep = steps[stepindex]
        playbackFrame = startStep.playback_frames[-1]
        refFramePose = get_frame_pose(startStep, playbackFrame)
        endStep = steps[stepindex + 1]
        for index, playbackFrame in enumerate(endStep.playback_frames):
            framePose = get_frame_pose(endStep, playbackFrame)
            delta = 1e-06
            for i in range(3):
                msg = f"step {endStep.name} playback frame {index},{i} has not the same position. refFrame{refFramePose[:3]}, step frame {framePose[:3]}"
                self.assertAlmostEqual(framePose[i], refFramePose[i], msg=msg, delta=delta)

    def _test_program(self,
                      valid_move_ids=True, missing_move_ids=True,
                      target_reached=True, playback_frame_errors=True, result_success=True,
                      verbose=False):
        self.program.load_to_robodk()
        self.program.simulate()

        if verbose:
            self.program.print()
            # self.program.simulation_result.print()
            self.program.simulation_result.add_to_robodk()

        if result_success:
            self._test_if_result_message_is_success()
        if playback_frame_errors:
            self._test_for_playback_frame_errors()
        if valid_move_ids:
            self._test_for_valid_move_ids()
        if missing_move_ids:
            self._test_for_missing_move_ids()
        if target_reached:
            self._test_if_target_reached()
