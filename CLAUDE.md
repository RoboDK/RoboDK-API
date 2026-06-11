# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Multi-language implementation of the RoboDK API for simulating and offline-programming industrial robots. The API communicates with the RoboDK desktop application via a TCP socket (default port 20500). Every language implements the same three core abstractions:

- **`Robolink`** — session/connection manager; entry point for all API calls
- **`Item`** — any node in the RoboDK station tree (robot, frame, tool, target, object, program, …)
- **`Mat`** — 4×4 homogeneous transformation matrix representing a pose (position + orientation)

The Python package (`robodk`) is the reference implementation and is the most complete. All other languages mirror its API naming.

## Languages and Build Commands

### Python (`/Python`)

```bash
# Install (development)
pip install -e Python/

# Install with optional extras
pip install robodk[cv,apps,lint]

# Run all unit tests (RoboDK must be running with the matching .rdk station open)
cd Python/tests
python -m unittest -v

# Run a specific test module
python -m nose2 test_RobotSim6Axes

# Lint a script
pylint --load-plugins=pylint_robodk <script.py>
```

Test dependencies: `pip install nose2 nose2-html-report parameterized`

The test `.cmd` files in `Python/tests/` show which `.rdk` station each test suite requires (e.g. `Robot_2TCP.rdk`, `Robot7_2TCP.rdk`).

### TypeScript/JavaScript (`/TypeScript`)

```bash
cd TypeScript
npm install
npm run build   # tsc → dist/
npm test        # build + node --test
```

### C++ (`/C++`)

Requires Qt (Open Source or Commercial). Either:

- Include `robodk_api.h` / `robodk_api.cpp` directly in a Qt project, or
- Build as a static library via CMake:

```bash
cd C++
mkdir build && cd build
cmake ..
cmake --build .
```

### C# (`/C#`)

Open in Visual Studio (.NET ≥ 2.0). Two integration options:
- Include `C#/Example/RoboDK.cs` directly (Python-based naming)
- Install the NuGet package from `C#/API/` (C# conventions with interfaces)

### MATLAB (`/Matlab`)

Standalone `.m` files — no build step. Add the `/Matlab` directory to the MATLAB path.

## Python Package Structure

```
Python/
  robodk/
    robolink.py      # Robolink + Item classes; TCP socket protocol
    robomath.py      # Pose math (Mat class, rotations, Euler conversions)
    robodialogs.py   # UI dialogs (open/save file, message prompts)
    robofileio.py    # CSV, FTP, file utilities
    roboapps.py      # App Loader plug-in framework
    robolinkutils.py # Helpers built on top of robolink
  robolink/          # Thin re-export package (legacy compatibility)
  pylint_robodk/     # Pylint plugin for RoboDK-aware linting
  tests/             # unittest suite (requires a live RoboDK instance)
  Examples/          # 200+ standalone scripts
```

## Key Conventions

**Pose representation:** All positions/orientations are 4×4 matrices (`Mat`). Euler angles (XYZRPW and robot-vendor variants like KUKA, Fanuc) are converted to/from `Mat` via helpers in `robomath.py`.

**Item types:** Constants prefixed `ITEM_TYPE_` (e.g. `ITEM_TYPE_ROBOT`, `ITEM_TYPE_FRAME`) are defined in `robolink.py` and used to filter `Robolink.Item()` and `Robolink.ItemList()` calls.

**Run modes:** `RUNMODE_SIMULATE` (default), `RUNMODE_MAKE_ROBOTPROG` (generate offline program), `RUNMODE_RUN_ROBOT` (control real robot). Set via `RDK.setRunMode()`.

**Movement types:** `MoveJ` (joint), `MoveL` (linear), `MoveC` (circular arc) — same method names across all languages.

**TypeScript async:** All I/O methods return `Promise`; every call must be `await`-ed.

**C++ namespace:** `using namespace RoboDK_API;` or define `RDK_SKIP_NAMESPACE` to avoid it.

## Testing Notes

Python tests require RoboDK to be running with a specific station loaded. Each `.cmd` script in `Python/tests/` sets the path and loads the right station. The `test_import_modules.py` and `test_quaternion.py` tests are standalone (no RoboDK needed). Tests use the `parameterized` package to run the same cases across different robot configurations.
