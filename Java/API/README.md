# RoboDK API for Java

A Java client library for the [RoboDK API](https://robodk.com/doc/en/RoboDK-API.html), ported
from the reference [RoboDK C# API](../../C%23/API).

This library provides the TCP/IP socket layer and binary serialization primitives used by
every RoboDK API call, a full `Mat` pose/matrix implementation, and an initial set of calls on
`RoboDK` and `Item` so the library is usable end to end. More API calls will be added over time
to reach full parity with the C# (`RoboDK.cs`, `Item.cs`) and Python (`robolink.py`) reference
implementations, following the same wire protocol.

This module is part of the `robodk-api-parent` reactor (see the top-level [`../README.md`](../README.md))
together with the [`../Example`](../Example) module, which is a small runnable application
built against this library. Build/run/debug instructions live there.

## Requirements

* Java 11+
* Maven 3.6+
* [RoboDK](https://robodk.com/download) installed and running, with the API server enabled
  (Tools > Options > Other > "Start the API server" and/or run RoboDK with the `-API` sample
  behavior already enabled by default)

## Building

From this folder:

```bash
mvn clean install
```

Or, from the parent folder, to build this module and `Example` together:

```bash
cd ..
mvn clean install
```

This builds `target/robodk-api-1.0.0-SNAPSHOT.jar`. The library has no third-party
dependencies.

## Usage

```java
import com.robodk.api.RoboDK;
import com.robodk.api.Item;
import com.robodk.api.ItemType;
import com.robodk.api.Mat;

public class Example {
    public static void main(String[] args) {
        try (RoboDK robodk = new RoboDK()) {
            if (!robodk.connect()) {
                throw new IllegalStateException("Could not connect to RoboDK. Is it running?");
            }

            System.out.println("Connected to RoboDK " + robodk.version());

            for (String name : robodk.getItemListNames(ItemType.ROBOT)) {
                System.out.println("Robot found: " + name);
            }

            Item robot = robodk.getItemByName("", ItemType.ROBOT);
            if (robot.isValid()) {
                System.out.println("First robot: " + robot.getName());
                System.out.println("Current joints: " + java.util.Arrays.toString(robot.getJoints()));
                System.out.println("Current pose:\n" + robot.getPose());
            }
        }
    }
}
```

A runnable version of this same walkthrough lives in the `Example` module
(`Example/src/main/java/com/robodk/example/BasicExample.java`).

## Project structure

```
Java/API/
  pom.xml
  README.md
  src/main/java/com/robodk/api/
    RoboDK.java              Socket layer, binary (de)serialization, and RoboDK-level API calls
    Item.java                Item-level API calls (name, pose, joints, tree navigation, ...)
    ItemType.java             Enum of RoboDK item types (robot, frame, tool, target, ...)
    Mat.java                  4x4 homogeneous pose matrix and general matrix operations
    exception/
      RdkException.java       Raised for RoboDK API errors and connection problems
      MatException.java       Raised for invalid Mat operations
```

## Mat

`Mat` is a standalone, dependency-free matrix implementation (backed by a plain `double[][]`)
covering the same operations as the reference C# `Mat` class:

* Construction: zero/identity matrices of any size, 4x4 poses from 12 or 16 values, 3x3
  rotation matrices, column vectors, and point lists.
* Pose builders: `transl`, `rotX`/`rotY`/`rotZ`, `fromXyzRpw`, `fromTxyzRxyz`, `fromUR`,
  `fromPointNormal`.
* Pose decomposition: `toXyzRpw`, `toTxyzRxyz`, `toUR`, `pos`/`setPos`, `vx`/`vy`/`vz` (and
  their setters), `rot3x3`, `translationPose`, `rotationPose`.
* Matrix algebra: `add`, `subtract`, `multiply` (matrix-matrix, matrix-scalar, and
  matrix-vector), `negate`, `transpose`, `invert`, `concatenateHorizontal`/`concatenateVertical`.
* Vector helpers: `norm`, `normalize`, `cross`, `dot`, `angle`.
* Tool/frame offsets: `relTool`, `offset`.
* Persistence: `saveCsv`, `saveMat`.

## Connecting to RoboDK, and launching it automatically

`connect()` first scans a small range of local ports (like the C# and Python reference APIs)
for an already-running RoboDK with its API server enabled. If none is found and the target
host is localhost, it will also try to **start RoboDK itself** and connect to the new instance,
without requiring any external/third-party dependency:

```java
RoboDK robodk = new RoboDK();
robodk.setStartNewInstance(true); // force a new instance even if one is already running
if (!robodk.connect()) {
    throw new IllegalStateException("Could not connect to RoboDK, and could not start it either.");
}
```

By default (`isStartNewInstance() == false`), a new instance is only launched as a fallback when
connecting to localhost and no running instance answered on any of the scanned ports — matching
the reference APIs' behavior of "connect, or start one for me".

Relevant `RoboDK` members:

* `setApplicationDir(String)` / `getApplicationDir()` — explicit path to the RoboDK executable to
  launch. When not set, the executable is located automatically (see below).
* `setStartNewInstance(boolean)` / `isStartNewInstance()` — always launch a new instance instead
  of trying to reuse one that is already running.
* `setCommandLineArgs(String...)` / `getCommandLineArgs()` — extra command-line arguments passed
  to RoboDK on launch (in addition to the `-PORT=` argument, which is always added automatically).
* `setStartTimeoutMilliseconds(int)` / `getStartTimeoutMilliseconds()` — how long to wait for the
  newly launched process to report that it is ready (default 60000 ms).
* `getProcess()` — the `java.lang.Process` for an instance started by this `RoboDK` object, or
  `null` if none was started (either not launched, or connected to an already-running instance).
* `RoboDK.findRoboDKExecutable()` — static helper that locates the RoboDK executable on the
  current machine, or returns `null` if it can't be found.
* `RoboDK.isRoboDKInstallFound()` — convenience wrapper: `findRoboDKExecutable() != null`.

### Executable discovery

Locating the executable without a third-party dependency (such as JNA, needed for a proper
Windows registry API) is handled per-OS, mirroring `getPathRoboDK()` from the Python reference
API (`robolink.py`), which is the only reference implementation that supports more than Windows
(the C# API only looks up the Windows registry via `Microsoft.Win32.Registry`, which is
Windows-only):

* **Windows**: reads `HKLM\SOFTWARE\RoboDK\INSTDIR` by shelling out to `reg.exe` (bundled with
  every Windows install), then looks for `<INSTDIR>\bin\RoboDK.exe`. Falls back to
  `C:\RoboDK\bin\RoboDK.exe` if the registry lookup fails or the key doesn't exist.
* **Linux**: `~/RoboDK/bin/RoboDK`.
* **macOS**: `~/Applications/RoboDK.app/Contents/MacOS/RoboDK`, falling back to
  `~/RoboDK/RoboDK.app/Contents/MacOS/RoboDK`.

Launching is done with `java.lang.ProcessBuilder` (no external dependency), passing `-PORT=<port>`
plus any `commandLineArgs`. `connect()` waits (up to `startTimeoutMilliseconds`) for RoboDK to
print that it is running, then connects to it; the process's remaining output is drained on a
background daemon thread so its stdout pipe never fills up and blocks it.

## Notes on the wire protocol

RoboDK API commands are ASCII strings terminated by `\n`, generally followed by binary
arguments (32-bit big-endian integers, 64-bit big-endian IEEE 754 doubles, or item
references made of a 64-bit item id followed by a 32-bit item type). Every command ends with
a status code read via `checkStatus()`; a non-zero status either carries a warning/error
message or signals a hard failure, which is surfaced as an `RdkException`.
