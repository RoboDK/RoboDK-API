# Viewport demonstration Script for RoboDK
# 
# This script investigates the relationship between window size and 3D viewport size
# in different window modes. The goal is to understand what offsets are needed when
# embedding RoboDK into an external application (e.g., Electron via Win32 SetParent).
# 
# PROBLEM:
# When embedding RoboDK and hiding UI elements via setFlagsRoboDK(), the 3D viewport
# does not fill the entire client area. Qt's layout reserves space for hidden dock
# widgets, creating gaps that require compensation.
# 
# We need API access to the actual viewport rectangle (position + size) to properly
# position the embedded window.
# 
# CONTEXT - Embedding vs This Script:
# - In actual embedding: SetParent + WS_CHILD removes title bar, window is a child
# - In this script: No reparenting, title bar visible, demonstrates Size3D behavior
# - The Qt layout gaps are the same in both cases
# 
# REQUESTED API:
# We need a way to get the 3D viewport rectangle in screen/pixel coordinates:
#   - Position (x, y) relative to window client area origin
#   - Size (width, height) matching Win32 coordinate system
# 
# Proposed command: "ViewportRect" or "Viewport3D_Rect"
# Expected format: "x,y,width,height" (e.g., "250,75,1920,1080")
# 
# Run this script with RoboDK open, or it will start a new instance.
# 

import time
import ctypes
from ctypes import wintypes
from robodk.robolink import *

# Win32 API for window geometry
user32 = ctypes.windll.user32

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


def get_window_rect(hwnd):
    """Get window rect in screen coordinates (includes frame)."""
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return {
        'x': rect.left,
        'y': rect.top,
        'width': rect.right - rect.left,
        'height': rect.bottom - rect.top,
    }


def get_client_rect(hwnd):
    """Get client area size (excludes frame, position is always 0,0)."""
    rect = RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    return {
        'width': rect.right,
        'height': rect.bottom,
    }


def get_client_origin(hwnd):
    """Get client area origin in screen coordinates."""
    point = POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(point))
    return {'x': point.x, 'y': point.y}


def get_size3d(RDK):
    """Get the 3D view size using the Size3D command.
     Size3D is likely the OpenGL framebuffer size, not widget size
     """
    result = RDK.Command("Size3D")
    # Parse "WIDTHxHEIGHT" format
    try:
        parts = result.strip().split('x')
        return int(parts[0]), int(parts[1])
    except:
        return None, None


def get_window_rect_robodk(RDK):
    """
    PROPOSED API: Get the main window rectangle in screen coordinates.

    Expected command: RDK.Command("WindowRect") or RDK.Command("MainWindow_Rect")
    Expected return: "x,y,width,height" in screen pixels

    Example return value: "-7,-7,2766,1118"
    - x, y: window origin in screen coordinates (can be negative when maximized)
    - width, height: total window size including frame/title bar

    This should match Win32 GetWindowRect() for cross-platform consistency.
    """
    # TODO: Uncomment when RoboDK implements this API
    result = RDK.Command("WindowRect")
    try:
        parts = result.strip().split(',')
        return {
            'x': int(parts[0]),
            'y': int(parts[1]),
            'width': int(parts[2]),
            'height': int(parts[3]),
        }
    except:
        return None
    
    return None  # Not yet implemented


def get_client_rect_robodk(RDK):
    """
    PROPOSED API: Get the client area rectangle.

    Expected command: RDK.Command("ClientRect") or RDK.Command("ClientArea")
    Expected return: "x,y,width,height" where x,y is client origin in screen coords

    Example return value: "0,23,2752,1080"
    - x, y: client area origin in screen coordinates
    - width, height: client area size (excludes window frame/title bar)

    This should match Win32 GetClientRect() + ClientToScreen() for consistency.
    """
    # TODO: Uncomment when RoboDK implements this API
    result = RDK.Command("ClientRect")
    try:
        parts = result.strip().split(',')
        return {
            'x': int(parts[0]),
            'y': int(parts[1]),
            'width': int(parts[2]),
            'height': int(parts[3]),
        }
    except:
        return None
    
    return None  # Not yet implemented


