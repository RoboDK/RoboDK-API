% Convert a position from [x,y,z,A,B,C] (mm and deg) to a 4x4 pose.
% The Euler conversion used is the same one used by KUKA KRC controllers.
function H = KUKA_2_Pose(xyzrpw)

x = xyzrpw(1);
y = xyzrpw(2);
z = xyzrpw(3);
a = xyzrpw(4)*pi/180;
b = xyzrpw(5)*pi/180;
c = xyzrpw(6)*pi/180;

H = [ cos(b)*cos(a), cos(a)*sin(c)*sin(b) - cos(c)*sin(a), sin(c)*sin(a) + cos(c)*cos(a)*sin(b),  x;
      cos(b)*sin(a), cos(c)*cos(a) + sin(c)*sin(b)*sin(a), cos(c)*sin(b)*sin(a) - cos(a)*sin(c),  y;
            -sin(b),                        cos(b)*sin(c),                        cos(c)*cos(b),  z;
                  0,                                    0,                                    0,  1];