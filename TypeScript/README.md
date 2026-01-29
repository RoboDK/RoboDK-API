# @robodk/robodk

Official RoboDK API for TypeScript and JavaScript. Control robots, create programs, and automate manufacturing workflows.

## Requirements

- Node.js 18+
- [RoboDK](https://robodk.com/download) installed (free educational license available)

## Installation

```bash
npm install @robodk/robodk
```

## Quick Start

```typescript
import { Robolink, ITEM_TYPE_ROBOT } from '@robodk/robodk';

async function main() {
  // Connect to RoboDK (launches automatically if not running)
  const rdk = new Robolink();
  await rdk.Connect();

  // Get the first robot in the station
  const robot = await rdk.Item('', ITEM_TYPE_ROBOT);
  console.log('Robot:', await robot.Name());

  // Get current joint positions
  const joints = await robot.Joints();
  console.log('Joints:', joints);

  // Move robot (joint movement)
  await robot.MoveJ([0, -90, 90, 0, 90, 0]);

  // Get current pose (position + orientation)
  const pose = await robot.Pose();
  console.log('Position:', pose.Pos());

  rdk.Disconnect();
}

main();
```

## Features

- **Full API parity** with the Python RoboDK API
- **TypeScript-first** with complete type definitions
- **Zero dependencies** - uses Node.js built-in modules
- **Auto-launch** RoboDK if not running
- **Async/await** for all I/O operations

## API Overview

### Robolink Class

Main interface to RoboDK. Manages connection and station-level operations.

```typescript
const rdk = new Robolink();
await rdk.Connect();

// Find items
const robot = await rdk.Item('UR10', ITEM_TYPE_ROBOT);
const frame = await rdk.Item('Base Frame', ITEM_TYPE_FRAME);
const items = await rdk.ItemList(ITEM_TYPE_ROBOT);

// Create items
const newFrame = await rdk.AddFrame('My Frame');
const newTarget = await rdk.AddTarget('Target 1', frame, robot);

// Station operations
await rdk.Render();
await rdk.Save('station.rdk');
```

### Item Class

Represents any item in the RoboDK station tree (robot, frame, tool, target, etc.).

```typescript
// Robot operations
await robot.MoveJ(target);        // Joint movement
await robot.MoveL(target);        // Linear movement
await robot.MoveC(via, target);   // Circular movement

const joints = await robot.Joints();
await robot.setJoints([0, -90, 90, 0, 90, 0]);

const pose = await robot.Pose();
await robot.setPose(newPose);

// Frame/tool operations
await frame.setPoseAbs(pose);
const children = await frame.Childs();

// Item properties
const name = await item.Name();
await item.setName('New Name');
const visible = await item.Visible();
await item.setVisible(false);
```

### Mat Class

4x4 transformation matrix for poses (position + orientation).

```typescript
import { Mat } from '@robodk/robodk';

// Identity matrix
const m = new Mat();

// From position
const pose = Mat.transl(100, 200, 300);

// Get/set position
const [x, y, z] = pose.Pos();
pose.setPos([150, 250, 350]);

// Matrix operations
const combined = pose1.multiply(pose2);
const inverse = pose.inv();
```

## Constants

Common constants are exported for convenience:

```typescript
import {
  // Item types
  ITEM_TYPE_ROBOT,
  ITEM_TYPE_FRAME,
  ITEM_TYPE_TOOL,
  ITEM_TYPE_TARGET,
  ITEM_TYPE_PROGRAM,

  // Run modes
  RUNMODE_SIMULATE,
  RUNMODE_MAKE_ROBOTPROG,
  RUNMODE_RUN_ROBOT,

  // Move types
  MOVE_TYPE_JOINT,
  MOVE_TYPE_LINEAR,
  MOVE_TYPE_CIRCULAR,
} from '@robodk/robodk';
```

## Connection Options

```typescript
// Default: localhost:20500, auto-launch RoboDK
const rdk = new Robolink();

// Custom IP/port (connect to remote RoboDK)
const rdk = new Robolink('192.168.1.100', 20500);

// Custom RoboDK path
const rdk = new Robolink('localhost', 20500, [], 'D:\\RoboDK\\bin\\RoboDK.exe');
```

## Documentation

- [RoboDK API Documentation](https://robodk.com/doc/en/PythonAPI/index.html)
- [RoboDK Examples](https://github.com/RoboDK/RoboDK-API/tree/master/Python/Examples)

## License

Apache-2.0
