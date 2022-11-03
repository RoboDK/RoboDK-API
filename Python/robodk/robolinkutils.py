# Copyright 2015-2022 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# --------------------------------------------
# --------------- DESCRIPTION ----------------
# This file defines general utility functions for Robolink and Items.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# --------------------------------------------

from robodk import robolink, robomath


def getLinks(item, type_linked=robolink.ITEM_TYPE_ROBOT):
    """
    Get all the items of a specific type for which getLink() returns the specified item.

    :param item: The source Item
    :type item: :class:`.Item`
    :param int type_linked: type of items to check for a link. None means any type.

    :return: A list of Items for which item.getLink return the specified item
    :rtype: list of :class:`.Item`
    """
    item_type = item.Type()
    links = []
    for candidate in item.RDK().ItemList(type_linked):
        if candidate == item:
            continue

        link = candidate.getLink(type_linked=item_type)
        if link.Valid() and link == item:
            links.append(candidate)
    return links


def getAncestors(item, parent_types=None):
    """
    Get the list of parents of an Item up to the Station, with type filtering (i.e. [ITEM_TYPE_FRAME, ITEM_TYPE_ROBOT, ..]).
    By default, it will return all parents of an Item with no regard to their type, ordered from the Item's parent to the Station.

    :param item: The source Item
    :type item: :class:`.Item`
    :param parent_types: The parent allowed types, such as ITEM_TYPE_FRAME, defaults to None
    :type parent_types: list of ITEM_TYPE_*, optional

    :return: A list of parents, ordered from the Item's parent to the Station.
    :rtype: list of :class:`.Item`
    """

    if parent_types and type(parent_types) is not list:
        parent_types = [parent_types]

    parent = item
    parents = []
    while (parent is not None and parent.Type() not in [robolink.ITEM_TYPE_STATION, -1]):
        parent = parent.Parent()

        if parent_types is None:
            parents.append(parent)
            continue

        for parent_type in parent_types:
            if parent.Type() == parent_type:
                parents.append(parent)
                break

    return parents


def getLowestCommonAncestor(item1, item2):
    """
    Finds the lowest common ancestor (LCA) between two Items in the Station's tree.

    :param item1: The first Item
    :type item1: :class:`.Item`
    :param item2: The second Item
    :type item2: :class:`.Item`

    :return: The lowest common ancestor (LCA)
    :rtype: :class:`.Item`
    """

    # Make an ordered list of parents. Iter on it until the parent differs.. and you get the lowest common ancestor (LCA)
    parents1 = getAncestors(item1)
    parents2 = getAncestors(item2)

    lca = None
    size = min(len(parents1), len(parents2))
    for i in range(size):
        if parents1[-1] != parents2[-1]:
            break

        lca = parents1[-1]
        parents1.pop()
        parents2.pop()

    return lca


def getAncestorPose(item_child, item_parent):
    """
    Gets the pose between two Items that have a hierarchical relationship in the Station's tree.
    There can be N Items between the two.
    This function will throw an error for synchronized axis.

    :param item_child: The child Item
    :type item_child: :class:`.Item`
    :param item_parent: The parent Item
    :type item_parent: :class:`.Item`

    :return: The pose from the child to the parent
    :rtype: :class:`robomath.Mat`
    """

    if item_child == item_parent:
        return robomath.eye(4)

    parents = getAncestors(item_child)
    if item_parent not in parents:
        return None

    items = [item_child] + parents
    idx = items.index(item_parent)
    poses = []
    for i in range(idx - 1, -1, -1):
        if items[i].Type() in [robolink.ITEM_TYPE_TOOL]:
            poses.append(items[i].PoseTool())

        elif items[i].Type() in [robolink.ITEM_TYPE_ROBOT]:
            if items[i].getLink(robolink.ITEM_TYPE_ROBOT) != items[i]:
                continue

            axes_links = getLinks(items[i], robolink.ITEM_TYPE_ROBOT_AXES)
            if axes_links:
                raise robolink.InputError("This function does not support synchronized axis")

            joints = items[i].Joints().list()
            poses.append(items[i].SolveFK(joints))

        else:
            poses.append(items[i].Pose())

    pose_wrt = robomath.eye(4)
    for pose in poses:  # this format is to ease debugging
        pose_wrt *= pose
    return pose_wrt


