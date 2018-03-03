% Convert a 4x4 pose to [x,y,z,rX,rY,rZ] (mm and rad) Euler format.
% The Euler conversion used is the same one used by Staubli controllers (using radians instead of degrees).
function xyzwpr = Pose_2_XYZRPW(T)

x = T(1,4);
y = T(2,4);
z = T(3,4);

a = T(1,1);
b = T(1,2);
c = T(1,3);
d = T(2,3);
e = T(3,3);

if c == 1
    ry1 = pi/2;
    rx1 = 0;
    rz1 = atan2(T(2,1),T(2,2));
elseif c== -1
    ry1 = -pi/2;
    rx1 = 0;
    rz1 = atan2(T(2,1),T(2,2));
else
    sy=c;
    cy1=+sqrt(1-sy^2);
%     cy2=-sqrt(1-sy^2);

    sx1=-d/cy1;
    cx1=e/cy1;

    sz1=-b/cy1;
    cz1=a/cy1;

%     sx2=-d/cy2;
%     cx2=e/cy2;
% 
%     sz2=-b/cy2;
%     cz2=a/cy2;

    rx1 = atan2(sx1,cx1);
%     rx2 = atan2(sx2,cx2);

    ry1 = atan2(sy,cy1);
%     ry2 = atan2(sy,cy2);

    rz1 = atan2(sz1,cz1);
%     rz2 = atan2(sz2,cz2);
end

xyzwpr = [x;y;z;rx1;ry1;rz1];