# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# A robot is programmed given an SVG image to simulate a drawing application. An ABB IRB 4600-20/2.50 is used in this example.

from robolink import *  # API to communicate with RoboDK for simulation and offline/online programming
from robodk import *  # Robotics toolbox for industrial robots

import sys
import os
import re

#--------------------------------------------------------------------------------
# function definitions:


def point2D_2_pose(point, tangent):
    """Converts a 2D point to a 3D pose in the XY plane (4x4 homogeneous matrix)"""
    return transl(point.x, point.y, 0) * rotz(tangent.angle())


def svg_draw_quick(svg_img, board, pix_ref):
    """Quickly shows the image result without checking the robot movements."""
    RDK.Render(False)
    count = 0
    for path in svg_img:
        count = count + 1
        # use the pixel reference to set the path color, set pixel width and copy as a reference
        pix_ref.Recolor(path.fill_color)
        np = path.nPoints()
        print('drawing path %i/%i' % (count, len(svg_img)))
        for i in range(np):
            p_i = path.getPoint(i)
            v_i = path.getVector(i)
            pt_pose = point2D_2_pose(p_i, v_i)

            # add the pixel geometry to the drawing board object, at the calculated pixel pose
            board.AddGeometry(pix_ref, pt_pose)

    RDK.Render(True)


def svg_draw_robot(svg_img, board, pix_ref, item_frame, item_tool, robot):
    """Draws the image with the robot. It is slower that svg_draw_quick but it makes sure that the image can be drawn with the robot."""

    APPROACH = 100  # approach distance in MM for each path
    home_joints = [0, 0, 0, 0, 90, 0]  # home joints, in deg

    robot.setPoseFrame(item_frame)
    robot.setPoseTool(item_tool)
    robot.MoveJ(home_joints)

    # get the target orientation depending on the tool orientation at home position
    orient_frame2tool = invH(item_frame.Pose()) * robot.SolveFK(home_joints) * item_tool.Pose()
    orient_frame2tool[0:3, 3] = Mat([0, 0, 0])
    # alternative: orient_frame2tool = roty(pi)

    for path in svg_img:
        # use the pixel reference to set the path color, set pixel width and copy as a reference
        print('Drawing %s, RGB color = [%.3f,%.3f,%.3f]' % (path.idname, path.fill_color[0], path.fill_color[1], path.fill_color[2]))
        pix_ref.Recolor(path.fill_color)
        np = path.nPoints()

        # robot movement: approach to the first target
        p_0 = path.getPoint(0)
        target0 = transl(p_0.x, p_0.y, 0) * orient_frame2tool
        target0_app = target0 * transl(0, 0, -APPROACH)
        robot.MoveL(target0_app)
        RDK.RunMessage('Drawing %s' % path.idname)
        RDK.RunProgram('SetColorRGB(%.3f,%.3f,%.3f)' % (path.fill_color[0], path.fill_color[1], path.fill_color[2]))
        for i in range(np):
            p_i = path.getPoint(i)
            v_i = path.getVector(i)
            pt_pose = point2D_2_pose(p_i, v_i)

            # robot movement:
            target = transl(p_i.x, p_i.y, 0) * orient_frame2tool  #keep the tool orientation constant
            #target = pt_pose*orient_frame2tool #moving the tool along the path (axis 6 may reach its limits)
            robot.MoveL(target)

            # create a new pixel object with the calculated pixel pose
            board.AddGeometry(pix_ref, pt_pose)

        target_app = target * transl(0, 0, -APPROACH)
        robot.MoveL(target_app)

    robot.MoveL(home_joints)


#--------------------------------------------------------------------------------
# Program start
RDK = Robolink()

# locate and import the svgpy module
path_stationfile = RDK.getParam('PATH_OPENSTATION')
sys.path.append(os.path.abspath(path_stationfile))  # temporary add path to import station modules
from svgpy.svg import *

# select the file to draw
svgfile = path_stationfile + '/World map.svg'
#svgfile = path_stationfile + '/RoboDK text.svg'

# import the SVG file
svgdata = svg_load(svgfile)

IMAGE_SIZE = Point(1000, 2000)  # size of the image in MM
MM_X_PIXEL = 10  # in mm the path will be cut is depending on the pixel size
svgdata.calc_polygon_fit(IMAGE_SIZE, MM_X_PIXEL)
size_img = svgdata.size_poly()  # returns the size of the current polygon

# get the robot, frame and tool objects
robot = RDK.Item('ABB IRB 4600-20/2.50')
framedraw = RDK.Item('Frame draw')
tooldraw = RDK.Item('Tool')

# get the pixel reference to draw
pixel_ref = RDK.Item('pixel')

# delete previous image if any
image = RDK.Item('Board & image')
if image.Valid() and image.Type() == ITEM_TYPE_OBJECT:
    image.Delete()

# make a drawing board base on the object reference "Blackboard 250mm"
board_1m = RDK.Item('Blackboard 250mm')
board_1m.Copy()
board_draw = framedraw.Paste()
board_draw.setName('Board & image')
board_draw.Scale([size_img.x / 250, size_img.y / 250, 1])  # adjust the board size to the image size (scale)

# quickly show the final result without checking the robot movements:
#svg_draw_quick(svgdata, board_draw, pixel_ref)

# draw the image with the robot:
svg_draw_robot(svgdata, board_draw, pixel_ref, framedraw, tooldraw, robot)
