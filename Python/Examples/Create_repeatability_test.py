# This macro can be used to schedule a repeatability test with RoboDK.
# There should be one or more targets (5 recommended) named like "ISO p1", "ISO p2", ... and the script
# will aucomatically schecule the repeatability and accuracy test using 30 cycles as stated by the ISO 9283 norm
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *    # API to communicate with robodk
from robodk import *      # basic matrix operations

# Initialise the RoboDK API
RDK = Robolink()

# Retrieve the TCP
tool_item = RDK.ItemUserPick("Select the TCP", ITEM_TYPE_TOOL)
if not tool_item.Valid():
    quit(0)

# Retrieve the validation project:
validation_project = RDK.ItemUserPick("Select the validation project", ITEM_TYPE_VALID_ISO9283)
if not validation_project.Valid():
    print("No calibration project selected or available")
    validation_project = RDK.ItemUserPick("Select the calibration project", ITEM_TYPE_CALIBPROJECT)
    if not validation_project.Valid():
        raise Exception("No calibration or validation projects selected or available")
    

# Retrieve the validation targets
measurement_list = []
tcp = Mat(tool_item.PoseTool().Pos())
count = 0
while True:
    count = count + 1
    ti = RDK.Item('ISO p%i' % count, ITEM_TYPE_TARGET)
    if not ti.Valid():
        break
    joints = Mat(ti.Joints())
    measurement_list.append(catV(joints, tcp))


# Build the validation sequence as 30 cycles
sequence = Mat(9,0)
for i in range(30):
    for j in range(len(measurement_list)):
        sequence = catH(sequence, measurement_list[j])

# Update the validation targets
#value = mbox('Do you want to use these targets for calibration or validation?', ('Calibration', 'CALIB_TARGETS'), ('Validation', 'VALID_TARGETS'))
validation_project.setValue('VALID_TARGETS', sequence)


