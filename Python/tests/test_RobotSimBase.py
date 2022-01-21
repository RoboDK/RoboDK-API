import unittest
from path_simulation import *


# Simulation Time for Time Based Simulation Tests
step_time_S = 0.002
step_time_M = 0.02
step_time_RM = 0.05 #0.05  # Simuation Time used in RobotManager
#step_time_L = 0.2 # triggers the default 25 deg limit for kinematic error when we are close to a singularity
step_time_L = 0.025


# Simulation Step Size in mm and deg for Position Based Simulation Tests
sim_step_mm_S = 1
sim_step_deg_S = 1
sim_step_mm_L = 10
sim_step_deg_L = 10

# Maximum calculation time in seconds
max_calc_time = 2

# Define the maximum expected playback frames per instruction
max_frames_instruction = 1250

# Replacement character for a simple dot "." used for parameterized tests
# This is needed for proper test discovery and execution in vscode
# nose2 (out unit test html report tool) can not deal with unicode character \u2024:
# UnicodeEncodeError: 'charmap' codec can't encode character '\u2024' in position 3871: character maps to <undefined>
# for the time being we use "_"
dot_repr = "_"   # "\u2024" does not work with nose 2 (see comment above)



class TestRobotSimBase(unittest.TestCase):
    """Base test class for InstructionListJoints tests"""
    rdk = None
    robot = None
    tools = None
    program = None
    calc_time = None

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

    def _test_calc_time(self):
        """Check if InstructionListJoints takes a reasonable amount of time to calculate"""
        msg = f"Unexpected calculation time: {self.calc_time} s"
        self.assertLessEqual(self.calc_time, max_calc_time, msg)

    def _test_frames_per_instruction(self):
        """Check if each instruction gets a reasonable amount of frames"""
        for step in self.program.steps:
            nframes = len(step.playback_frames)
            msg = f"Step {step.name} has too many playback frames: {nframes}"
            self.assertLessEqual(nframes, max_frames_instruction, msg)

    def _test_result_message(self):
        """Asserts that If number of errors == 0 then result message must be success"""
        numberOfErrors = 0
        for step in self.program.steps:
            for frame in step.playback_frames:
                if frame.error > 0:
                    numberOfErrors = numberOfErrors + 1
        errorMessage = self.program.simulation_result.message.lower()

        if numberOfErrors == 0:
            msg = f"Found no simulation errors. Expected error message 'success' but got error message: {errorMessage}"
            self.assertEqual( "success", errorMessage, msg)

        if numberOfErrors > 0:
            msg = f"{numberOfErrors} Simulation errors found. Expected error message != 'success'"
            self.assertNotEqual( "success", errorMessage, msg)

        msg = f"Expected only 1 error code but got {numberOfErrors} errors"
        self.assertLessEqual( numberOfErrors, 1, msg)

    def _test_result_for_expected_path_error_flags(self):
        numberOfErrors = 0
        for step in self.program.steps:
            expectedErrorFlags = step.expected_error_flags
            if numberOfErrors == 0:
                msg = f"Unexpected empty playback frame list in Step {step.name}"
                self.assertGreater( len(step.playback_frames), 0, msg)
                lastFrame = step.playback_frames[-1]
                simulatedErrorFlags = ConvertErrorCodeToJointErrorType(lastFrame.error)
                msg = f"Step {step.name} Invalid error result. expectedErrorFlags:{str(expectedErrorFlags)}, actual simulation error:{str(simulatedErrorFlags)}"
                self.assertEqual(expectedErrorFlags, simulatedErrorFlags, msg)
            if expectedErrorFlags != PathErrorFlags.NoError:
                numberOfErrors = numberOfErrors + 1
                errorMessage = self.program.simulation_result.message.lower()
                self.assertNotEqual( errorMessage, "success", "expected an error message but got 'success'")

        if numberOfErrors == 0:
            errorMessage = self.program.simulation_result.message.lower()
            msg = f"expected error message 'success' but got error message {errorMessage}"
            self.assertEqual( errorMessage, "success", msg)

    def _test_for_missing_move_ids(self):
        """Asserts that there is at least one playback frame per step"""
        move_id = 0
        numberOfErrors = 0
        for s in self.program.steps:
            expectedErrorFlags = s.expected_error_flags
            if expectedErrorFlags != PathErrorFlags.NoError:
               numberOfErrors = numberOfErrors + 1
            if numberOfErrors == 0:
                move_id += 1
                msg = f"Step {s.name} has no playbackFrames. Move Id {move_id} is missing"
                self.assertNotEqual(len(s.playback_frames), 0, msg)

    def _test_for_playback_frames_with_time_step0(self):
        """Asserts that there is no playback frame with time_step 0 in the middle of a move from A to B. Only the last playback frame can have a value of 0 if it is a stop point.
        """
        if self.program.simulation_type != InstructionListJointsFlags.TimeBased:
            return
        for s in self.program.steps:
            playbackFrameWithTimeStep0 = None
            frameNumber = 0
            for f in s.playback_frames:
                frameNumber = frameNumber + 1
                if playbackFrameWithTimeStep0 != None:
                    msg = f"Step {s.name} playbackFrame {frameNumber-1} with moveId {f.move_id} has time_step value 0. playbackFrame {frameNumber} has time_step value {f.time_step} in the middle of the move from {f.move_id-1} to {f.move_id}. "
                    self.fail(msg)
                if f.time_step == 0 and f.error != 0.0:
                    playbackFrameWithTimeStep0 = f
            
    def _test_for_duplicate_frames_for_first_step(self):
        """Asserts there is only one playback frame for the first target"""
        firstStep = self.program.steps[0]
        msg = f"First Step {firstStep.name} has more then one playbackFrame. Move Id 1. number of PlaybackFrames: {len(firstStep.playback_frames)}"
        self.assertEqual(len(firstStep.playback_frames), 1, msg)
            
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
                if len(s.playback_frames) > 0:
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
        numerical_tolerance = 1e-6
        for step in self.program.steps:
            for index, pb_frame in enumerate(step.playback_frames):
                if self.program.simulation_type >= InstructionListJointsFlags.TimeBased:
                    msg = f"Step {step.name} playback frame {index}, time_step {pb_frame.time_step} not within 'max_time_step' bounds"
                    self.assertLessEqual(pb_frame.time_step, self.program.max_time_step + numerical_tolerance, msg)
                else:
                    #move_type = step.move_type if index != 0 else previous_step.move_type
                    move_type = step.move_type # Fix by Albert
                    # deg step applies to joint moves
                    if move_type == MoveType.Joint:
                        msg_deg = f"Step {step.name} (Joint) playback frame {index}, deg_step {pb_frame.deg_step} not within 'max_deg_step' bounds"

                        # Check if value given in list result is smaller than max for simulation
                        self.assertLessEqual(pb_frame.deg_step, self.program.max_deg_step, msg_deg)

                        # Check if actual step is smaller than max for simulation
                        actual_deg_step = max([abs(j_a[0] - j_b[0]) for j_a, j_b
                                               in zip(pb_frame.joints.rows, previous_pb_frame.joints.rows)])
                        self.assertLessEqual(actual_deg_step, self.program.max_deg_step + numerical_tolerance, msg_deg)
                    else:
                        msg_mm = f"Step {step.name} (Frame) playback frame {index}, mm_step {pb_frame.mm_step} not within 'max_mm_step' bounds"

                        # Check if value given in list result is smaller than max for simulation
                        self.assertLessEqual(pb_frame.mm_step, self.program.max_mm_step, msg_mm)

                        # Check if actual step is smaller than max for simulation
                        actual_mm_step = sqrt(sum([(c_a[0] - c_b[0]) * (c_a[0] - c_b[0])
                                                   for c_a, c_b in zip(pb_frame.coords.rows, previous_pb_frame.coords.rows)]))
                        self.assertLessEqual(actual_mm_step, self.program.max_mm_step + numerical_tolerance, msg_mm)

                previous_pb_frame = pb_frame
            previous_step = step

    def _test_program(self, verbose=False):
        """Loads and simulates program and then asserts various properties on result

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
        self.calc_time = self.program.calc_time

        if verbose:
            self.program.print()
            self.program.simulation_result.add_to_robodk()

        self._test_for_valid_move_ids()
        self._test_result_message()
        self._test_result_for_expected_path_error_flags()
        self._test_calc_time()
        self._test_frames_per_instruction()
        self._test_for_missing_move_ids()
        self._test_max_simulation_step()
        self._test_if_stop_points_reached()
        self._test_for_duplicate_frames_for_first_step()
        self._test_for_playback_frames_with_time_step0()

if __name__ == '__main__':
    import unittest
    unittest.main()
