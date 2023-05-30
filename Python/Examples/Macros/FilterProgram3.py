# Example to reorder instructions
# Test with Example-01.a

from robolink import *

RDK = Robolink()

p1 = RDK.Item("ApproachMove", ITEM_TYPE_PROGRAM)
p2 = RDK.Item("PaintTop", ITEM_TYPE_PROGRAM)

program_from = p1
program_to = p1 # this can be a different program as well
instruction_id_from = 2
instruction_id_to = 0

# Choose if you want to reorder before or after
reorder_cmd = "ReorderBefore"
#reorder_cmd = "ReorderAfter"

# Warning: This can crash if id's are not valid
program_from.setParam(reorder_cmd, str(instruction_id_from) + "|" + str(instruction_id_to) + "|" + str(program_to.item))
