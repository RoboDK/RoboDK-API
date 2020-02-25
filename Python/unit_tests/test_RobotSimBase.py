import unittest
from path_simulation import *


# Simulation Time for Time Based Simulation Tests
step_time_S = 0.002
step_time_M = 0.02
step_time_L = 0.2


# Simulation Step Size in mm and deg for Position Based Simulation Tests
sim_step_mm_S = 1
sim_step_deg_S = 1
sim_step_mm_L = 10
sim_step_deg_L = 10

# Replacement character for a simple dot "." used for parameterized tests
# This is needed for proper test discovery and execution in vscode
dot_repr = "\u2024"


class TestRobotSimBase(unittest.TestCase):
    """Base test class for InstructionListJoints tests"""
    rdk = None
    robot = None
    tools = None
    program = None

    sim_type = None
    sim_step_mm = None
    sim_step_deg = None
    sim_step_time = None

    def load_robot_cell(self):
        raise NotImplementedError

    def setUp(self):
        self.rdk = init_robodk()
        self.load_robot_cell()
        reset_robodk_state()

    def tearDown(self):
        if self.rdk is not None:
            self.rdk.Disconnect()

    def _test_result_message(self, expect_error=False):
        """Asserts that InstructionListJoints result message is as expected

        :param bool expect_error: Set 'True' if simulation error is expected
        """
        result = self.program.simulation_result
        result_has_error = result.message.lower() != "success"
        msg = f"InstructionListJoints result message: '{result.message}' (but expect_error={expect_error})"
        self.assertEqual(result_has_error, expect_error, msg)

    def _test_for_missing_move_ids(self):
        """Asserts that there is at least one playback frame per step"""
        move_id = 0
        for s in self.program.steps:
            move_id += 1
            msg = f"Step {s.name} has no playbackFrames. Move Id {move_id} is missing"
            self.assertNotEqual(len(s.playback_frames), 0, msg)

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
                msg = f"Step {s.name} frame number {index} has a simulation error: {pb_frame.error_string}"
                self.assertEqual(pb_frame.error, 0, msg)

    def _test_if_stop_points_reached(self):
        """Asserts that for each frame move without blending the target is reached exactly"""
        for s in self.program.steps:
            if s.blending == 0 and s.move_type == MoveType.Frame:
                lastFrame = s.playback_frames[-1]
                expectedFramePose = get_frame_pose(s, lastFrame)
                delta = 0.0011  # one micron is used in RoboDK as tolerance when time based sequence is used
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
            delta = 1e-05
            for i in range(3):
                msg = f"Step {endStep.name} playback frame {index},{i} has not the same position. refFrame{refFramePose[:3]}, step frame {framePose[:3]}"
                self.assertAlmostEqual(framePose[i], refFramePose[i], msg=msg, delta=delta)

    def _test_max_simulation_step(self):
        """Asserts that max simulation steps (mm, deg, time) ar not exceeded"""
        previous_step = self.program.steps[0]
        previous_pb_frame = self.program.steps[0].playback_frames[0]
        for step in self.program.steps:
            for index, pb_frame in enumerate(step.playback_frames):
                if self.program.simulation_type >= InstructionListJointsFlags.TimeBased:
                    msg = f"Step {step.name} playback frame {index}, time_step {pb_frame.time_step} not in 'max_time_step' bounds"
                    self.assertLessEqual(pb_frame.time_step, self.program.max_time_step, msg)
                else:
                    move_type = step.move_type if index != 0 else previous_step.move_type
                    # deg step applies to joint moves
                    if move_type == MoveType.Joint:
                        msg_deg = f"Step {step.name} (Joint) playback frame {index}, deg_step {pb_frame.deg_step} not in 'max_deg_step' bounds"

                        # Check if value given in list result is smaller than max for simulation
                        self.assertLessEqual(pb_frame.deg_step, self.program.max_deg_step, msg_deg)

                        # Check if actual step is smaller than max for simulation
                        actual_deg_step = max([abs(j_a[0] - j_b[0]) for j_a, j_b
                                               in zip(pb_frame.joints.rows, previous_pb_frame.joints.rows)])
                        self.assertLessEqual(actual_deg_step, self.program.max_deg_step, msg_deg)
                    else:
                        msg_mm = f"Step {step.name} (Frame )playback frame {index}, mm_step {pb_frame.mm_step} not in 'max_mm_step' bounds"

                        # Check if value given in list result is smaller than max for simulation
                        self.assertLessEqual(pb_frame.mm_step, self.program.max_mm_step, msg_mm)

                        # Check if actual step is smaller than max for simulation
                        actual_mm_step = sqrt(sum([(c_a[0] - c_b[0]) * (c_a[0] - c_b[0])
                                                   for c_a, c_b in zip(pb_frame.coords.rows, previous_pb_frame.coords.rows)]))
                        self.assertLessEqual(actual_mm_step, self.program.max_mm_step, msg_mm)

                previous_pb_frame = pb_frame
            previous_step = step

    def _test_program(self, expect_error=False, verbose=False):
        """Loads and simulates program and then asserts various properties on result

        :param bool expect_error:
            Set 'True' if simulation error is expected, will only check for result message.
            If set to false addidional checks on the simulation result will be executed.
        :param bool verbose:
            Print details of simulation result and load it to RoboDK
        """

        # set testing parameters
        if self.sim_type is InstructionListJointsFlags.Position:
            self.program.simulation_type = self.sim_type
            self.program.max_mm_step = self.sim_step_mm
            self.program.max_deg_step = self.sim_step_deg
        elif self.sim_type is InstructionListJointsFlags.TimeBased:
            self.program.simulation_type = self.sim_type
            self.program.max_time_step = self.sim_step_time
        elif self.sim_type is None:
            raise ValueError("No 'sim_type' provided")

        self.program.load_to_robodk()
        self.program.simulate()

        if verbose:
            self.program.print()
            self.program.simulation_result.add_to_robodk()

        self._test_result_message(expect_error)

        if expect_error:
            # other checks don't make sense if program simulation has errors
            return

        # perform checks on simulation result
        self._test_for_playback_frame_errors()
        self._test_for_missing_move_ids()
        self._test_for_valid_move_ids()
        self._test_max_simulation_step()
        self._test_if_stop_points_reached()
