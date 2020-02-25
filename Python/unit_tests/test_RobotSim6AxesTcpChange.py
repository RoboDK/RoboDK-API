from parameterized import parameterized, parameterized_class
from path_simulation import *
import test_RobotSimBase


def get_program_no_movement(blending):
    """Test program with two joint steps no movement in between"""
    j1 = [58, -70, 107, 64, -60, 43]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Joint, 0, j1, blending, 0, 0)
    ]
    return Program("No Move", steps)


def get_program_tcp_change(blending):
    j1 = [58, -70, 107, 64, -60, 43]
    f2 = [500, -600, 500, 0, 0, -90]
    f3 = [600, -600, 500, 0, 0, -90]
    f4 = [657, -596.5, 321.3, -90, 90, 90]
    f5 = [557, -596.5, 421.3, -90, 90, 90]
    steps = [
        # Step: name, move_type, tcp, pose, blending, speed, accel):
        Step("1", MoveType.Joint, 0, j1, blending, 0, 0),
        Step("2", MoveType.Frame, 0, f2, blending, 0, 0),
        Step("3", MoveType.Frame, 0, f3, blending, 0, 0),
        Step("4", MoveType.Frame, 1, f4, blending, 0, 0),
        Step("5", MoveType.Frame, 1, f5, blending, 0, 0)
    ]
    return Program("Tcp Change", steps)


@parameterized_class(
    ("test_name", "sim_type", "sim_step_mm", "sim_step_deg", "sim_step_time"), [
        (f"PosBased_{test_RobotSimBase.sim_step_mm_S:0.1f}mm_{test_RobotSimBase.sim_step_deg_S:0.1f}deg", InstructionListJointsFlags.Position, test_RobotSimBase.sim_step_mm_S, test_RobotSimBase.sim_step_deg_S, None),
        (f"PosBased_{test_RobotSimBase.sim_step_mm_L:0.1f}mm_{test_RobotSimBase.sim_step_deg_L:0.1f}deg", InstructionListJointsFlags.Position, test_RobotSimBase.sim_step_mm_L, test_RobotSimBase.sim_step_deg_L, None),
        (f"TimeBased_{test_RobotSimBase.step_time_S:0.4f}ms", InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_S),
        (f"TimeBased_{test_RobotSimBase.step_time_M:0.4f}ms", InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_M),
        (f"TimeBased_{test_RobotSimBase.step_time_L:0.4f}ms", InstructionListJointsFlags.TimeBased, None, None, test_RobotSimBase.step_time_L)
    ])
class TestRobotSim6Axes(test_RobotSimBase.TestRobotSimBase):

    def load_robot_cell(self):
        self.robot, self.tools = load_file(r"Robot_2TCP.rdk")

    def _test_tcps_in_different_positions(self):
        tool_list = self.rdk.ItemList(filter=ITEM_TYPE_TOOL)
        self.robot.setPoseTool(tool_list[0])
        p1 = self.robot.PoseTool()
        self.robot.setPoseTool(tool_list[1])
        p2 = self.robot.PoseTool()
        self.assertNotEqual(p1, p2, f"The two robot pose tools have the same offset => one must have changed")

    @parameterized.expand([
        ("NoBlending", -1),
        ("Blending", 10),
    ])
    def test_no_movement(self, _, blending):
        """Test program with no movement from step 1 to step 2"""
        self.program = get_program_no_movement(blending)
        self._test_program(verbose=False)

    @parameterized.expand([
        ("NoBlending", -1),
        ("Blending", 10),
    ])
    def test_tcp_change(self, _, blending):
        """Test program with one stop point"""
        self.program = get_program_tcp_change(blending)
        self._test_program(verbose=False)
        self._test_tcps_in_different_positions()


if __name__ == '__main__':
    unittest.main()