def getPoseWrt(item1, item2):
    """
    Gets the pose of an Item (item1) with respect to an another Item (item2).

    .. code-block:: python

        child.PoseWrt(child.Parent())  # will return a forward pose from the parent to the child
        child.Parent().PoseWrt(child)  # will return an inverse pose from the child to the parent
        tool.PoseWrt(tool.Parent())  # will return the PoseTool() of the tool
        tool.PoseWrt(station)  # will return the absolute pose of the tool

    :param item1: The source Item
    :type item1: :class:`robolink.Item`
    :param item2: The second Item
    :type item2: :class:`robolink.Item`

    :return: The pose from the source Item to the second Item
    :rtype: :class:`robomath.Mat`
    """

    if item1 == item2:
        return robomath.eye(4)

    parents1 = getAncestors(item1)
    if item2 in parents1:
        return getAncestorPose(item1, item2)

    parents2 = getAncestors(item2)
    if item1 in parents2:
        return getAncestorPose(item2, item1).inv()

    lca = getLowestCommonAncestor(item1, item2)
    pose1 = getAncestorPose(item1, lca)
    pose2 = getAncestorPose(item2, lca)

    return pose2.inv() * pose1


def setPoseAbsIK(item, pose_abs):
    """
    Set the pose of the item with respect to the absolute reference frame, accounting for inverse kinematics.
    For instance, you can set the absolute pose of a ITEM_TYPE_TOOL directly without accounting for the robot kinematics.
    This function will throw an error for synchronized axis.

    .. code-block:: python

        tool_item.setPoseAbs(eye(4))  # will SET the tool center point with respect to the station at [0,0,0,0,0,0]
        setPoseAbsIK(tool_item, eye(4))  # will MOVE the robot so that the tool center point with regard to the station is [0,0,0,0,0,0]

    :param item: The source Item
    :type item: :class:`robolink.Item`
    :param pose_abs: pose of the item with respect to the station reference
    :type pose_abs: :class:`robomath.Mat`
    """
    if item.Type() == robolink.ITEM_TYPE_STATION:
        return

    parents = getAncestors(item)
    if len(parents) == 1:
        item.setPose(pose_abs)
        return

    if item.Type() in [robolink.ITEM_TYPE_TOOL]:
        # Tool Item is not necessarily the active tool
        pose_abs = pose_abs * item.PoseTool().inv() * item.Parent().PoseTool()
        item = item.Parent()
        parents.pop(0)

    parent_pose_abs = getAncestorPose(parents[0], item.RDK().ActiveStation())
    pose = parent_pose_abs.inv() * pose_abs

    if item.Type() == robolink.ITEM_TYPE_ROBOT:
        joints = item.SolveIK(pose, tool=item.PoseTool()).list()
        if len(joints) != len(item.Joints().list()):
            raise robolink.TargetReachError("No solution found for the desired pose.")
        item.setJoints(joints)
    else:
        item.setPose(pose)


def SolveIK_Conf(robot, pose, toolpose=None, framepose=None, joint_config=[0, 1, 0]):
    """Calculates the inverse kinematics for the specified robot and pose. The function returns only the preferred solutions from the joint configuration as a 2D matrix.
    Returns a list of joints as a 2D matrix [N x M], where N is the number of degrees of freedom (robot joints) and M is the number of solutions. For some 6-axis robots, SolveIK returns 2 additional values that can be ignored.

    :param robot: The robot Item
    :type robot: :class:`robolink.Item`
    :param pose: pose of the robot flange with respect to the robot base frame
    :type pose: :class:`~robodk.robomath.Mat`
    :param toolpose: Tool pose with respect to the robot flange (TCP)
    :type toolpose: :class:`~robodk.robomath.Mat`
    :param framepose: Reference pose (reference frame with respect to the robot base)
    :type framepose: :class:`~robodk.robomath.Mat`
    :param joint_config: desired joint configuration, as [Front(0)/Rear(1)/Any(-1), Elbow Up(0)/Elbow Down(1)/Any(-1), Non-flip(0)/Flip(1)/Any(-1)]
    :type joint_config: list of int
    """

    desired_rear, desired_lower, desired_flip = joint_config
    joint_solutions = []

    for joint_solution in robot.SolveIK_All(pose, toolpose, framepose):
        rear, lower, flip = [int(x) for x in robot.JointsConfig(joint_solution).list()[:3]]
        if desired_rear < 0 or rear == desired_rear:
            if desired_lower < 0 or lower == desired_lower:
                if desired_flip < 0 or flip == desired_flip:
                    joint_solutions.append(joint_solution)

    return joint_solutions


if __name__ == "__main__":
    pass