from robodk import robolink
from robodk import robodialogs, robofileio
from collections import OrderedDict


import sys
from pathlib import Path

robolink.import_install('ezdxf')

import ezdxf
from ezdxf import recover, path

def LoadDXF(file_path=None):
    # file_path = "C:\\Users\\RoboDK\\Downloads\\example.dxf"
    # file_path = None
    if file_path is None and len(sys.argv) >= 2:
        file_path = sys.argv[1]

    if file_path is None:
        file_path = robodialogs.getOpenFileName(filetypes=[('DXF files', '.DXF .dxf')])

    if Path(str(file_path)).is_file() :

        doc, auditor = ezdxf.recover.readfile(file_path)

        RDK = robolink.Robolink()

        RDK.ShowMessage("Loading DXF file: " + file_path, False)

        RDK.Render(False)

        layer_objects = OrderedDict()

        for entity in doc.modelspace():
            print(entity.DXFTYPE)

            if entity.DXFTYPE not in ['LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'SPLINE']:
                continue

            entity_path = ezdxf.path.make_path(entity)
            #points = list(entity_path.flattening(2))
            points = [list(v.xyz) for v in entity_path.flattening(2)]
            if len(points) == 0:
                continue

            if not entity.dxf.layer in layer_objects:
                layer_objects[entity.dxf.layer] = []

            curve = RDK.AddCurve(points)
            layer_objects[entity.dxf.layer].append(curve)

        if len(layer_objects) == 0:
            RDK.ShowMessage("No valid geometry found for: " + file_path, False)
            quit()

        fname = robofileio.getFileName(file_path)
        for k, v in layer_objects.items():
            dxf = RDK.MergeItems(v)
            dxf.setName(fname+"-"+k)
        #dxf.Scale(1000)

        RDK.ShowMessage("Done loading: " + file_path, False)

        RDK.Render(True)
        
    else:
        print("Invalid file:")
        print(file_path)

if __name__ == "__main__":
    LoadDXF()