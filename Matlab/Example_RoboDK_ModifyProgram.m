% This is an example that uses the RoboDK API for Matlab.
% This is a .m file (Matlab file).
% The RoboDK API for Matlab requires the files in this folder.
% This example requires RoboDK to be running 
% (otherwise, RoboDK will be started if it was installed in the default location)
% This example automatically loads the Example 01 installed by default in the "Library" folder

% Note: This program is not meant to accomplish a specific goal, only to
% show how to use the Matlab API
% 
% RoboDK api Help:
% ->Type "doc Robolink"            for more help on the Robolink class
% ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
% ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes

clc
clear
close all

% Generate a Robolink object RDK. This object interfaces with RoboDK.
RDK = Robolink;

% Get the library path
path = RDK.getParam('PATH_LIBRARY');

% Open example 4
RDK.AddFile([path,'Example 04 - Robot Milling 3axes.rdk']);

% Display a list of all items
fprintf('Available items in the station:\n');
disp(RDK.ItemList());

% Get all programs
allprograms = RDK.ItemList(RDK.ITEM_TYPE_PROGRAM);
if numel(allprograms) < 1
    error('No programs found in the station!')
end

% Select first program:
selectprogram = allprograms{1};
fprintf('Selecting program: %s\n',selectprogram)
prog = RDK.Item(selectprogram);

% Turn off automatic rendering
RDK.Render(0);
% Iterate through the instructions in the program:
nins = prog.InstructionCount();
fprintf('%i instructions in %s\n', nins, selectprogram);
for i=1:nins
    [name, instype, movetype, isjointtarget, pose, joints] = prog.Instruction(i);
    fprintf('Instruction %i: %s\t', i, name);
    if instype == RobolinkItem.INS_TYPE_MOVE && movetype == RDK.MOVE_TYPE_LINEAR && isjointtarget == 0
        % Shift/rotate the current pose
        fprintf('(modifying instruction)');
        pose2 = transl(0,0,10)*pose;%*rotz(-2*pi/180)*pose;
        name2 = [name, ' shifted']; % note: right click program and select show instructions
        prog.setInstruction(i, name2, instype, movetype, isjointtarget, pose2, joints);
    end
    fprintf('\n');
end
RDK.Render(1);


% Start selected program
prog.RunProgram();
