from robodk import robolink, robomath, robodialogs

from collections import OrderedDict
import sys
from pathlib import Path

robolink.import_install('ezdxf')  # >= 1.4.1

import ezdxf
from ezdxf import recover, path


def LoadDXF(file_path=None):
    if not file_path and len(sys.argv) >= 2:
        file_path = sys.argv[1]

    if not file_path or not Path(file_path).is_file():
        file_path = robodialogs.getOpenFileName(defaultextension='.dxf', filetypes=[('DXF files', '.DXF .dxf')])

    if not file_path or not Path(file_path).is_file():
        print("Invalid file:")
        print(file_path)
        return

    RDK = robolink.Robolink()
    RDK.ShowMessage("Loading DXF file: " + file_path, False)

    doc, auditor = ezdxf.recover.readfile(file_path)
    factor_mm = ezdxf.units.conversion_factor(doc.units, 4) if doc.units > 0 else 1.0

    layer_objects = OrderedDict()
    for entity in doc.modelspace():
        print(entity.DXFTYPE)

        if entity.DXFTYPE not in ['LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'SPLINE']:
            continue

        entity_path = ezdxf.path.make_path(entity)
        curve = [list(v.xyz) for v in entity_path.flattening(2)]
        if len(curve) == 0:
            continue

        if factor_mm != 1.0:
            curve = [robomath.mult3(list(point), factor_mm) for point in curve]

        if not str(entity.dxf.layer) in layer_objects:
            layer_objects[str(entity.dxf.layer)] = []
        layer_objects[str(entity.dxf.layer)].append(curve)

    if len(layer_objects) == 0:
        RDK.ShowMessage("No valid geometry found for: " + file_path, False)
        return

    RDK.Render(False)

    objects = []
    base_name = Path(file_path).stem
    for layer, curves in layer_objects.items():
        layer_objects = []
        for curve in curves:
            layer_objects.append(RDK.AddCurve(curve))
        dxf = RDK.MergeItems(layer_objects)
        dxf.setName(base_name + " - " + layer)
        objects.append(dxf)

    RDK.Render(True)

    if len(objects) > 1:
        if robodialogs.ShowMessageYesNo("Merge into one single object?"):
            RDK.Render(False)
            dxf = RDK.MergeItems(objects)
            dxf.setName(base_name)
            RDK.Render(True)

    RDK.ShowMessage("Done loading: " + file_path, False)


if __name__ == "__main__":
    LoadDXF()
