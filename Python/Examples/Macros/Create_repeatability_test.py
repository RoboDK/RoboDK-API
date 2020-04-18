# This macro can be used to schedule a repeatability test with RoboDK.
# There should be one or more targets (5 recommended) named like "ISO p1", "ISO p2", ... and the script
# will aucomatically schecule the repeatability and accuracy test using 30 cycles as stated by the ISO 9283 norm
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

# Set to True for unidirectional repeatability (ISO9283 norm)
# Set to False for multi directional repeatability (random order)
UNIDIRECTIONAL_REPEATABILITY = True


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

# Number of targets (ISO9283 is 5 targets)
n_targets = len(measurement_list)

# Function to create a normal array or a  random order
def GetOrderArray(np, make_random=False):
    import random
    array = list(range(np))
    if not make_random:
        return array

    for i in range(100):
        id1 = random.randrange(np)
        id2 = random.randrange(np)
        val1 = array[id1]
        array[id1] = array[id2]
        array[id2] = val1

    return array
        
# First iteration is in order
# Second iteration and so on is not in order if UNIDIRECTIONAL_REPEATABILITY is False:
for i in range(0,30):
    array_ids = GetOrderArray(n_targets, i > 0 and not UNIDIRECTIONAL_REPEATABILITY)
    for j in range(n_targets):
        jid = array_ids[j]
        sequence = catH(sequence, measurement_list[jid])


# Update the validation targets
#value = mbox('Do you want to use these targets for calibration or validation?', ('Calibration', 'CALIB_TARGETS'), ('Validation', 'VALID_TARGETS'))
validation_project.setValue('VALID_TARGETS', sequence)


RDK.ShowMessage("Measurements loaded", False)