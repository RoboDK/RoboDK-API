% Copyright (c) 2015, RoboDK Inc.
% All rights reserved.
% 
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are met:
% 
% * Redistributions of source code must retain the above copyright notice, this
%   list of conditions and the following disclaimer.
% 
% * Redistributions in binary form must reproduce the above copyright notice,
%   this list of conditions and the following disclaimer in the documentation
%   and/or other materials provided with the distribution
% 
% * Neither the name of RoboDK Inc. nor the names of its
%   contributors may be used to endorse or promote products derived from this
%   software without specific prior written permission.
% 
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
% AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
% IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
% DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
% FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
% DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
% SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
% CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
% OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
% OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
%
% --------------------------------------------
% --------------- DESCRIPTION ----------------
% This file defines the following class:
%     RobolinkItem()  (or Item() as used in the Python version of the API)
%
% These classes are the objects used to interact with RoboDK and create macros.
% An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
% Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method)
%
% More information about the RoboDK API for Python here:
%     https://robodk.com/doc/en/RoboDK-API.html
%     https://robodk.com/doc/en/PythonAPI/index.html
%
% --------------------------------------------

classdef RobolinkItem < handle
    % The Item class represents an item in RoboDK station.
    % An item can be a robot, a frame, a tool, an object, a target, ... (any item visible in the station tree)
    % An item can also be seen as a node where other items can be attached to (child items).
    % Items (RobolinkItem) are created by certain functions calls from Robolink class.
    % Every item has one parent item/node and can have one or more child items/nodes.
    %
    % RoboDK api Help:
    % ->Type "doc Robolink"            for more help on the Robolink class
    % ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
    % ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes
    properties (Constant)

        % See Robolink.m for constants

    end

    properties
        item = 0; % This value should not be modified. It stores the object pointer
        link = 0; % This value should not be modified. It stores the connection pointer
        type = 0; % This value should not be modified. It stores the type of the item
    end

    methods

        function this = RobolinkItem(rl, ptr_item, itemtype)
            % Creates an item object from the Robolink() connection and an
            % item number
            if nargin < 2
                ptr_item = 0;
            end

            if nargin < 3
                itemtype = -1;
            end

            this.item = ptr_item;
            this.link = rl;
            this.type = itemtype;
        end

        function rdk = RDK(this)
            % Get the pointer to RoboDK instance
            rdk = this.link;
        end

        function type = Type(this)
            % Returns an integer that represents the type of the item (robot, object, tool, frame, ...)
            this.link.check_connection();
            command = 'G_Item_Type';
            this.link.send_line(command);
            this.link.send_item(this);
            type = this.link.rec_int();
            this.link.check_status();
        end

        function Copy(this)
            % Copy the item to the clipboard (same as Ctrl+C). Use together with Paste() to duplicate items.
            this.link.Copy(this);
        end

        function newitem = Paste(this)
            % Paste the item from the clipboard as a child of this item (same as Ctrl+V)
            % Out 1: item -> new item pasted (created)
            newitem = this.link.Paste(this.item);
        end

        function newitem = AddFile(this, filename)
            % Adds an object attached to this object
            newitem = this.link.AddFile(filename, this.item);
        end

        function Save(this, filename)
            % Save a station or object to a file
            this.link.Save(filename, this.item)
        end

        function collision = Collision(this, item_check)
            % Returns True if this item is in a collision state with another :class:`.Item`, otherwise it returns False.
            collision = this.link.Collision(this.item, item_check);
        end

        function is_inside = IsInside(this, object)
            % Return True if the object is inside the provided object
            is_inside = this.link.IsInside(this.item, object);
        end

        function AddGeometry(this, fromitem, pose)
            % Makes a copy of the geometry fromitem adding it at a given position (pose) relative to this item.
            this.link.check_connection();
            command = 'CopyFaces';
            this.link.send_line(command);
            this.link.send_item(fromitem);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end

        function Delete(this)
            % Deletes an item in the station.
            this.link.check_connection();
            command = 'Remove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end

        function valid = Valid(this, check_deleted)
            % Checks if the item is valid.
            % Returns True if the item is valid or False if the item is not valid.
            % An invalid item will be returned by an unsuccessful function call (wrong name or because an item was deleted)
            if nargin < 2
                check_deleted = 0;
            end

            valid = (this.item ~= 0);

            if check_deleted
                valid = this.Type() >= 0;
            end

        end

        function setParent(this, parent)
            % Moves the item to another location (parent)
            % In 1  : parent -> parent to attach the item
            this.link.check_connection();
            command = 'S_Parent';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);
            this.link.check_status();
        end

        function setParentStatic(this, parent)
            % Moves the item to another location (parent) without changing the current position in the station
            % In 1  : parent -> parent to attach the item
            this.link.check_connection();
            command = 'S_Parent_Static';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);
            this.link.check_status();
        end

        function item_attached = AttachClosest(this)
            % Attaches the closest object to the provided tool.
            % Out  : item -> returns the item that was attached (0 if none found)
            this.link.check_connection();
            command = 'Attach_Closest';
            this.link.send_line(command);
            this.link.send_item(this);
            item_attached = this.link.rec_item();
            this.link.check_status();
        end

        function item_detached = DetachClosest(this, parent)
            % Detaches the closest object attached to the tool (see also: Set_Parent_Static).
            % In  1 : item (optional) -> parent to leave the objects
            if nargin < 2
                parent = 0;
            end

            this.link.check_connection();
            command = 'Detach_Closest';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);
            item_detached = this.link.rec_item();
            this.link.check_status();
        end

        function DetachAll(this, parent)
            % Detaches any object attached to a tool (see also: Set_Parent_Static).
            % In  1 : item (optional) -> parent to leave the objects
            if nargin < 2
                parent = RobolinkItem(this.link);
            end

            this.link.check_connection();
            command = 'Detach_All';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(parent);
            this.link.check_status();
        end

        function parent = Parent(this)
            % Returns the parent item of the provided item.
            % Out : parent -> parent of the item
            this.link.check_connection();
            command = 'G_Parent';
            this.link.send_line(command);
            this.link.send_item(this);
            parent = this.link.rec_item();
            this.link.check_status();
        end

        function itemlist = Childs(this)
            % Returns a list of the item childs that are attached to the provided item.
            % Out  : child x n -> list of child item pointers
            this.link.check_connection();
            command = 'G_Childs';
            this.link.send_line(command);
            this.link.send_item(this);
            nitems = this.link.rec_int();
            itemlist = cell(nitems, 1);

            for i = 1:nitems
                itemlist{i} = this.link.rec_item();
            end

            this.link.check_status();
        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function visible = Visible(this)
            % Returns 1 if the item is visible, otherwise, returns 0.
            % Out : int -> visible (1) or not visible (0)
            this.link.check_connection();
            command = 'G_Visible';
            this.link.send_line(command);
            this.link.send_item(this);
            visible = this.link.rec_int();
            this.link.check_status();
        end

        function setVisible(this, visible, visible_frame)
            % Sets the item visiblity
            % In 2 : int -> set visible (1) or not visible (0)
            % In 3 : int (optional) -> set visible frame (True or 1) or not visible (False or 0)
            if nargin < 3
                visible_frame = visible;
            end

            this.link.check_connection();
            command = 'S_Visible';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(visible);
            this.link.send_int(visible_frame);
            this.link.check_status();
        end

        function name = Name(this)
            % Gets the name of an item.
            % Out : name (string)
            this.link.check_connection();
            command = 'G_Name';
            this.link.send_line(command);
            this.link.send_item(this);
            name = this.link.rec_line();
            this.link.check_status();
        end

        function setName(this, name)
            % Sets the name of an item.
            % In 1 : name (string)
            this.link.check_connection();
            command = 'S_Name';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(name);
            this.link.check_status();
        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function setValue(this, varname, value)
            % Set a specific variable name to a given value. This is reserved for internal purposes and future compatibility.
            % In 1 : variable name
            % In 2 : variable value
            this.link.check_connection();

            if isa(value, 'double')
                command = 'S_Gen_Mat';
                this.link.send_line(command);
                this.link.send_item(this);
                this.link.send_line(varname);
                this.link.send_matrix(value);
            else
                command = 'S_Gen_Str';
                this.link.send_line(command);
                this.link.send_item(this);
                this.link.send_line(varname);
                this.link.send_line(value);
            end

            this.link.check_status();
        end

        function setPose(this, pose)
            % Sets the local position (pose) of an item. For example, the position of an object/frame/target with respect to its parent.
            % In 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'S_Hlocal';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end

        function pose = Pose(this)
            % Gets the local position (pose) of an item. For example, the position of an object/frame/target with respect to its parent.
            % Out 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'G_Hlocal';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function setGeometryPose(this, pose, apply)
            % Set the position (pose) the object geometry with respect to its own reference frame. This can be applied to tools and objects.
            if nargin < 3
                apply = 0;
            end

            this.link.check_connection();
            command = 'S_Hgeo2';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.send_int(apply > 0);
            this.link.check_status();
        end

        function pose = GeometryPose(this)
            % Returns the position (pose as :class:`~robodk.robomath.Mat`) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
            this.link.check_connection();
            command = 'G_Hgeom';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function setPoseAbs(this, pose)
            % Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
            % In  1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'S_Hlocal_Abs';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(pose);
            this.link.check_status();
        end

        function pose = PoseAbs(this)
            % Gets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
            % Out 1 : 4x4 homogeneous matrix (pose)
            this.link.check_connection();
            command = 'G_Hlocal_Abs';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function color = check_color(~, color)
            % Makes formats color in a vector of size 4x1 and ranges [0,1]
            cs = numel(color);
            color = reshape(color, 1, cs);

            if cs > 4
                color = color(1:4);
            elseif cs < 4
                color = [color(1:end), zeros(1, 4 - cs)];
                color(4) = 1;
            end

            maxc = max(color);

            if maxc > 1
                color = color / maxc;
            end

        end

        function Recolor(this, tocolor, fromcolor, tolerance)
            % Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            % Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
            % In  1 : color -> color to change to
            % In  2 (optional) : color -> filter by this color
            % In  3 (optional) : int -> optional tolerance to use if a color filter is used (defaults to 0.1)
            this.link.check_connection();

            if nargin < 3
                fromcolor = [0, 0, 0, 0];
                tolerance = 2;
            elseif nargin < 4
                tolerance = 0.1;
            end

            tocolor = check_color(this, tocolor);
            fromcolor = check_color(this, fromcolor);
            command = 'Recolor';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array([tolerance(1), fromcolor, tocolor]);
            this.link.check_status();
        end

        function setColor(this, tocolor)
            % Set the color of an object, tool or robot.
            % A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            this.link.check_connection();
            tocolor = check_color(this, tocolor);
            command = 'S_Color';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(tocolor);
            this.link.check_status();
        end

        function setColorShape(this, tocolor, shape_id)
            % Set the color of an object shape. It can also be used for tools.
            % A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            this.link.check_connection();
            tocolor = check_color(this, tocolor);
            command = 'S_ShapeColor';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(shape_id);
            this.link.send_array(tocolor);
            this.link.check_status();
        end

        function setColorCurve(this, tocolor, curve_id)
            % Set the color of a curve object. It can also be used for tools.
            % A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            if nargin < 3
                curve_id = -1;
            end

            this.link.check_connection();
            tocolor = check_color(this, tocolor);
            command = 'S_CurveColor';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(curve_id);
            this.link.send_array(tocolor);
            this.link.check_status();
        end

        function color = Color(this)
            % Return the color of an :class:`.Item` (object, tool or robot). If the item has multiple colors it returns the first color available).
            % A color is in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
            this.link.check_connection();
            command = 'G_Color';
            this.link.send_line(command);
            this.link.send_item(this);
            color = this.link.rec_array();
            this.link.check_status();
        end

        function Scale(this, scale)
            % Apply a scale to an object to make it bigger or smaller.
            % the scale can be uniform (one single value) or per axis (if scale is a vector [scale_x, scale_y, scale_z]).
            % In  1 : scale -> scale to apply
            this.link.check_connection();

            if numel(scale) < 3
                scale = [scale(1); scale(1); scale(1)];
            end

            command = 'Scale';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(scale);
            this.link.check_status();
        end

        function item = AddShape(this, triangle_points)
            % Adds a shape to the object provided some triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be optionally provided.
            item = this.link.AddShape(triangle_points, this);
        end

        function item = AddCurve(this, curve_points, add_to_ref, projection_type)
            % Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.

            if nargin < 3
                add_to_ref = 0;
            end

            if nargin < 4
                projection_type = this.link.PROJECTION_ALONG_NORMAL_RECALC;
            end

            item = this.link.AddCurve(curve_points, this, add_to_ref, projection_type);
        end

        function item = AddPoints(this, points, add_to_ref, projection_type)
            % Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
            if nargin < 3
                add_to_ref = 0;
            end

            if nargin < 4
                projection_type = this.link.PROJECTION_ALONG_NORMAL_RECALC;
            end

            item = this.link.AddPoints(points, this, add_to_ref, projection_type);
        end

        function projected_points = ProjectPoints(this, points, projection_type)
            % Projects a point or a list of points to the object given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
            if nargin < 3
                projection_type = this.link.PROJECTION_ALONG_NORMAL_RECALC;
            end

            projected_points = this.link.ProjectPoints(points, this, projection_type);
        end

        function [is_selected, feature_type, feature_id] = SelectedFeature(this)
            % Retrieve the currently selected feature for this object.
            this.link.check_connection();
            command = 'G_ObjSelection';
            this.link.send_line(command);
            this.link.send_item(this);
            is_selected = this.link.rec_int();
            feature_type = this.link.rec_int();
            feature_id = this.link.rec_int();
            this.link.check_status();
        end

        function [points, feature_name] = GetPoints(this, feature_type, feature_id)
            % Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format in relative coordinates. The XYZ are the local point coordinate and ijk is the normal of the surface.
            if nargin < 2
                feature_type = this.link.FEATURE_SURFACE;
            end

            if nargin < 3
                feature_id = 0;
            end

            this.link.check_connection();
            command = 'G_ObjPoint';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(feature_type);
            this.link.send_int(feature_id);
            points = this.link.rec_matrix();
            points = transpose(points);
            feature_name = this.link.rec_line();
            this.link.check_status();
        end

        function [newprog, status] = setMachiningParameters(this, ncfile, part, params)
            % Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
            if nargin < 2
                ncfile = '';
            end

            if nargin < 3
                part = 0;
            end

            if nargin < 4
                params = '';
            end

            this.link.check_connection();
            command = 'S_MachiningParams';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(ncfile);
            this.link.send_item(part);
            this.link.send_line(params);
            set(this.link.COM, 'Timeout', 3600);
            newprog = this.link.rec_item();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            status = this.link.rec_int() / 1000.0;
            this.link.check_status();
        end

        function setAsCartesianTarget(this)
            % Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
            this.link.check_connection();
            command = 'S_Target_As_RT';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end

        function setAsJointTarget(this)
            % Sets a target as a joint target. A joint target moves to a joints position.
            this.link.check_connection();
            command = 'S_Target_As_JT';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
        end

        function is_joint = isJointTarget(this)
            % Returns True if a target is a joint target. A joint target moves to the joint position without taking into account the cartesian coordinates.
            this.link.check_connection();
            command = 'Target_Is_JT';
            this.link.send_line(command);
            this.link.send_item(this);
            is_joint = this.link.rec_int();
            this.link.check_status();
        end

        function joints = Joints(this)
            % Returns the current joints of a robot or a target. In case of a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
            % Out 1 : double x n -> joints
            this.link.check_connection();
            command = 'G_Thetas';
            this.link.send_line(command);
            this.link.send_item(this);
            joints = this.link.rec_array();
            this.link.check_status();
        end

        function joints = SimulatorJoints(this)
            % Return the current joint position of a robot (only from the simulator, never from the real robot).
            % This should be used only when RoboDK is connected to the real robot and only the simulated robot needs to be retrieved (for example, if we want to move the robot using a spacemouse).
            % Note: Use robot.Joints() instead to retrieve the simulated and real robot position when connected.
            this.link.check_connection();
            command = 'G_Thetas_Sim';
            this.link.send_line(command);
            this.link.send_item(this);
            joints = this.link.rec_array();
            this.link.check_status();
        end

        function poses = JointPoses(this, joints)
            % Returns the positions of the joint links for a provided robot configuration (joints). If no joints are provided it will return the poses for the current robot position.
            % Out 1 : 4x4 x n -> array of 4x4 homogeneous matrices. Index 0 is the base frame reference (it never moves when the joints move).
            this.link.check_connection();
            command = 'G_LinkPoses';
            this.link.send_line(command);
            this.link.send_item(this);

            if nargin < 2
                this.link.send_array([]);
            else
                this.link.send_array(joints);
            end

            nlinks = this.link.rec_int();
            poses = cell(1, nlinks);

            for i = 1:nlinks
                poses{i} = this.link.rec_pose();
            end

            this.link.check_status();
        end

        function joints = JointsHome(this)
            % Return the home joints of a robot. The home joints can be manually set in the robot "Parameters" menu of the robot panel in RoboDK, then select "Set home position".
            % Out 1 : double x n -> joints
            this.link.check_connection();
            command = 'G_Home';
            this.link.send_line(command);
            this.link.send_item(this);
            joints = this.link.rec_array();
            this.link.check_status();
        end

        function setJointsHome(this, joints)
            % Set the home position of the robot in the joint space.
            % In  1 : double x n -> joints
            this.link.check_connection();
            command = 'S_Home';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            this.link.check_status();
        end

        function item = ObjectLink(this, link_id)
            % Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.
            if nargin < 2
                link_id = 0;
            end

            this.link.check_connection();
            command = 'G_LinkObjId';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(link_id);
            item = this.link.rec_item();
            this.link.check_status();
        end

        function item = getLink(this, item_type)
            % Returns an item pointer (:class:`.Item`) to a robot, object, tool or program. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
            % In  1 : int item type (such as RDK.ITEM_TYPE_ROBOT)
            this.link.check_connection();
            command = 'G_LinkType';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(item_type);
            item = this.link.rec_item();
            this.link.check_status();
        end

        function setLink(this, item)
            % Sets a link between this item and the specified item.
            % This is useful to set the relationship between programs, robots, tools and other specific projects.

            if nargin < 2
                item = RobolinkItem(this.link);
            end

            this.link.check_connection();
            command = 'S_Link_ptr';
            this.link.send_line(command);
            this.link.send_item(item);
            this.link.send_item(this);
            this.link.check_status();
        end

        function setJoints(this, joints)
            % Sets the current joints of a robot or a target. In case of a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
            % In  1 : double x n -> joints
            this.link.check_connection();
            command = 'S_Thetas';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            this.link.check_status();
        end

        function [lim_inf, lim_sup, joints_type] = JointLimits(this)
            % Retrieve the joint limits of a robot. Returns (lower limits, upper limits, joint type)
            this.link.check_connection();
            command = 'G_RobLimits';
            this.link.send_line(command);
            this.link.send_item(this);
            lim_inf = this.link.rec_array()';
            lim_sup = this.link.rec_array()';
            joints_type = this.link.rec_int() / 1000.0;
            this.link.check_status();
        end

        function setJointLimits(this, lower_lim, upper_lim)
            % Update the robot joint limits
            % In  1 : double x n -> lower joint limits
            % In  2 : double x n -> upper joint limits
            this.link.check_connection();
            command = 'S_RobLimits';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(lower_lim);
            this.link.send_array(upper_lim);
            this.link.check_status();
        end

        function setRobot(this, robot)
            % Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
            % If the robot is not provided, the first available robot will be chosen automatically.
            % In  1 : robot (optional) -> robot item
            if nargin < 2
                robot = RobolinkItem(this.link);
            end

            this.link.check_connection();
            command = 'S_Robot';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_item(robot);
            this.link.check_status();
        end

        function setPoseFrame(this, frame)
            % Sets the frame of a robot. The frame can be either an item pointer or a 4x4 Matrix.
            % If "frame" is an item pointer, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
            % In  1 : item/pose -> frame item or 4x4 Matrix (pose of the reference frame)
            this.link.check_connection();

            if numel(frame) == 1
                command = 'S_Link_ptr';
                this.link.send_line(command);
                this.link.send_item(frame);
            else
                command = 'S_Frame';
                this.link.send_line(command);
                this.link.send_pose(frame);
            end

            this.link.send_item(this);
            this.link.check_status();
        end

        function setPoseTool(this, tool)
            % Set the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
            this.link.check_connection();

            if isa(tool, class(this))
                command = 'S_Tool_ptr';
                this.link.send_line(command);
                this.link.send_item(tool);
            else
                command = 'S_Tool';
                this.link.send_line(command);
                this.link.send_pose(tool);
            end

            this.link.send_item(this);
            this.link.check_status();
        end

        function pose = PoseTool(this)
            % Returns the pose (:class:`~robodk.robomath.Mat`) of the robot tool (TCP) with respect to the robot flange
            this.link.check_connection();
            command = 'G_Tool';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function pose = PoseFrame(this)
            % Returns the pose (:class:`~robodk.robomath.Mat`) of the robot reference frame with respect to the robot base
            this.link.check_connection();
            command = 'G_Frame';
            this.link.send_line(command);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function setTool(this, tool)
            % Sets the tool pose of a robot. The tool pose can be either an item pointer or a 4x4 Matrix.
            % If "tool" is an item pointer, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
            % In  1 : item/pose -> tool item or 4x4 Matrix (pose of the tool frame)
            setPoseTool(this, tool);
        end

        function newtool = AddTool(this, tool_pose, tool_name)
            % Add a tool to a robot given the tool pose and the tool name. It returns the tool as an :class:`.Item`.
            if nargin < 3
                tool_name = 'New TCP';
            end

            this.link.check_connection();
            command = 'AddToolEmpty';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_pose(tool_pose);
            this.link.send_line(tool_name);
            newtool = this.link.rec_item();
            this.link.check_status();
        end

        function pose = SolveFK(this, joints)
            % Computes the forward kinematics for the specified robot and joints.
            % In  1 : double x n -> joints
            % Out 1 : 4x4 matrix -> pose of the robot flange with respect to the base frame
            this.link.check_connection();
            command = 'G_FK';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            pose = this.link.rec_pose();
            this.link.check_status();
        end

        function config = JointsConfig(this, joints)
            % Returns the robot configuration state for a set of robot joints.
            % In  1 : double x n -> joints
            % Out 1 : The configuration state is defined as: [REAR, LOWERARM, FLIP, turns].
            this.link.check_connection();
            command = 'G_Thetas_Config';
            this.link.send_line(command);
            this.link.send_array(joints);
            this.link.send_item(this);
            config = this.link.rec_array()';
            this.link.check_status();
        end

        function joints = SolveIK(this, pose, joints_approx)
            % Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see Solve_IK_All()).
            % In  1 : 4x4 matrix -> pose of the robot flange with respect to the base frame
            % In  2 : double x n -> approximated joint values to return the closest solution
            % Out 1 : double x n -> joints
            this.link.check_connection();

            if nargin < 3
                command = 'G_IK';
                this.link.send_line(command);
                this.link.send_pose(pose);
                this.link.send_item(this);
            else
                command = 'G_IK_jnts';
                this.link.send_line(command);
                this.link.send_pose(pose);
                this.link.send_array(joints_approx);
                this.link.send_item(this);
            end

            joints = this.link.rec_array();
            this.link.check_status();
        end

        function joints_list = SolveIK_All(this, pose)
            % Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
            % In  1 : 4x4 matrix -> pose of the robot tool with respect to the robot frame
            % Out 1 : double x n x m -> joint list (2D matrix)
            this.link.check_connection();
            command = 'G_IK_cmpl';
            this.link.send_line(command);
            this.link.send_pose(pose);
            this.link.send_item(this);
            joints_list = this.link.rec_matrix();

            if size(joints_list, 1) == 6
                joints_list = joints_list(1:end - 2, :);
            end

            this.link.check_status();
        end

        function [pose_filtered, joints_filtered] = FilterTarget(this, pose, joints_approx)
            % Filters a target to improve accuracy. This option requires a calibrated robot.
            if nargin < 3
                joints_approx = [0; 0; 0; 0; 0; 0];
            end

            this.link.check_connection();
            command = 'FilterTarget';
            this.link.send_line(command);
            this.link.send_pose(pose);
            this.link.send_array(joints_approx);
            this.link.send_item(this);
            pose_filtered = this.link.rec_pose();
            joints_filtered = this.link.rec_array();
            this.link.check_status();
        end

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function status = Connect(this, robot_ip, blocking, timeout)
            % Connect to a real robot and wait for a connection to succeed. Returns 1 if connection succeeded, or 0 if it failed.
            % In 1 : Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
            % In 2 : blocking: set to 1 to block until the robot is
            % connected
            % In 3 : Timeout for the connection
            % Out 1 : Status (1 if success)
            if nargin < 2
                robot_ip = '';
            end

            if nargin < 3
                blocking = 1;
            end

            if nargin < 4
                timeout = this.link.TIMEOUT;
            end

            this.link.check_connection();
            command = 'Connect2';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(robot_ip);
            this.link.send_int(blocking);
            set(this.link.COM, 'Timeout', timeout);
            status = this.link.rec_int();
            this.link.check_status();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
        end

        function [robot_ip, port, remote_path, ftp_user, ftp_pass] = ConnectionParams(this)
            % Retrieve robot connection parameters
            this.link.check_connection();
            command = 'ConnectParams';
            this.link.send_line(command);
            this.link.send_item(this);
            robot_ip = this.link.rec_line();
            port = this.link.rec_int();
            remote_path = this.link.rec_line();
            ftp_user = this.link.rec_line();
            ftp_pass = this.link.rec_line();
            this.link.check_status();
        end

        function itm = setConnectionParams(this, robot_ip, port, remote_path, ftp_user, ftp_pass)
            % Retrieve robot connection parameters
            this.link.check_connection();
            command = 'setConnectParams';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(robot_ip);
            this.link.send_int(port);
            this.link.send_line(remote_path);
            this.link.send_line(ftp_user);
            this.link.send_line(ftp_pass);
            this.link.check_status();
            itm = this;
        end

        function [robotcom_status, status_msg] = ConnectedState(this)
            % Check connection status with a real robobt
            % Out 1 : status code -> (int) ROBOTCOM_READY if the robot is ready to move, otherwise, status message will provide more information about the issue
            % Out 2 : status message -> Message description of the robot status
            this.link.check_connection();
            command = 'ConnectedState';
            this.link.send_line(command);
            this.link.send_item(this);
            robotcom_status = this.link.rec_int();
            status_msg = this.link.rec_line();
            this.link.check_status();
        end

        function status = Disconnect(this)
            % Disconnect from a real robot (when the robot driver is used)
            % Returns 1 if it disconnected successfully, 0 if it failed. It can fail if it was previously disconnected manually for example.
            % Out 1 : Status (1 if success)
            this.link.check_connection();
            command = 'Disconnect';
            this.link.send_line(command);
            this.link.send_item(this);
            status = this.link.rec_int();
            this.link.check_status();
        end

        function MoveJ(this, target, blocking)
            % Moves a robot to a specific target ("Move Joint" mode). This function blocks until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional) blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 3
                blocking = 1;
            end

            if this.type == this.link.ITEM_TYPE_PROGRAM
                blocking = 0;

                if isa(target, class(this))
                    this.addMoveJ(target);
                    return
                end

            end

            this.link.moveX(target, this, this.link.MOVE_TYPE_JOINT, blocking);

        end

        function MoveL(this, target, blocking)
            % Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional): blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 3
                blocking = 1;
            end

            if this.type == this.link.ITEM_TYPE_PROGRAM
                blocking = 0;

                if isa(target, class(this))
                    this.addMoveL(target);
                    return
                end

            end

            this.link.moveX(target, this, this.link.MOVE_TYPE_LINEAR, blocking);

        end

        function joints = SearchL(this, target, blocking)
            % Moves a robot to a specific target and stops when a specific input switch is detected ("Search Linear" mode). This function waits (blocks) until the robot finishes its movements.

            if nargin < 3
                blocking = 1;
            end

            if this.type == this.link.ITEM_TYPE_PROGRAM
                this.moveX(target, this, this.link.MOVE_TYPE_LINEARSEARCH, 0);
                joints = [];
                return
            end

            this.link.moveX(target, this, this.link.MOVE_TYPE_LINEARSEARCH, blocking)
            joints = this.SimulatorJoints();
        end

        function MoveC(this, target1, target2, blocking)
            % Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements.
            % In  1 : joints/pose/item -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or an item (item pointer)
            % In  2 (optional) blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)
            if nargin < 4
                blocking = 1;
            end

            if this.type == this.link.ITEM_TYPE_PROGRAM

                if ~isa(target1, class(this)) || ~isa(target2, class(this))
                    error('Adding a movement instruction to a program given joints or a pose is not supported. Use a target item instead, for example, add a target as with RDK.AddTarget(...) and set the pose or joints.')
                end

                this.addMoveC(target1, target2);
            else
                this.link.moveC(target1, target2, this, blocking);
            end

        end

        function collision = MoveJ_Test(this, j1, j2, minstep_deg)
            % Checks if a joint movement is free of collision.
            % In  1 : joints -> start joints
            % In  2 : joints -> destination joints
            % In  3 (optional) maximum joint step in degrees
            % Out : collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.
            if nargin < 4
                minstep_deg = -1;
            end

            this.link.check_connection();
            command = 'CollisionMove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(j1);
            this.link.send_array(j2);
            this.link.send_int(minstep_deg * 1000);
            set(this.link.COM, 'Timeout', 3600);
            collision = this.link.rec_int();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            this.link.check_status();
        end

        function collision = MoveJ_Test_Blend(this, j1, j2, j3, blend_deg, minstep_deg)
            % Checks if a joint movement with blending is feasible and free of collisions (if collision checking is activated). The robot will move to the collision point if a collision is detected (use Joints to collect the collision joints) or it will be placed at the destination joints if a collision is not detected.

            if nargin < 5
                blend_deg = 5;
            end

            if nargin < 6
                minstep_deg = -1;
            end

            this.link.check_connection();
            this.link.send_line("CollisionMoveBlend")
            this.link.send_item(this)
            this.link.send_array(j1)
            this.link.send_array(j2)
            this.link.send_array(j3)
            this.link.send_int(minstep_deg * 1000.0)
            this.link.send_int(blend_deg * 1000.0)
            set(this.link.COM, 'Timeout', 3600);
            collision = this.link.rec_int();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            this.link.check_status()
        end

        function collision = MoveL_Test(this, j1, poseto, minstep_deg)
            % Checks if a joint movement is free of collision.
            % In  1 : joints -> start joints
            % In  2 : pose -> destination pose with respect to current reference and tool frames
            % In  3 (optional) maximum joint step in degrees
            % Out : collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.
            %                  if the robot can not reach the target pose it returns -2. If the robot can reach the target but it can not make a linear movement it returns -1
            if nargin < 4
                minstep_deg = -1;
            end

            this.link.check_connection();
            command = 'CollisionMoveL';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array(j1);
            this.link.send_pose(poseto);
            this.link.send_int(minstep_deg * 1000);
            set(this.link.COM, 'Timeout', 3600);
            collision = this.link.rec_int();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            this.link.check_status();
        end

        function setSpeed(this, speed_linear, speed_joints, accel_linear, accel_joints)
            % Sets the speed and/or the acceleration of a robot.
            % In  1 : speed_linear: linear speed -> speed in mm/s (-1 = no change)
            % In  2 : speed_joints: joint speed (optional) -> acceleration in mm/s2 (-1 = no change)
            % In  3 : accel_linear: linear acceleration (optional) -> acceleration in mm/s2 (-1 = no change)
            % In  4 : accel_joints: joint acceleration (optional) -> acceleration in deg/s2 (-1 = no change)
            if nargin < 3
                speed_joints = -1;
            end

            if nargin < 4
                accel_linear = -1;
            end

            if nargin < 5
                accel_joints = -1;
            end

            this.link.check_connection();
            command = 'S_Speed4';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array([speed_linear, speed_joints, accel_linear, accel_joints]);
            this.link.check_status();
        end

        function setAcceleration(this, accel_linear)
            % Sets the linear acceleration of a robot in mm/s2
            this.setSpeed(-1, -1, accel_linear, -1)
        end

        function setSpeedJoints(this, speed_joints)
            % Sets the joint speed of a robot in deg/s for rotary joints and mm/s for linear joints
            this.setSpeed(-1, speed_joints, -1, -1)
        end

        function setAccelerationJoints(this, accel_joints)
            % Sets the joint acceleration of a robot
            this.setSpeed(-1, -1, -1, accel_joints)
        end

        function setRounding(this, rounding_mm)
            % Sets the rounding accuracy to smooth the edges of corners. In general, it is recommended to allow a small approximation near the corners to maintain a constant speed.
            % Setting a rounding values greater than 0 helps avoiding jerky movements caused by constant acceleration and decelerations.
            % This rounding parameter is also known as ZoneData (ABB), CNT (Fanuc), C_DIS/ADVANCE (KUKA), cornering (Mecademic) or blending (Universal Robots)
            this.link.check_connection();
            command = 'S_ZoneData';
            this.link.send_line(command);
            this.link.send_int(rounding_mm * 1000);
            this.link.send_item(this);
            this.link.check_status();
        end

        function setZoneData(this, zonedata)
            % Sets the robot zone data value.
            % In  1 : zonedata value (robot dependent, set to -1 for fine movements)
            this.setZoneData(zonedata)
        end

        function ShowSequence(this, matrix, display_type, timeout)
            % Sends a joint sequence or an instruction sequence (like in RoKiSim).
            % In  1 : sequence
            if nargin < 3
                display_type = this.link.SEQUENCE_DISPLAY_DEFAULT;
            end

            if nargin < 4
                timeout = -1;
            end

            display_ghost_joints = 0;

            if display_type > 0
                display_ghost_joints = bitand(display_type, 2048);
            end

            if display_ghost_joints
                % poses assumed
                this.link.check_connection()
                command = 'Show_SeqPoses';
                this.link.send_line(command)
                this.link.send_item(self)
                this.link.send_array([display_type, timeout])
                this.link.send_int(len(matrix))

                if display_ghost_joints

                    for jnts = 1:length(matrix)
                        self.link.send_array(jnts)
                    end

                else

                    for pose = 1:length(matrix)
                        self.link.send_pose(pose)
                    end

                end

                this.link.check_status()

            else
                % list of joints as a Mat assumed
                this.link.check_connection();
                command = 'Show_Seq';
                this.link.send_line(command);
                this.link.send_matrix(matrix);
                this.link.send_item(this);
                this.link.check_status();
            end

        end

        function busy = Busy(this)
            % Checks if a robot or program is currently running (busy or moving).
            % In  1 : item -> robot to check
            % Out 1 : int -> busy status (1=moving, 0=stopped)
            this.link.check_connection();
            command = 'IsBusy';
            this.link.send_line(command);
            this.link.send_item(this);
            busy = this.link.rec_int();
            this.link.check_status();
        end

        function Stop(this)
            % Stop a program or a robot
            this.link.check_connection();
            command = 'Stop';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.check_status()
        end

        function WaitMove(this, timeout)
            % Waits (blocks) until the robot finished its move.
            % In  1 (optional) timeout -> Max time to wait for robot to finish its movement (in seconds)
            if nargin < 2
                timeout = 300;
            end

            this.link.check_connection();
            command = 'WaitMove';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.check_status();
            set(this.link.COM, 'Timeout', timeout);
            this.link.check_status();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
        end

        function WaitFinished(this)
            % Wait until a program finishes or a robot completes its movement
            busy = Busy(this);

            while busy
                busy = Busy(this);
                pause(0.05);
            end

        end

        function errors = ProgramStart(this, programname, folder, postprocessor)
            % Defines the name of the program when a program must be generated.
            % It is possible to specify the name of the post processor as well as the folder to save the program.
            % This method must be called before any program output is generated (before any robot movement or other program instructions).

            if nargin < 3
                folder = '';
            end

            if nargin < 4
                postprocessor = '';
            end

            errors = this.link.ProgramStart(programname, folder, postprocessor, this);
        end

        function setAccuracyActive(this, accurate)
            % Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.
            % In 1: int set to 1 to use the accurate model or 0 to use the nominal model
            this.link.check_connection();
            command = 'S_AbsAccOn';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(accurate);
            this.link.check_status();
        end

        function accurate = AccuracyActive(this)
            % Returns True if the accurate kinematics are being used. Accurate kinematics are available after a robot calibration.
            this.link.check_connection();
            command = 'G_AbsAccOn';
            this.link.send_line(command);
            this.link.send_item(this);
            accurate = this.link.rec_int();
            this.link.check_status();
        end

        function setParamRobotTool(this, tool_mass, tool_cog)
            % Sets the tool mass and center of gravity. This is only used with accurate robots to improve accuracy.
            this.link.check_connection();
            command = 'S_ParamCalibTool';
            this.link.send_line(command)
            this.link.send_item(this)
            values = tool_mass + tool_cog;
            this.link.send_array(values)
            this.link.check_status()
        end

        function [filter_status, filter_msg] = FilterProgram(this, filestr)
            % Filter a program file to improve accuracy for a specific robot. The robot must have been previously calibrated.
            % It returns 0 if the filter succeeded, or a negative value if there are filtering problems. It also returns a summary of the filtering.
            this.link.check_connection();
            command = 'FilterProg2';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(filestr)
            filter_status = this.link.rec_int();
            filter_msg = this.link.rec_line();
            this.link.check_status()
        end

        function [success, prog_log_str, transfer_ok] = MakeProgram(this, folder_path, run_mode)
            % Generate the program file. Returns True if the program was successfully generated.

            if nargin < 2
                folder_path = '';
            end

            if nargin < 3
                folder_path = this.link.RUNMODE_MAKE_ROBOTPROG;
            end

            this.link.check_connection();
            command = 'MakeProg2';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(folder_path)
            this.link.send_int(run_mode)
            set(this.link.COM, 'Timeout', 300);
            prog_status = this.link.rec_int();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            prog_log_str = this.link.rec_line();
            transfer_status = this.link.rec_int();
            this.link.check_status()
            success = 0;

            if prog_status > 0
                success = 1;
            end

            transfer_ok = 0;

            if transfer_status > 0
                transfer_ok = 1;
            end

        end

        function setRunType(this, program_run_type)
            % Set the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).
            % In 1: int Use "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot
            this.link.check_connection();
            command = 'S_ProgRunType';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(program_run_type);
            this.link.check_status();
        end

        function runtype = RunType(this)
            % Get the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).
            this.link.check_connection();
            command = 'G_ProgRunType';
            this.link.send_line(command);
            this.link.send_item(this);
            runtype = this.link.rec_int();
            this.link.check_status();
        end

        function prog_status = RunProgram(this)
            % Obsolete. Use RunCode Instead.
            this.link.check_connection();
            command = 'RunProg';
            this.link.send_line(command);
            this.link.send_item(this);
            prog_status = this.link.rec_int();
            this.link.check_status();
        end

        function prog_status = RunCode(this)
            % Runs a program. It returns the number of instructions that can be executed successfully (a quick check is performed before the program starts)
            % This is a non-blocking call.
            % Out 1 : int -> number of instructions that can be executed
            this.link.check_connection();
            command = 'RunProg';
            this.link.send_line(command);
            this.link.send_item(this);
            prog_status = this.link.rec_int();
            this.link.check_status();
        end

        function prog_status = RunInstruction(this, code, run_type)
            % Add a program call, code, message or comment to the program. Returns 0 if succeeded.
            % In 1 : int -> the code to insert, program to run, or comment to add.
            % In 2 : int -> Use INSTRUCTION_* variable to specify if the
            % code is a program call or just a raw code insert.
            % Out 1 : int -> number of instructions that can be executed
            if nargin < 3
                run_type = this.link.INSTRUCTION_CALL_PROGRAM;
            end

            this.link.check_connection();
            command = 'RunCode2';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(strrep(strrep(code, '\r\n', '<<br>>'), '\r', '<<br>>'));
            this.link.send_int(run_type);
            prog_status = this.link.rec_int();
            this.link.check_status();
        end

        function Pause(this, time_ms)
            % Pause instruction for a robot or insert a pause instruction to a program (when generating code offline -offline programming- or when connected to the robot -online programming-).
            % In 1 : double -> Pause time in milliseconds
            if nargin < 2
                time_ms = -1;
            end

            this.link.check_connection();
            command = 'RunPause';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(time_ms * 1000.0);
            this.link.check_status();
        end

        function setDO(this, do_variable, do_value)
            % Set a Digital Output (DO). This command can also be used to set any generic variables to a desired value.
            % In 1 : str -> Digital Output variable
            % In 2 : str -> Digital Output value
            this.link.check_connection();
            command = 'setDO';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(do_variable);
            this.link.send_line(do_value);
            this.link.check_status();
        end

        function setAO(this, io_var, io_value)
            % Set an Analog Output (AO).
            this.link.check_connection();
            command = 'setAO';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(io_var)
            this.link.send_line(io_value)
            this.link.check_status()
        end

        function io_value = getDI(this, io_var)
            % Get a Digital Input (DI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (1=True, 0=False). This function returns an empty string if the script is not executed on the robot.
            this.link.check_connection();
            command = 'getDI';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(io_var)
            io_value = this.link.rec_line();
            this.link.check_status()
        end

        function io_value = getAI(this, io_var)
            % Get an Analog Input (AI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (0-1 or other range depending on the robot driver). This function returns an empty string if the script is not executed on the robot.
            this.link.check_connection();
            command = 'getAI';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(io_var)
            io_value = this.link.rec_line();
            this.link.check_status()
        end

        function waitDI(this, di_variable, di_value, timeout_ms)
            % Wait for an digital input io_var to attain a given value io_value. Optionally, a timeout can be provided.
            % In 1 : str -> Digital Input variable
            % In 2 : str -> Digital Input value
            if nargin < 3
                timeout_ms = -1;
            end

            this.link.check_connection();
            command = 'waitDI';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(di_variable);
            this.link.send_line(di_value);
            this.link.send_int(timeout_ms * 1000.0);
            set(this.link.COM, 'Timeout', 3600 * 24 * 7); % Wait up to 1 week
            this.link.check_status();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
        end

        function customInstruction(this, name, path_run, path_icon, blocking, cmd_run_on_robot)
            % Add a custom instruction. This instruction will execute a Python file or an executable file.
            if nargin < 4
                path_icon = "";
            end

            if nargin < 5
                blocking = 1;
            end

            if nargin < 6
                cmd_run_on_robot = "";
            end

            this.link.check_connection();
            command = 'InsCustom2';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_line(name)
            this.link.send_line(path_run)
            this.link.send_line(path_icon)
            this.link.send_line(cmd_run_on_robot)
            this.link.send_int(blocking)
            this.link.check_status()
        end

        function addMoveJ(this, itemtarget)
            % Adds a new "Move Joint" instruction to a program.
            % In  1 : item -> target to move to
            this.link.check_connection();
            command = 'Add_INSMOVE';
            this.link.send_line(command);
            this.link.send_item(itemtarget);
            this.link.send_item(this);
            this.link.send_int(1);
            this.link.check_status();
        end

        function addMoveL(this, itemtarget)
            % (Obsolete, use MoveL instead) Adds a new "Move Linear" instruction to a program.
            % In  1 : item -> target to move to
            this.link.check_connection();
            command = 'Add_INSMOVE';
            this.link.send_line(command);
            this.link.send_item(itemtarget);
            this.link.send_item(this);
            this.link.send_int(2);
            this.link.check_status();
        end

        function addMoveSearch(this, itemtarget)
            % (Obsolete, use SearchL instead)
            % Adds a new linear search move instruction to a program.
            this.link.check_connection();
            command = 'Add_INSMOVE';
            this.link.send_line(command)
            this.link.send_item(itemtarget)
            this.link.send_item(this)
            this.link.send_int(5)
            this.link.check_status()
        end

        function addMoveC(this, itemtarget1, itemtarget2)
            % (Obsolete, use MoveC instead) Adds a new "Move Circular" instruction to a program.
            % In  1 : item -> target to move to (via point)
            % In  2 : item -> target to move to (final point)
            this.link.check_connection();
            command = 'Add_INSMOVEC';
            this.link.send_line(command);
            this.link.send_item(itemtarget1);
            this.link.send_item(itemtarget2);
            this.link.send_item(this);
            this.link.check_status();
        end

        function ShowInstructions(this, display)
            % Show or hide instruction items of a program in the RoboDK tree
            if nargin < 2
                display = 1;
            end

            this.link.check_connection();
            command = 'Prog_ShowIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(display);
            this.link.check_status();
        end

        function ShowTargets(this, display)
            % Show or hide targets of a program in the RoboDK tree
            if nargin < 2
                display = 1;
            end

            this.link.check_connection();
            command = 'Prog_ShowTargets';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(display);
            this.link.check_status();
        end

        function nins = InstructionCount(this)
            % Returns the number of instructions of a program.
            this.link.check_connection();
            command = 'Prog_Nins';
            this.link.send_line(command);
            this.link.send_item(this);
            nins = this.link.rec_int();
            this.link.check_status();
        end

        function ins_id = InstructionSelect(this, ins_id)
            % Select an instruction in the program as a reference to add new instructions. New instructions will be added after the selected instruction.
            % If no instruction ID is specified, the active instruction will be selected and returned (if the program is running), otherwise it returns -1.
            if nargin < 2
                ins_id = -1;
            end

            this.link.check_connection();
            command = 'Prog_SelIns';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_int(ins_id)
            ins_id = this.link.rec_int();
            this.link.check_status()
        end

        function success = InstructionDelete(this, ins_id)
            % Delete an instruction of a program
            if nargin < 2
                ins_id = 0;
            end

            this.link.check_connection();
            command = 'Prog_DelIns';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_int(ins_id)
            success = this.link.rec_int() > 0;
            this.link.check_status()
        end

        function [name, instype, movetype, isjointtarget, target, joints] = Instruction(this, ins_id)
            % Returns the program instruction at position id.
            this.link.check_connection();
            command = 'Prog_GIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(ins_id - 1);
            name = this.link.rec_line();
            instype = this.link.rec_int();
            movetype = -1;
            isjointtarget = -1;
            target = -1;
            joints = -1;

            if instype == this.link.INS_TYPE_MOVE
                movetype = this.link.rec_int();
                isjointtarget = this.link.rec_int();
                target = this.link.rec_pose();
                joints = this.link.rec_array();
            end

            this.link.check_status();
        end

        function setInstruction(this, ins_id, name, instype, movetype, isjointtarget, target, joints)
            % Sets the program instruction at position id.
            this.link.check_connection();
            command = 'Prog_SIns';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_int(ins_id - 1);
            this.link.send_line(name);
            this.link.send_int(instype);

            if instype == this.link.INS_TYPE_MOVE
                this.link.send_int(movetype);
                this.link.send_int(isjointtarget);
                this.link.send_pose(target);
                this.link.send_array(joints);
            end

            this.link.check_status();
        end

        function [valid_instructions, program_time, program_distance, valid_ratio, readable_msg] = Update(this, check_collisions, timeout_sec, mm_step, deg_step)
            % Updates a program and returns the estimated time and the number of valid instructions.
            % An update can also be applied to a robot machining project. The update is performed on the generated program.
            if nargin < 2
                check_collisions = this.link.COLLISION_OFF;
            end

            if nargin < 3
                timeout_sec = 3600;
            end

            if nargin < 4
                mm_step = -1;
            end

            if nargin < 5
                deg_step = -1;
            end

            this.link.check_connection();
            command = 'Update2';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_array([check_collisions, mm_step, deg_step]);
            set(this.link.COM, 'Timeout', timeout_sec);
            values = this.link.rec_array();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            readable_msg = this.link.rec_line();
            this.link.check_status();
            valid_instructions = values(1);
            program_time = values(2);
            program_distance = values(3);
            valid_ratio = values(4);
        end

        function [insmat, errors] = InstructionList(this)
            % Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes. This is the equivalent sequence that used to be supported by RoKiSim.
            % Tip: Use RDK.ShowSequence(matrix) to dipslay a joint list or a RoKiSim sequence of instructions.
            this.link.check_connection();
            command = 'G_ProgInsList';
            this.link.send_line(command)
            this.link.send_item(this)
            insmat = this.link.rec_matrix();
            errors = this.link.rec_int();
            this.link.check_status()
        end

        function [error_msg, joint_list, error_code] = InstructionListJoints(this, mm_step, deg_step, save_to_file, collision_check, flags, time_step)
            % Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.

            if nargin < 2
                mm_step = 10;
            end

            if nargin < 3
                deg_step = 5;
            end

            if nargin < 4
                save_to_file = '';
            end

            if nargin < 5
                collision_check = this.link.COLLISION_OFF;
            end

            if nargin < 6
                flags = 0;
            end

            if nargin < 7
                time_step = 0.1;
            end

            this.link.check_connection();
            command = 'G_ProgJointList';
            this.link.send_line(command)
            this.link.send_item(this)
            this.link.send_array([mm_step, deg_step, float(collision_check), float(flags), float(time_step)])
            joint_list = save_to_file;
            set(this.link.COM, 'Timeout', 3600);

            if isempty(save_to_file)
                this.link.send_line('')
                joint_list = this.link.rec_matrix();
            else
                this.link.send_line(save_to_file)
            end

            error_code = this.link.rec_int();
            set(this.link.COM, 'Timeout', this.link.TIMEOUT);
            error_msg = this.link.rec_line();
            this.link.check_status()
        end

        function data = getParam(this, param)
            % Get custom binary data from this item. Use setParam to set the data.
            this.link.check_connection();
            command = 'G_ItmDataParam';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(param);
            data = this.link.rec_bytes();
            this.link.check_status();
        end

        function data = setParam(this, param, value)
            % Get custom binary data from this item. Use setParam to set the data.
            this.link.check_connection();
            command = 'ICMD';
            this.link.send_line(command);
            this.link.send_item(this);
            this.link.send_line(param);
            this.link.send_line(value);
            data = this.link.rec_line();
            if numel(data) > 1 && data(1) == '{'
                data = jsondecode(data);
            end
            this.link.check_status()
        end

    end

end
