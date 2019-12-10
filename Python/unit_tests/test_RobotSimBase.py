import unittest
from path_simulation import *


class TestRobotSimBase(unittest.TestCase):
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
        reset_robodk_state()

    def tearDown(self):
        if self.rdk is not None:
            self.rdk.Disconnect()

    def _test_if_result_message_is_success(self):
        """Asserts that InstructionLitJoints result message is 'success'"""
        result = self.program.simulation_result
        self.assertEqual(result.message.lower(), "success",
                         f"Step {self.program.name} InstructionLitJoints result: {result.message}")

    def _test_for_missing_move_ids(self):
        """Asserts that there is at least one playback frame per step"""
        move_id = 0
        for s in self.program.steps:
            move_id += 1
            self.assertNotEqual(len(s.playback_frames), 0,
                                f"Step {s.name} has no playbackFrames. Move Id {move_id} is missing")

    def _test_for_valid_move_ids(self):
        """Asserts that all playback frames have a valid move id"""
        playback_frames = self.program.simulation_result.playback_frames
        max_move_id = len(self.program.steps)
        for index, pb_frame in enumerate(playback_frames):
            msg = f"Frame {index} has invalid move id {pb_frame.move_id}. Move id must be between 1 and {max_move_id}"
            self.assertGreaterEqual(pb_frame.move_id, 1, msg)
            self.assertLessEqual(pb_frame.move_id, max_move_id, msg)

    def _test_for_playback_frame_errors(self):
        """Asserts that all playback frames are without error"""
        steps = self.program.steps
        for s in steps:
            for index, pb_frame in enumerate(s.playback_frames):
                self.assertEqual(pb_frame.error, 0,
                                 f"Step {s.name} frame number {index} has a simulation error: {pb_frame.error_string}")

    def _test_if_stop_points_reached(self):
        """Asserts that for each frame move without blending the target is reached exactly"""
        for s in self.program.steps:
            if s.blending == 0 and s.move_type == MoveType.Frame:
                lastFrame = s.playback_frames[-1]
                expectedFramePose = get_frame_pose(s, lastFrame)
                delta = 1e-06
                msg = f"Step {s.name} is a stop point (frame move, blending 0). Exact target position should be reached"
                for index, value in enumerate(expectedFramePose):
                    self.assertAlmostEqual(s.pose[index], value, msg=msg, delta=delta)

    def _test_if_cartesian_coordinates_const(self, step_index):
        """Asserts that all playback frames of given step have same cartesian coorinates (x,y,z)"""
        steps = self.program.steps
        startStep = steps[step_index]
        playbackFrame = startStep.playback_frames[-1]
        refFramePose = get_frame_pose(startStep, playbackFrame)
        endStep = steps[step_index + 1]
        for index, playbackFrame in enumerate(endStep.playback_frames):
            framePose = get_frame_pose(endStep, playbackFrame)
            delta = 1e-06
            for i in range(3):
                msg = f"Step {endStep.name} playback frame {index},{i} has not the same position. refFrame{refFramePose[:3]}, step frame {framePose[:3]}"
                self.assertAlmostEqual(framePose[i], refFramePose[i], msg=msg, delta=delta)

    def _test_max_simulation_step(self):
        """Asserts that max simulation steps (mm, deg, time) ar not exceeded"""
        for step in self.program.steps:
            for index, pb_frame in enumerate(step.playback_frames):
                if self.program.simulation_type == InstructionListJointsFlags.TimeBased:
                    msg = f"Step {step.name} playback frame {index}, time_step {pb_frame.time_step} not in 'max_time_step' bounds"
                    self.assertLessEqual(pb_frame.time_step, self.program.max_time_step, msg)
                else:
                    if step.move_type == MoveType.Joint:
                        msg_deg = f"Step {step.name} (Joint) playback frame {index}, deg_step {pb_frame.deg_step} not in 'max_deg_step' bounds"
                        self.assertLessEqual(pb_frame.deg_step, self.program.max_deg_step, msg_deg)
                    else:
                        msg_mm = f"Step {step.name} (Frame )playback frame {index}, mm_step {pb_frame.mm_step} not in 'max_mm_step' bounds"
                        self.assertLessEqual(pb_frame.mm_step, self.program.max_mm_step, msg_mm)

    def _test_program(self, playback_frame_errors=True, result_success=True, verbose=False):
        """Loads and simulates program and then asserts various properties on result"""

        self.program.load_to_robodk()
        self.program.simulate()

        if verbose:
            self.program.print()
            self.program.simulation_result.add_to_robodk()

        self._test_max_simulation_step()
        self._test_for_valid_move_ids()
        self._test_for_missing_move_ids()
        self._test_if_stop_points_reached()

        if result_success:
            self._test_if_result_message_is_success()
        if playback_frame_errors:
            self._test_for_playback_frame_errors()