def get_viewport_rect(RDK):
    """
    PROPOSED API: Get the 3D viewport rectangle relative to client area.

    Expected command: RDK.Command("ViewportRect") or RDK.Command("Viewport3D_Rect")
    Expected return: "x,y,width,height" in pixels relative to client area origin

    Example return value: "250,75,1920,1080"
    - x=250: viewport starts 250px from left (tree panel width)
    - y=75: viewport starts 75px from top (menu + toolbar height)
    - width=1920: viewport width in pixels
    - height=1080: viewport height in pixels

    The width,height should match Size3D when in the same coordinate system (with a 1:1 OpenGL buffer)
    """
    # TODO: Uncomment when RoboDK implements this API
    result = RDK.Command("ViewportRect")
    try:
        parts = result.strip().split(',')
        return {
            'x': int(parts[0]),
            'y': int(parts[1]),
            'width': int(parts[2]),
            'height': int(parts[3]),
        }
    except:
        return None
    return None  # Not yet implemented


def get_window_id(RDK):
    """Get the main window handle."""
    while True:
        # IMPORTANT! Robolink() returns before the MainWindow_ID is ready, while QtMainWinID si ready right away!
        qt_id = RDK.Command("QtMainWinID")
        main_id = RDK.Command("MainWindow_ID")
        if qt_id.isdigit() and main_id.isdigit():
            break
    return qt_id, main_id


def print_separator(title=''):
    print(f"\n{'='*60}")
    if title:
        print(f"  {title}")
        print('='*60)


def investigate_mode(RDK, hwnd, mode_name, setup_func):
    """Investigate viewport in a specific mode."""
    print_separator(mode_name)

    setup_func()
    time.sleep(1.0)  # Let RoboDK apply window state changes

    # Win32 window geometry (reference implementation)
    win32_window = get_window_rect(hwnd)
    win32_client = get_client_rect(hwnd)
    win32_client_origin = get_client_origin(hwnd)

    # RoboDK current API
    size3d_w, size3d_h = get_size3d(RDK)

    # RoboDK proposed APIs (not yet implemented)
    rdk_window = get_window_rect_robodk(RDK)
    rdk_client = get_client_rect_robodk(RDK)
    rdk_viewport = get_viewport_rect(RDK)

    # Print Win32 reference values
    print(f"Win32 Window:      origin=({win32_window['x']}, {win32_window['y']})  size={win32_window['width']}x{win32_window['height']}")
    print(f"Win32 Client:      origin=({win32_client_origin['x']}, {win32_client_origin['y']})  size={win32_client['width']}x{win32_client['height']}")

    # Print RoboDK proposed API values (or placeholders)
    if rdk_window:
        print(f"RoboDK WindowRect: origin=({rdk_window['x']}, {rdk_window['y']})  size={rdk_window['width']}x{rdk_window['height']}")
        # Validate against Win32
        if rdk_window != win32_window:
            print(f"  WARNING: WindowRect doesn't match Win32!")
    else:
        print(f"RoboDK WindowRect: NOT IMPLEMENTED (should match Win32 Window)")

    if rdk_client:
        print(f"RoboDK ClientRect: origin=({rdk_client['x']}, {rdk_client['y']})  size={rdk_client['width']}x{rdk_client['height']}")
    else:
        print(f"RoboDK ClientRect: NOT IMPLEMENTED (should match Win32 Client)")

    # Print current Size3D and proposed ViewportRect
    print(f"RoboDK Size3D:     {size3d_w} x {size3d_h}")

    if rdk_viewport:
        print(f"RoboDK ViewportRect: origin=({rdk_viewport['x']}, {rdk_viewport['y']})  size={rdk_viewport['width']}x{rdk_viewport['height']}")
    else:
        print(f"RoboDK ViewportRect: NOT IMPLEMENTED (viewport position + size in client coords)")

    return {
        'win32_window': win32_window,
        'win32_client': win32_client,
        'win32_client_origin': win32_client_origin,
        'size3d': (size3d_w, size3d_h),
        'rdk_window': rdk_window,
        'rdk_client': rdk_client,
        'rdk_viewport': rdk_viewport,
    }


