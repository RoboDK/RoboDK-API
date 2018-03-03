% Convert a position from [x,y,z,w,p,r] to a 4x4 pose.
% The Euler conversion used is the same one used by Fanuc controllers.
function H = Fanuc_2_Pose(xyzrpw)

x = xyzrpw(1);
y = xyzrpw(2);
z = xyzrpw(3);
a = xyzrpw(4)*pi/180;
b = xyzrpw(5)*pi/180;
c = xyzrpw(6)*pi/180;

H = [ cos(b)*cos(c), cos(c)*sin(a)*sin(b) - cos(a)*sin(c), sin(a)*sin(c) + cos(a)*cos(c)*sin(b),  x;
      cos(b)*sin(c), cos(a)*cos(c) + sin(a)*sin(b)*sin(c), cos(a)*sin(b)*sin(c) - cos(c)*sin(a),  y;
            -sin(b),                        cos(b)*sin(a),                        cos(a)*cos(b),  z;
                  0,                                    0,                                    0,  1];