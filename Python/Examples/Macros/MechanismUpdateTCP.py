# Cette macro permet de mettre a jour le TCP d'un robot defini par un mecanisme
#
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station

# Imposer le nom du mecanisme (existant ou nouveau)
NOM_TCP_MOBILE = 'TCP Mecanisme'

# Option pour garder le TCP a jour en permanence
MISE_A_JOUR_PERMANENTE = True

#--------------------------------------------------
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox

RDK = Robolink()

mecanisme = None

# Extraire le premier mecanisme de moins de 3 axes attache a un robot
robot_list = RDK.ItemList(ITEM_TYPE_ROBOT)
for r in robot_list:
    if len(r.Joints().list()) <= 3 and r.Parent().Type() == ITEM_TYPE_ROBOT:
        mecanisme = r

if not mecanisme:
    raise Exception("Mecanisme pas trouve")

robot = mecanisme.Parent()
if not robot.Valid() or robot.Type() != ITEM_TYPE_ROBOT:
    raise Exception("Le mecanisme " + mecanisme.Name() + " n'est pas attache a un robot")

# Extraire le TCP existant, s'il y a lieu, ou en créer un de nouveau
tcp = RDK.Item(NOM_TCP_MOBILE, ITEM_TYPE_TOOL)
if not tcp.Valid():
    tcp = robot.AddTool(eye(4), NOM_TCP_MOBILE)

# Boucle infini pour garder le TCP à jour:
while True:
    # Extraire la position absolue du flange robot
    robot_flange_abs = robot.PoseAbs() * robot.SolveFK(robot.Joints())
    # Extraire la position absolue du flange mecanisme
    mechanisme_flange_abs = mecanisme.PoseAbs() * mecanisme.SolveFK(mecanisme.Joints())

    # Calculer le TCP (relation entre les 2 derniers)
    pose_tcp = invH(robot_flange_abs) * mechanisme_flange_abs

    # Mettre à jour le TCP
    tcp.setPoseTool(pose_tcp)

    # Arreter a la premiere iteration:
    if not MISE_A_JOUR_PERMANENTE:
        break
