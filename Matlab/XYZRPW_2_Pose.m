% Convert a position from [x,y,z,rX,rY,rZ] (mm and rad) to a 4x4 pose.
% The Euler conversion used is the same one used by Staubli controllers (using radians instead of degrees).
function H = XYZRPW_2_Pose(xyzrpw)
x = xyzrpw(1);
y = xyzrpw(2);
z = xyzrpw(3);
rx = xyzrpw(4);
ry = xyzrpw(5);
rz = xyzrpw(6);

srx = sin(rx);
crx = cos(rx);
sry = sin(ry);
cry = cos(ry);
srz = sin(rz);
crz = cos(rz);

H=[             cry*crz,              -cry*srz,      sry, x;
  crx*srz + crz*srx*sry, crx*crz - srx*sry*srz, -cry*srx, y;
  srx*srz - crx*crz*sry, crz*srx + crx*sry*srz,  crx*cry, z;
                      0,                     0,        0, 1];
