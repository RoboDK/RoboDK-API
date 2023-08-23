from robodk import robolink
from robodk import robodialogs, robofileio

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

        objects = []

        for entity in doc.modelspace():
            print(entity.DXFTYPE)

            if entity.DXFTYPE not in ['LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'SPLINE']:
                continue

            entity_path = ezdxf.path.make_path(entity)
            #points = list(entity_path.flattening(2))
            points = [list(v.xyz) for v in entity_path.flattening(2)]
            objects.append(RDK.AddCurve(points))

        if len(objects) == 0:
            RDK.ShowMessage("No valid geometry found for: " + file_path, False)
            quit()

        dxf = RDK.MergeItems(objects)
        dxf.setName(robofileio.getFileName(file_path))
        #dxf.Scale(1000)

        RDK.ShowMessage("Done loading: " + file_path, False)

        RDK.Render(True)
        
    else:
        print("Invalid file:")
        print(file_path)

if __name__ == "__main__":
    LoadDXF()