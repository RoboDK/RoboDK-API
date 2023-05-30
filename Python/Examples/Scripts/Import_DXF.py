from robodk import robolink
from robodk import robodk

import sys

robolink.import_install('ezdxf')
import ezdxf
from ezdxf import recover, path

# file_path = "C:\\Users\\RoboDK\\Downloads\\example.dxf"

file_path = robodk.getOpenFileName()

doc, auditor = ezdxf.recover.readfile(file_path)

RDK = robolink.Robolink()

RDK.ShowMessage("Loading DXF file: " + file_path, False)

RDK.Render(False)

objects = []
for entity in doc.modelspace():
    print(entity.DXFTYPE)

    if entity.DXFTYPE not in ['LINE', 'ARC', 'CIRCLE']:
        continue

    entity_path = ezdxf.path.make_path(entity)
    #points = list(entity_path.flattening(2))
    points = [list(v.xyz) for v in entity_path.flattening(2)]
    objects.append(RDK.AddCurve(points))

if len(objects) == 0:
    RDK.ShowMessage("No valid geometry found for: " + file_path, False)
    quit()

dxf = RDK.MergeItems(objects)
dxf.setName(robodk.getFileName(file_path))
# dxf.Scale(1000)

RDK.ShowMessage("Done loading: " + file_path, False)

RDK.Render(True)
