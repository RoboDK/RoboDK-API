# This example shows how to quickly calculate the cycle time of a program
# as a function of the linear and joint speeds
#
# Important notes and tips for accurate cycle time calculation:
# https://robodk.com/doc/en/General.html#CycleTime

# Start the RoboDK API
from robolink import *  # RoboDK API

RDK = Robolink()

# Ask the user to select a program
program = RDK.ItemUserPick('Select a program (make sure the program does not change the robot speed)', ITEM_TYPE_PROGRAM)

# Retrieve the robot linked to the selected program
robot = program.getLink(ITEM_TYPE_ROBOT)

# Output the linear speed, joint speed and time (separated by tabs)
writeline = "Linear Speed (mm/s)\tJoint Speed (deg/s)\tCycle Time(s)"
print(writeline)
# Prepare an HTML message we can show to the user through the RoboDK API:
msg_html = "<table border=1><tr><td>" + writeline.replace('\t', '</td><td>') + "</td></tr>"

for speed_lin in [1, 5, 10, 20, 50, 100, 200, 500]:
    for speed_joints in [1, 5, 10, 20, 50, 100, 200, 500]:
        # Set the robot speed
        robot.setSpeed(speed_lin, speed_joints)

        # Update the program and retrieve updated information:
        # https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Item.Update
        result = program.Update()
        instructions, time, travel, ok, error = result

        # Print the information
        newline = "%.1f\t%.1f\t%.1f" % (speed_lin, speed_joints, time)
        print(newline)
        msg_html = msg_html + '<tr><td>' + newline.replace('\t', '</td><td>') + '</td></tr>'

msg_html = msg_html + '</table>'

RDK.ShowMessage(msg_html)
