from robodk import robolink, robomath, robodialogs

from collections import OrderedDict
import sys
from pathlib import Path

robolink.import_install('ezdxf')  # >= 1.4.1

import ezdxf
from ezdxf import recover, path
from ezdxf.math import Matrix44
import math

DEFAULT_RESOLUTION = 0.001


def insert_transform(ins):
    """
    Compute the transformation matrix for a DXF INSERT entity.

    This includes scaling and rotation. Translation is excluded so that
    parent matrices can handle positioning recursively.

    :param ins: The INSERT entity from the DXF.
    :type ins: ezdxf.entities.Insert
    :return: Transformation matrix (excluding translation).
    :rtype: ezdxf.math.Matrix44
    """
    location = ins.dxf.insert
    rotation = ins.dxf.rotation
    xscale = getattr(ins.dxf, 'xscale', 1.0)
    yscale = getattr(ins.dxf, 'yscale', 1.0)
    zscale = getattr(ins.dxf, 'zscale', 1.0)
    return Matrix44.chain(
        Matrix44.scale(xscale, yscale, zscale),
        Matrix44.z_rotate(math.radians(rotation)),
        #Matrix44.translate(location.x, location.y, location.z),
    )


def traverse_entity(layout_or_block, parent_matrix=Matrix44(), factor_mm=1.0, resolution=DEFAULT_RESOLUTION):
    """
    Recursively traverse a DXF layout or block and extract geometry.

    This function handles nested INSERTs, applying cumulative transforms. Supported
    entity types include LINE, ARC, CIRCLE, LWPOLYLINE, SPLINE and POINT.

    :param layout_or_block: DXF layout or block to traverse.
    :type layout_or_block: ezdxf.layouts.Layout or ezdxf.blocks.BlockRecord
    :param parent_matrix: Transformation matrix accumulated from parent INSERTs.
    :type parent_matrix: ezdxf.math.Matrix44
    :param factor_mm: Unit scaling factor to convert to millimeters.
    :type factor_mm: float
    :return: List of tuples with (layer name, list of 3D points).
    :rtype: list[tuple[str, list[list[float]]]]
    """
    entities = []

    for entity in layout_or_block:
        dxftype = entity.dxftype()
        print(dxftype)

        if dxftype == 'INSERT':
            print(f"INSERT {entity.dxf.name} at {entity.dxf.insert}, rotation {entity.dxf.rotation}")

            block_name = entity.dxf.name
            if block_name not in entity.doc.blocks:
                return []

            m = parent_matrix @ insert_transform(entity)
            block = entity.doc.blocks[block_name]
            entities += traverse_entity(block, parent_matrix=m, factor_mm=factor_mm, resolution=resolution)

        elif dxftype in ['LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'SPLINE']:
            try:
                spath = path.make_path(entity)
                spath = spath.transform(parent_matrix)
                curve = [list(v.xyz) for v in spath.flattening(distance=resolution, segments=4)]

                if len(curve) > 0:
                    if factor_mm != 1.0:
                        curve = [robomath.mult3(p, factor_mm) for p in curve]

                    layer = str(entity.dxf.layer)
                    entities.append((layer, curve))

            except Exception as e:
                print(f"Skipped entity {entity.dxftype()}: {e}")

        elif dxftype in ['POINT']:
            try:
                location = entity.dxf.location
                curve = [[location.x, location.y, location.z]]

                if len(curve) > 0:
                    if factor_mm != 1.0:
                        curve = [robomath.mult3(p, factor_mm) for p in curve]

                    layer = str(entity.dxf.layer)
                    entities.append((layer, curve))

            except Exception as e:
                print(f"Skipped entity {entity.dxftype()}: {e}")

    return entities


def merge_connected_curves(curves, tol=0.001):
    """
    Merge open curves that are end-to-end connected within a distance tolerance.

    This detects continuous sequences of curves and joins them into a single curve,
    reversing point order when necessary to ensure smooth joining.
    Closed curves are preserved as-is.

    :param curves: List of curves, each defined by a list of 3D points.
    :type curves: list[list[list[float]]]
    :param tol: Distance tolerance for endpoint matching.
    :type tol: float
    :return: Curves with connected segments merged.
    :rtype: list[list[list[float]]]
    """
    closed_curves = []
    open_curves = []

    # Find closed vs. open forms in individual curves
    for curve in curves:
        if robomath.distance((curve[0])[:3], (curve[-1])[:3]) < tol:
            closed_curves.append(curve)
        else:
            open_curves.append(curve)

    # Find closed forms across multiple segments/curves (permutate)
    merged_curves = []
    while open_curves:
        base = open_curves.pop(0)
        merged = True
        while merged:
            merged = False
            for i, other in enumerate(open_curves):
                s1, e1 = base[0][:3], base[-1][:3]
                s2, e2 = other[0][:3], other[-1][:3]

                if robomath.distance(e1, e2) < tol:
                    base += other[-2::-1]  # reverse
                elif robomath.distance(s1, s2) < tol:
                    base = other[::-1] + base[1:]  # reverse
                elif robomath.distance(s1, e2) < tol:
                    base = other[:-1] + base
                elif robomath.distance(e1, s2) < tol:
                    base += other[1:]
                else:
                    continue

                del open_curves[i]
                merged = True
                break

        merged_curves.append(base)

    return closed_curves + merged_curves


def _is_closed(curve, tol=0.001):
    return robomath.distance(curve[0][:3], curve[-1][:3]) < tol


def _signed_area2d(points):
    xy = _xy_no_dup_last(points)
    a = 0.0
    n = len(xy)
    if n < 3:
        return 0.0
    for i in range(n):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return 0.5 * a  # >0 CCW, <0 CW


def _is_clockwise(points):
    return _signed_area2d(points) < 0.0


def _xy_no_dup_last(points):
    # Return list of (x,y) without duplicating the last point if equal to first
    if len(points) >= 2 and points[0][:2] == points[-1][:2]:
        pts = points[:-1]
    else:
        pts = points
    return [(p[0], p[1]) for p in pts]


def _bbox(points):
    xy = _xy_no_dup_last(points)
    if not xy:
        return 0.0, 0.0, 0.0, 0.0
    xs = [p[0] for p in xy]
    ys = [p[1] for p in xy]
    return min(xs), min(ys), max(xs), max(ys)


def _bbox_contains(inner_points, outer_points, tol=0.001):
    ix0, iy0, ix1, iy1 = _bbox(inner_points)
    ox0, oy0, ox1, oy1 = _bbox(outer_points)
    return (ix0 >= ox0 - tol and iy0 >= oy0 - tol and ix1 <= ox1 + tol and iy1 <= oy1 + tol)


def _orient_nested_curves(curves, tol=0.001):
    """
    For closed polygons only.
    Depth 0 (not inside any) -> clockwise.
    Depth 1 -> counterclockwise.
    Depth 2 -> clockwise. And so on.
    """
    # Separate closed from open
    closed = []
    open_curves = []
    for c in curves:
        if _is_closed(c, tol):
            closed.append(c)
        else:
            open_curves.append(c)

    if not closed:
        return curves

    # Build containment depth for each closed polygon using bounding boxes
    depths = []
    for i, pi in enumerate(closed):
        depth = 0
        for j, pj in enumerate(closed):
            if i == j:
                continue
            if _bbox_contains(pi, pj, tol):
                depth += 1
        depths.append(depth)

    # Reorient based on depth parity
    reoriented_closed = []
    for poly, depth in zip(closed, depths):
        should_be_cw = (depth % 2 == 0)  # even depth
        is_cw = _is_clockwise(poly)
        if should_be_cw != is_cw:
            poly = poly[::-1]
        reoriented_closed.append(poly)

    return reoriented_closed + open_curves


def LoadDXF(file_path=None, merge_continuous_segments=True, resolution=DEFAULT_RESOLUTION, orient_closed_curves=False, create_machining_project=False):
    """
    Load a DXF file, extract geometry, and import it into RoboDK.

    This supports recursive block resolution, unit scaling, and optional merging of
    connected segments. Geometry is grouped by DXF layer and imported accordingly.

    :param file_path: Path to the DXF file. If None, prompts the user.
    :type file_path: str or None
    :param merge_continuous_segments: Whether to merge connected curves. If None, user is prompted.
    :type merge_continuous_segments: bool or None
    :param resolution: Segment resolution. If None, user is prompted.
    :type resolution: bool or None
    :param orient_closed_curves: Make outermost closed curves clockwise and alternate by nesting depth. If None, user is prompted.
    :type orient_closed_curves: bool or None
    :param create_machining_project: Create a Curve Follow Project after importation. If None, user is prompted.
    :type create_machining_project: bool or None
    :return: The main RoboDK object created from the DXF, or None on failure.
    :rtype: robolink.Item or None
    """
    if not file_path and len(sys.argv) >= 2:
        file_path = sys.argv[1]
        
    if len(sys.argv) >= 3:
        if "-SkipInput" in sys.argv[2:]:
            if resolution is None:
                resolution = DEFAULT_RESOLUTION
                orient_closed_curves = False
                create_machining_project = False
                
            
    if not file_path or not Path(file_path).is_file():
        file_path = robodialogs.getOpenFileName(defaultextension='.dxf', filetypes=[('DXF files', '.DXF .dxf')])

    if not file_path or not Path(file_path).is_file():
        print("Invalid file:")
        print(file_path)
        RDK.ShowMessage("Could not open the provided DXF file.\n"
                        "Please check the file path and try again.")
        return None

    RDK = robolink.Robolink()
    RDK.ShowMessage("Loading DXF file: " + file_path, False)

    if resolution is None:
        resolution = robodialogs.InputDialog("Specify the segment resolution", DEFAULT_RESOLUTION + 1e-10)
        if resolution is None:
            RDK.ShowMessage("Operation cancelled")
            return None

    doc, auditor = ezdxf.recover.readfile(file_path)
    factor_mm = ezdxf.units.conversion_factor(doc.units, 4) if doc.units > 0 else 1.0

    entities = traverse_entity(doc.modelspace(), factor_mm=factor_mm, resolution=resolution)
    layer_objects = OrderedDict()
    for layer, curve in entities:
        layer_objects.setdefault(layer, []).append(curve)

    if len(layer_objects) == 0:
        RDK.ShowMessage("No valid geometry found for: " + file_path, False)
        return None

    if merge_continuous_segments is None:
        merge_continuous_segments = robodialogs.ShowMessageYesNo("Do you want to merge connected curve segments into continuous contours?\n"
                                                                 "This can help simplify geometry, but it may reverse the direction of some curves.")

    if orient_closed_curves is None:
        orient_closed_curves = robodialogs.ShowMessageYesNo("Do you want to make nested closed curves consistent? Outer clockwise, inner counterclockwise.")

    if create_machining_project is None:
        create_machining_project = robodialogs.ShowMessageYesNo("Do you want to create a Curve Follow Project after import?")

    RDK.Render(False)

    objects = []
    base_name = Path(file_path).stem
    for layer, curves in layer_objects.items():
        layer_objects = []

        if merge_continuous_segments:
            curves = merge_connected_curves(curves)

        if orient_closed_curves:
            curves = _orient_nested_curves(curves)

        # Import in RoboDK
        for curve in curves:
            if len(curve) == 1:
                layer_objects.append(RDK.AddPoints(curve))
            else:
                layer_objects.append(RDK.AddCurve(curve))
            layer_objects[-1].setVisible(False)
            layer_objects[-1].setVisible(True)  # Force toggle from Object to Curve Object
        dxf = RDK.MergeItems(layer_objects)
        dxf.setName(base_name + " - " + layer)
        dxf.setVisible(False)  # Force toggle from Object to Curve Object
        dxf.setVisible(True)
        objects.append(dxf)

    RDK.Render(True)

    if len(objects) > 1:
        if robodialogs.ShowMessageYesNo("Multiple layers or shapes were imported.\n"
                                        "Do you want to merge them into a single object in RoboDK?"):
            RDK.Render(False)
            dxf = RDK.MergeItems(objects)
            dxf.setName(base_name)
            RDK.Render(True)

    RDK.ShowMessage("Done loading: " + file_path, False)

    if create_machining_project:
        RDK.Render(False)
        cfp = RDK.AddMachiningProject(dxf.Name())
        cfp.setMachiningParameters(part=dxf, params="ReorderAuto=0")
        RDK.Render(True)

    return dxf


if __name__ == "__main__":
    LoadDXF(merge_continuous_segments=True, resolution=None, orient_closed_curves=None, create_machining_project=None)