def main():
    print("Viewport Investigation Script")
    print("This script tests current behavior and validates proposed API additions.")
    print_separator()

    # Connect to RoboDK, default
    RDK = Robolink()

    # Get window handles
    qt_id, main_id = get_window_id(RDK)
    hwnd = int(main_id)  # Use MainWindow_ID for Win32 calls

    print(f"\nWindow Handles:")
    print(f"  QtMainWinID:   {qt_id}")
    print(f"  MainWindow_ID: {main_id}") # Same values? but QtMainWinID is ready on start while MainWindow_ID needs a while loop..

    # Store results
    results = {}

    # Mode 1: Normal window with all UI
    def setup_normal():
        RDK.setWindowState(WINDOWSTATE_NORMAL)
        RDK.setFlagsRoboDK(FLAG_ROBODK_ALL)
        RDK.Command("ToolbarLayout", "Complete")

    results['normal'] = investigate_mode(RDK, hwnd, "MODE 1: Normal Window (with all UI)", setup_normal)

    # Mode 2: Maximized window with all UI
    def setup_maximized():
        RDK.setWindowState(WINDOWSTATE_MAXIMIZED)
        RDK.setFlagsRoboDK(FLAG_ROBODK_ALL)
        RDK.Command("ToolbarLayout", "Complete")

    results['maximized'] = investigate_mode(RDK, hwnd, "MODE 2: Maximized Window (with all UI)", setup_maximized)

    # Mode 3: Maximized with soft cinema (UI hidden via flags)
    # This is the mode we use for embedding - hides UI but keeps window frame
    #
    # NOTE: For accurate results, disable all Apps in Tools > Add-in Manager.
    #       Active Apps add toolbars that affect viewport size.
    #
    def setup_soft_cinema():
        RDK.setWindowState(WINDOWSTATE_FULLSCREEN)
        # Minimal flags - just 3D view active with interaction
        minimal_flags = (
            FLAG_ROBODK_3DVIEW_ACTIVE |
            FLAG_ROBODK_LEFT_CLICK |
            FLAG_ROBODK_RIGHT_CLICK |
            FLAG_ROBODK_DOUBLE_CLICK |
            FLAG_ROBODK_WINDOWKEYS_ACTIVE
        )
        RDK.setFlagsRoboDK(minimal_flags)
        RDK.Command("ToolbarLayout", "None")

    results['soft_cinema'] = investigate_mode(RDK, hwnd, "MODE 3: Soft Cinema (UI hidden via flags) - EMBEDDING MODE", setup_soft_cinema)

    # Mode 4: RoboDK Cinema
    def setup_cinema():
        RDK.setFlagsRoboDK(FLAG_ROBODK_ALL)  # reset
        RDK.Command("ToolbarLayout", "Complete")  # reset
        RDK.setWindowState(WINDOWSTATE_CINEMA)  # let RoboDK handle flags

    results['cinema'] = investigate_mode(RDK, hwnd, "MODE 4: Cinema", setup_cinema)

    # Mode 5: RoboDK Full Screen Cinema
    def setup_cinema_fullscreen():
        RDK.setFlagsRoboDK(FLAG_ROBODK_ALL)  # reset
        RDK.Command("ToolbarLayout", "Complete")  # reset
        RDK.setWindowState(WINDOWSTATE_FULLSCREEN_CINEMA)  # let RoboDK handle flags

    results['cinema_fs'] = investigate_mode(RDK, hwnd, "MODE 5: Cinema Fullscreen", setup_cinema_fullscreen)

    # Summary
    print_separator("SUMMARY - Size Comparison")

    print("\n              Win32 Client     RoboDK Size3D    Gap (Client - Size3D)")
    print("              -------------    -------------    ---------------------")
    for mode, data in results.items():
        client = data['win32_client']
        size3d = data['size3d']
        gap_w = client['width'] - size3d[0] if size3d[0] else 'N/A'
        gap_h = client['height'] - size3d[1] if size3d[1] else 'N/A'
        print(f"  {mode:12} {client['width']:4}x{client['height']:<4}         {size3d[0]}x{size3d[1]}        {gap_w}, {gap_h}")

    print_separator("PROPOSED API SUMMARY")
    print("""
Three new commands are requested for embedding support:

1. RDK.Command("WindowRect")
   Returns: "x,y,width,height" - window rect in screen coordinates
   Should match: Win32 GetWindowRect()

2. RDK.Command("ClientRect")
   Returns: "x,y,width,height" - client area with origin in screen coordinates
   Should match: Win32 GetClientRect() + ClientToScreen()

3. RDK.Command("ViewportRect")
   Returns: "x,y,width,height" - 3D viewport relative to client area
   This is the key one for embedding - tells us where the 3D view is!

Note: Size3D returns values larger than Win32 client rect (see gap column).
      This suggests Size3D uses a different coordinate system (DPI scaled?).
      ViewportRect should use the same coordinate system as ClientRect.
""")

    # Validation test for proposed APIs
    print_separator("VALIDATION TEST - Proposed APIs")

    # First reset from cinema mode, then set up soft cinema
    setup_normal()
    time.sleep(0.5)
    setup_soft_cinema()
    time.sleep(1.0)  # Let RoboDK apply window state changes

    # Get Win32 reference values
    win32_window = get_window_rect(hwnd)
    win32_client = get_client_rect(hwnd)
    win32_client_origin = get_client_origin(hwnd)

    # Get proposed RoboDK API values
    rdk_window = get_window_rect_robodk(RDK)
    rdk_client = get_client_rect_robodk(RDK)
    rdk_viewport = get_viewport_rect(RDK)

    print("Testing in SOFT CINEMA mode (embedding scenario):\n")

    # Test 1: WindowRect
    print("1. WindowRect API:")
    if rdk_window:
        match = (rdk_window['x'] == win32_window['x'] and
                 rdk_window['y'] == win32_window['y'] and
                 rdk_window['width'] == win32_window['width'] and
                 rdk_window['height'] == win32_window['height'])
        if match:
            print(f"   PASS - Matches Win32: ({rdk_window['x']}, {rdk_window['y']}) {rdk_window['width']}x{rdk_window['height']}")
        else:
            print(f"   FAIL - Mismatch!")
            print(f"     RoboDK: ({rdk_window['x']}, {rdk_window['y']}) {rdk_window['width']}x{rdk_window['height']}")
            print(f"     Win32:  ({win32_window['x']}, {win32_window['y']}) {win32_window['width']}x{win32_window['height']}")
    else:
        print(f"   NOT IMPLEMENTED")
        print(f"   Expected: ({win32_window['x']}, {win32_window['y']}) {win32_window['width']}x{win32_window['height']}")

    # Test 2: ClientRect
    print("\n2. ClientRect API:")
    if rdk_client:
        match = (rdk_client['x'] == win32_client_origin['x'] and
                 rdk_client['y'] == win32_client_origin['y'] and
                 rdk_client['width'] == win32_client['width'] and
                 rdk_client['height'] == win32_client['height'])
        if match:
            print(f"   PASS - Matches Win32: ({rdk_client['x']}, {rdk_client['y']}) {rdk_client['width']}x{rdk_client['height']}")
        else:
            print(f"   FAIL - Mismatch!")
            print(f"     RoboDK: ({rdk_client['x']}, {rdk_client['y']}) {rdk_client['width']}x{rdk_client['height']}")
            print(f"     Win32:  ({win32_client_origin['x']}, {win32_client_origin['y']}) {win32_client['width']}x{win32_client['height']}")
    else:
        print(f"   NOT IMPLEMENTED")
        print(f"   Expected: ({win32_client_origin['x']}, {win32_client_origin['y']}) {win32_client['width']}x{win32_client['height']}")

    # Test 3: ViewportRect
    print("\n3. ViewportRect API:")
    if rdk_viewport:
        errors = []

        # Check viewport fits within client area
        if rdk_viewport['x'] < 0:
            errors.append(f"x ({rdk_viewport['x']}) should be >= 0")
        if rdk_viewport['y'] < 0:
            errors.append(f"y ({rdk_viewport['y']}) should be >= 0")
        if rdk_viewport['x'] + rdk_viewport['width'] > win32_client['width']:
            errors.append(f"right edge exceeds client width")
        if rdk_viewport['y'] + rdk_viewport['height'] > win32_client['height']:
            errors.append(f"bottom edge exceeds client height")

        if errors:
            print("   FAIL - Invalid values:")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"   PASS - Valid viewport rect")
            print(f"   Viewport: ({rdk_viewport['x']}, {rdk_viewport['y']}) {rdk_viewport['width']}x{rdk_viewport['height']}")
            print(f"   Margins: left={rdk_viewport['x']}, top={rdk_viewport['y']}, ", end="")
            print(f"right={win32_client['width'] - rdk_viewport['x'] - rdk_viewport['width']}, ", end="")
            print(f"bottom={win32_client['height'] - rdk_viewport['y'] - rdk_viewport['height']}")
    else:
        print(f"   NOT IMPLEMENTED")
        print(f"   Expected: (x, y, width, height) where viewport fits within client area")
        print(f"   In soft cinema mode, viewport should nearly fill the {win32_client['width']}x{win32_client['height']} client area")

    # Restore normal state
    print_separator()
    print("Restoring normal window state...")
    setup_normal()

    print("\nDone!")


if __name__ == "__main__":
    main()
