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

    :param item_child: The child Item
    :type item_child: :class:`.Item`
    :param item_parent: The parent Item
    :type item_parent: :class:`.Item`

    :return: The pose from the child to the parent
    :rtype: :class:`robomath.Mat`
    """

    parents = getAncestors(item_child)
    if item_parent not in parents:
        return None

    pose = item_parent.Pose()
    for parent in reversed(parents):
        pose *= parent.Pose()
    pose *= item_child.Pose()

    return pose


def getPoseWrt(item1, item2):
    """Gets the pose of an Item (item1) with respect to an another Item (item2).

    :param item1: The source Item
    :type item1: :class:`robolink.Item`
    :param item2: The second Item
    :type item2: :class:`robolink.Item`

    :return: The pose from the source Item to the second Item
    :rtype: :class:`robomath.Mat`
    """

    parents1 = getAncestors(item1)
    if item2 in parents1:
        return getAncestorPose(item1, item2)

    parents2 = getAncestors(item2)
    if item1 in parents2:
        return getAncestorPose(item2, item1)

    lca = getLowestCommonAncestor(item1, item2)
    pose1 = getAncestorPose(item1, lca)
    pose2 = getAncestorPose(item2, lca)

    return pose2.inv() * pose1
