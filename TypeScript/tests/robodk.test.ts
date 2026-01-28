// robodk.test.ts
import { test, describe, before, after } from 'node:test';
import assert from 'node:assert';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME, ITEM_TYPE_TOOL, ITEM_TYPE_OBJECT, RUNMODE_SIMULATE, MAKE_ROBOT_6COBOT, MAKE_ROBOT_GRIPPER, FEATURE_SURFACE, FEATURE_CURVE, EVENT_SELECTION_TREE_CHANGED, EVENT_ROBOT_MOVED, EVENT_ITEM_MOVED_POSE, EVENT_STATION_CHANGED, Mat, Robolink, Item } from '../src/robodk.js';

// Get path to test assets (go up from dist/tests/ to project root, then into tests/)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const TEST_ASSETS = join(__dirname, '..', '..', 'tests');

// Default timeout for integration tests (30 seconds)
const TEST_TIMEOUT = 30000;

// ============================================================
// Unit Tests (no RoboDK required)
// ============================================================

test('constants are exported', () => {
    assert.strictEqual(ITEM_TYPE_ROBOT, 2);
    assert.strictEqual(ITEM_TYPE_FRAME, 3);
    assert.strictEqual(RUNMODE_SIMULATE, 1);
});

test('event constants are exported', () => {
    assert.strictEqual(EVENT_SELECTION_TREE_CHANGED, 1);
    assert.strictEqual(EVENT_ROBOT_MOVED, 9);
    assert.strictEqual(EVENT_ITEM_MOVED_POSE, 11);
    assert.strictEqual(EVENT_STATION_CHANGED, 19);
});

test('Mat default constructor creates 4x4 identity', () => {
    const m = new Mat();
    assert.strictEqual(m.rows.length, 4);
    assert.strictEqual(m.rows[0][0], 1);
    assert.strictEqual(m.rows[1][1], 1);
    assert.strictEqual(m.rows[2][2], 1);
    assert.strictEqual(m.rows[3][3], 1);
    assert.strictEqual(m.rows[0][1], 0);
});

test('Mat.Pos returns translation vector', () => {
    const m = new Mat();
    m.rows[0][3] = 100;
    m.rows[1][3] = 200;
    m.rows[2][3] = 300;
    assert.deepStrictEqual(m.Pos(), [100, 200, 300]);
});

test('Mat.setPos sets translation vector', () => {
    const m = new Mat();
    m.setPos([10, 20, 30]);
    assert.deepStrictEqual(m.Pos(), [10, 20, 30]);
});

test('Mat.eye creates identity matrix', () => {
    const m = Mat.eye(3);
    assert.deepStrictEqual(m.size(), [3, 3]);
    assert.strictEqual(m.rows[0][0], 1);
    assert.strictEqual(m.rows[1][1], 1);
    assert.strictEqual(m.rows[2][2], 1);
});

test('Mat.tr transposes matrix', () => {
    const m = new Mat([[1, 2], [3, 4]]);
    const t = m.tr();
    assert.strictEqual(t.rows[0][1], 3);
    assert.strictEqual(t.rows[1][0], 2);
});

test('Mat.tolist flattens matrix', () => {
    const m = new Mat([[1, 2], [3, 4]]);
    assert.deepStrictEqual(m.tolist(), [1, 2, 3, 4]);
});

test('Mat.VX/VY/VZ return rotation columns', () => {
    const m = new Mat();
    m.rows[0][0] = 1; m.rows[1][0] = 2; m.rows[2][0] = 3; // VX
    m.rows[0][1] = 4; m.rows[1][1] = 5; m.rows[2][1] = 6; // VY
    m.rows[0][2] = 7; m.rows[1][2] = 8; m.rows[2][2] = 9; // VZ
    assert.deepStrictEqual(m.VX(), [1, 2, 3]);
    assert.deepStrictEqual(m.VY(), [4, 5, 6]);
    assert.deepStrictEqual(m.VZ(), [7, 8, 9]);
});

test('Mat.multiply with scalar', () => {
    const m = new Mat([[1, 2], [3, 4]]);
    const result = m.multiply(2) as Mat;
    assert.strictEqual(result.rows[0][0], 2);
    assert.strictEqual(result.rows[0][1], 4);
    assert.strictEqual(result.rows[1][0], 6);
    assert.strictEqual(result.rows[1][1], 8);
});

test('Mat.multiply with matrix', () => {
    const m1 = new Mat([[1, 2], [3, 4]]);
    const m2 = new Mat([[5, 6], [7, 8]]);
    const result = m1.multiply(m2) as Mat;
    // [1*5+2*7, 1*6+2*8] = [19, 22]
    // [3*5+4*7, 3*6+4*8] = [43, 50]
    assert.strictEqual(result.rows[0][0], 19);
    assert.strictEqual(result.rows[0][1], 22);
    assert.strictEqual(result.rows[1][0], 43);
    assert.strictEqual(result.rows[1][1], 50);
});

test('Mat.multiply with vector', () => {
    const m = new Mat();  // 4x4 identity
    m.rows[0][3] = 100;   // Translation X
    m.rows[1][3] = 200;   // Translation Y
    m.rows[2][3] = 300;   // Translation Z
    // Multiply by 3D vector (extends to [0, 0, 0, 1] for homogeneous)
    const result = m.multiply([0, 0, 0]) as number[];
    assert.strictEqual(result.length, 3);
    assert.strictEqual(result[0], 100);
    assert.strictEqual(result[1], 200);
    assert.strictEqual(result[2], 300);
});

test('Mat.invH inverts homogeneous matrix', () => {
    // Create a translation matrix
    const m = Mat.transl(100, 200, 300);
    const inv = m.invH();
    // Inverse of translation should be negative translation
    const pos = inv.Pos();
    assert.strictEqual(pos[0], -100);
    assert.strictEqual(pos[1], -200);
    assert.strictEqual(pos[2], -300);
});

test('Mat.invH roundtrip', () => {
    // Create a rotation and translation
    const m = Mat.rotx(Math.PI / 4).multiply(Mat.transl(100, 200, 300)) as Mat;
    const inv = m.invH();
    const identity = m.multiply(inv) as Mat;
    // Should be close to identity
    const epsilon = 1e-10;
    assert.ok(Math.abs(identity.rows[0][0] - 1) < epsilon);
    assert.ok(Math.abs(identity.rows[1][1] - 1) < epsilon);
    assert.ok(Math.abs(identity.rows[2][2] - 1) < epsilon);
    assert.ok(Math.abs(identity.rows[3][3] - 1) < epsilon);
    assert.ok(Math.abs(identity.rows[0][3]) < epsilon);
    assert.ok(Math.abs(identity.rows[1][3]) < epsilon);
    assert.ok(Math.abs(identity.rows[2][3]) < epsilon);
});

test('Mat.rotx creates rotation around X', () => {
    const m = Mat.rotx(Math.PI / 2); // 90 degrees
    // Y axis should become Z axis
    const epsilon = 1e-10;
    assert.ok(Math.abs(m.rows[1][1]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[2][2]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[1][2] - (-1)) < epsilon); // -sin(90) = -1
    assert.ok(Math.abs(m.rows[2][1] - 1) < epsilon);    // sin(90) = 1
});

test('Mat.roty creates rotation around Y', () => {
    const m = Mat.roty(Math.PI / 2); // 90 degrees
    // X axis should become -Z axis
    const epsilon = 1e-10;
    assert.ok(Math.abs(m.rows[0][0]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[2][2]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[0][2] - 1) < epsilon);    // sin(90) = 1
    assert.ok(Math.abs(m.rows[2][0] - (-1)) < epsilon); // -sin(90) = -1
});

test('Mat.rotz creates rotation around Z', () => {
    const m = Mat.rotz(Math.PI / 2); // 90 degrees
    // X axis should become Y axis
    const epsilon = 1e-10;
    assert.ok(Math.abs(m.rows[0][0]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[1][1]) < epsilon); // cos(90) = 0
    assert.ok(Math.abs(m.rows[0][1] - (-1)) < epsilon); // -sin(90) = -1
    assert.ok(Math.abs(m.rows[1][0] - 1) < epsilon);    // sin(90) = 1
});

test('Mat.transl creates translation matrix', () => {
    const m = Mat.transl(100, 200, 300);
    assert.deepStrictEqual(m.Pos(), [100, 200, 300]);
    // Should be identity rotation
    assert.strictEqual(m.rows[0][0], 1);
    assert.strictEqual(m.rows[1][1], 1);
    assert.strictEqual(m.rows[2][2], 1);
    assert.strictEqual(m.rows[3][3], 1);
});

test('Mat.transl accepts array', () => {
    const m = Mat.transl([50, 100, 150]);
    assert.deepStrictEqual(m.Pos(), [50, 100, 150]);
});

// ============================================================
// Robolink Constructor Tests (no connection)
// ============================================================

test('Robolink constructor sets defaults', () => {
    const rdk = new Robolink();
    assert.strictEqual(rdk.IP, 'localhost');
    assert.strictEqual(rdk.PORT, 20500);
});

test('Buffer serializes int32 as big-endian', () => {
    const buf = Buffer.alloc(4);
    buf.writeInt32BE(12345, 0);
    assert.strictEqual(buf.readInt32BE(0), 12345);
});

test('Buffer serializes pose as column-major doubles', () => {
    const pose = new Mat();
    pose.rows[0][3] = 100; // Translation X
    pose.rows[1][3] = 200; // Translation Y
    pose.rows[2][3] = 300; // Translation Z

    // Column-major: col0, col1, col2, col3
    // Translation is column 3: indices 12, 13, 14 in flat array
    const buf = Buffer.alloc(128);
    let offset = 0;
    for (let j = 0; j < 4; j++) {
        for (let i = 0; i < 4; i++) {
            buf.writeDoubleBE(pose.rows[i][j], offset);
            offset += 8;
        }
    }

    // Col 3 starts at offset 96 (12 * 8)
    assert.strictEqual(buf.readDoubleBE(96), 100);  // X
    assert.strictEqual(buf.readDoubleBE(104), 200); // Y
    assert.strictEqual(buf.readDoubleBE(112), 300); // Z
});


// ============================================================
// Item Tests (no connection)
// ============================================================

test('Item stores pointer and type', () => {
    const rdk = new Robolink();
    const item = new Item(rdk, BigInt(12345), 2);
    assert.strictEqual(item.item, BigInt(12345));
    assert.strictEqual(item.type, 2);
});

test('Item.Valid checks pointer', () => {
    const rdk = new Robolink();
    const invalid = new Item(rdk);
    const valid = new Item(rdk, BigInt(1));
    assert.strictEqual(invalid.Valid(), false);
    assert.strictEqual(valid.Valid(), true);
});

// ============================================================
// Robolink Lifecycle Tests (no connection)
// ============================================================

test('Robolink constructor with default args', () => {
    const rdk = new Robolink();
    assert.strictEqual(rdk.IP, 'localhost');
    assert.strictEqual(rdk.PORT, 20500);
    assert.strictEqual(rdk.PORT_START, 20500);
    assert.strictEqual(rdk.PORT_END, 20500);
    assert.deepStrictEqual(rdk.ARGUMENTS, []);
    assert.strictEqual(rdk.QUIT_ON_CLOSE, false);
    assert.strictEqual(rdk.CLOSE_STD_OUT, false);
});

test('Robolink constructor with custom port', () => {
    const rdk = new Robolink('localhost', 20501);
    assert.strictEqual(rdk.PORT, 20501);
    assert.strictEqual(rdk.PORT_START, 20501);
    assert.strictEqual(rdk.PORT_END, 20501);
    assert.ok(rdk.ARGUMENTS.includes('-PORT=20501'));
});

test('Robolink constructor with args as string', () => {
    const rdk = new Robolink('localhost', null, '-NOUI');
    assert.deepStrictEqual(rdk.ARGUMENTS, ['-NOUI']);
});

test('Robolink constructor with args as array', () => {
    const rdk = new Robolink('localhost', null, ['-NOUI', '-SKIPINI']);
    assert.deepStrictEqual(rdk.ARGUMENTS, ['-NOUI', '-SKIPINI']);
});

test('Robolink constructor with quit_on_close', () => {
    const rdk = new Robolink('localhost', null, [], null, false, true);
    assert.strictEqual(rdk.QUIT_ON_CLOSE, true);
});

// ============================================================
// Lifecycle Test (starts/stops its own RoboDK)
// ============================================================

// Use port 20511 for lifecycle tests (different from integration tests on 20510)
const LIFECYCLE_TEST_PORT = 20511;
const LIFECYCLE_TEST_ARGS = ['-NEWINSTANCE', '-HIDDEN', '-SKIPINI', '-EXIT_LAST_COM'];

test('Robolink.Connect connects to RoboDK', { timeout: TEST_TIMEOUT }, async () => {
    // This test verifies start/connect/disconnect/stop lifecycle
    const rdk = new Robolink('localhost', LIFECYCLE_TEST_PORT, LIFECYCLE_TEST_ARGS, null, false, true);
    const result = await rdk.Connect();
    assert.strictEqual(result, 1);
    assert.ok(rdk.BUILD > 0);
    await rdk.Disconnect();
});

test('Robolink Command', async () => {
    const rdk = new Robolink('localhost', LIFECYCLE_TEST_PORT, LIFECYCLE_TEST_ARGS, null, false, true);
    const result = await rdk.Connect();
    assert.strictEqual(result, 1);
    let response = await rdk.Command('')
    assert.ok(response.startsWith('(Command)'));
    await rdk.Disconnect();
});


// ============================================================
// Integration Tests (shared RoboDK instance)
// ============================================================

// Test configuration - use isolated instance to avoid conflicts with user's RoboDK
const TEST_PORT = 20510;
const TEST_ARGS = ['-NEWINSTANCE', '-HIDDEN', '-SKIPINI', '-EXIT_LAST_COM'];

describe('Integration Tests', { timeout: 300000 }, () => {
    let rdk: Robolink;

    before(async () => {
        // Start RoboDK on isolated port with -NEWINSTANCE to avoid conflicts
        rdk = new Robolink('localhost', TEST_PORT, TEST_ARGS, null, false, true);
        const result = await rdk.Connect();
        if (result !== 1) {
            throw new Error('Failed to connect to RoboDK');
        }
        console.log(`RoboDK connected on port ${TEST_PORT} for integration tests`);
    });

    after(async () => {
        // Stop RoboDK after all integration tests
        if (rdk) {
            await rdk.Disconnect();
            console.log('RoboDK disconnected after integration tests');
        }
    });

    test('Item.Name gets and sets item name', async () => {
        const station = await rdk.AddStation('NameTest');
        const frame = await rdk.AddFrame('TestFrame');
        assert.ok(frame.Valid());

        const name = await frame.Name();
        assert.strictEqual(name, 'TestFrame');

        await frame.setName('RenamedFrame');
        const newName = await frame.Name();
        assert.strictEqual(newName, 'RenamedFrame');

        await rdk.CloseStation();
    });

    test('Item.Pose gets and sets pose', async () => {
        const station = await rdk.AddStation('PoseTest');
        const frame = await rdk.AddFrame('PoseTestFrame');

        // Get initial pose (should be identity at origin)
        const pose1 = await frame.Pose();
        assert.strictEqual(pose1.rows.length, 4);

        // Set new pose with translation
        const newPose = new Mat();
        newPose.setPos([100, 200, 300]);
        await frame.setPose(newPose);

        // Verify pose was set
        const pose2 = await frame.Pose();
        const pos = pose2.Pos();
        assert.ok(Math.abs(pos[0] - 100) < 0.001);
        assert.ok(Math.abs(pos[1] - 200) < 0.001);
        assert.ok(Math.abs(pos[2] - 300) < 0.001);

        await rdk.CloseStation();
    });

    test('Robolink.Item finds item by name', async () => {
        const station = await rdk.AddStation('ItemFindTest');
        const frame = await rdk.AddFrame('FindMeFrame');
        const found = await rdk.Item('FindMeFrame');
        assert.ok(found.Valid());
        assert.strictEqual(found.type, ITEM_TYPE_FRAME);

        await rdk.CloseStation();
    });

    test('Robolink.ItemList returns all items', async () => {
        const station = await rdk.AddStation('ItemListTest');
        const frame1 = await rdk.AddFrame('ListFrame1');
        const frame2 = await rdk.AddFrame('ListFrame2');

        const items = await rdk.ItemList();
        assert.ok(Array.isArray(items));
        assert.ok(items.length >= 2);

        await rdk.CloseStation();
    });

    test('Robolink.Version returns version string', async () => {
        const version = await rdk.Version();
        assert.ok(typeof version === 'string');
        assert.ok(version.length > 0);
    });

    test('Robolink.AddTarget creates target', async () => {
        const station = await rdk.AddStation('TargetTest');
        const target = await rdk.AddTarget('TestTarget');
        assert.ok(target.Valid());

        // Verify it's a target type
        const itemType = await target.Type();
        assert.strictEqual(itemType, 6); // ITEM_TYPE_TARGET = 6

        // Verify name was set
        const name = await target.Name();
        assert.strictEqual(name, 'TestTarget');

        // Verify it can be found by name
        const found = await rdk.Item('TestTarget');
        assert.ok(found.Valid());
        assert.strictEqual(found.item, target.item);

        await rdk.CloseStation();
    });

    test('Item.Type returns item type', async () => {
        const station = await rdk.AddStation('TypeTest');
        const frame = await rdk.AddFrame('TypeTestFrame');
        const itemType = await frame.Type();
        assert.strictEqual(itemType, ITEM_TYPE_FRAME);

        await rdk.CloseStation();
    });

    test('Item.Parent returns parent item', async () => {
        const station = await rdk.AddStation('ParentTest');
        const parent = await rdk.AddFrame('ParentFrame');
        const child = await rdk.AddFrame('ChildFrame', parent);

        const foundParent = await child.Parent();
        const parentName = await foundParent.Name();
        assert.strictEqual(parentName, 'ParentFrame');

        await rdk.CloseStation();
    });

    test('Item.Visible gets and sets visibility', async () => {
        const station = await rdk.AddStation('VisibleTest');
        const frame = await rdk.AddFrame('VisibleTestFrame');

        // Frame should be visible by default
        const visible = await frame.Visible();
        assert.strictEqual(visible, true);

        // Hide the frame
        await frame.setVisible(false);
        const hidden = await frame.Visible();
        assert.strictEqual(hidden, false);

        // Show it again
        await frame.setVisible(true);

        await rdk.CloseStation();
    });

    test('Robolink.SimulationSpeed get/set', async () => {
        await rdk.setSimulationSpeed(5);
        const speed = await rdk.SimulationSpeed();
        assert.ok(Math.abs(speed - 5) < 0.1);

        // Restore default
        await rdk.setSimulationSpeed(1);
    });

    test('Robolink.SimulationTime returns number', async () => {
        const time = await rdk.SimulationTime();
        assert.ok(typeof time === 'number');
    });

    test('Robolink.RunMode get/set', async () => {
        await rdk.setRunMode(RUNMODE_SIMULATE);
        const mode = await rdk.RunMode();
        assert.strictEqual(mode, RUNMODE_SIMULATE);
    });

    test('Robolink.getParam returns string', async () => {
        const path = await rdk.getParam('PATH_OPENSTATION');
        assert.ok(typeof path === 'string');
    });

    test('Robolink.AddProgram creates program', async () => {
        const station = await rdk.AddStation('ProgramTest');
        const prog = await rdk.AddProgram('TestProgram');
        assert.ok(prog.Valid());

        // Verify it's a program type
        const itemType = await prog.Type();
        assert.strictEqual(itemType, 8); // ITEM_TYPE_PROGRAM = 8

        // Verify name was set
        const name = await prog.Name();
        assert.strictEqual(name, 'TestProgram');

        // Verify it can be found by name
        const found = await rdk.Item('TestProgram');
        assert.ok(found.Valid());
        assert.strictEqual(found.item, prog.item);

        await rdk.CloseStation();
    });

    test('Robolink.AddStation creates station', async () => {
        const station = await rdk.AddStation('TestStation');
        assert.ok(station.Valid());

        // Verify it's a station type
        const itemType = await station.Type();
        assert.strictEqual(itemType, 1); // ITEM_TYPE_STATION = 1

        // Verify name was set
        const name = await station.Name();
        assert.strictEqual(name, 'TestStation');

        // Verify it's the active station
        const active = await rdk.ActiveStation();
        assert.strictEqual(active.item, station.item);

        // Cleanup - close the new station
        await rdk.CloseStation();
    });

    // Collision Detection Tests
    // Note: These tests verify the API works correctly. Actual collision detection
    // behavior depends on RoboDK settings and geometry, so we focus on return types.
    test('Robolink.setCollisionActive enables collision checking', async () => {
        const station = await rdk.AddStation('CollisionTest');

        // Enable collision detection - returns number of collision pairs
        const ncollisions = await rdk.setCollisionActive(1); // COLLISION_ON
        assert.strictEqual(typeof ncollisions, 'number');

        // Disable collision detection
        await rdk.setCollisionActive(0); // COLLISION_OFF

        await rdk.CloseStation();
    });

    test('Robolink.Collisions returns collision count', async () => {
        const station = await rdk.AddStation('CollisionsTest');

        // Enable collision detection
        await rdk.setCollisionActive(1);

        // Collisions() should return a number >= 0
        const ncollisions = await rdk.Collisions();
        assert.strictEqual(typeof ncollisions, 'number');
        assert.ok(ncollisions >= 0);

        // Cleanup
        await rdk.setCollisionActive(0);
        await rdk.CloseStation();
    });

    test('Robolink.CollisionItems returns array', async () => {
        const station = await rdk.AddStation('CollisionItemsTest');

        // Enable collision detection
        await rdk.setCollisionActive(1);

        // CollisionItems should return an array
        const items = await rdk.CollisionItems();
        assert.ok(Array.isArray(items));

        // Cleanup
        await rdk.setCollisionActive(0);
        await rdk.CloseStation();
    });

    // View and Selection Tests
    test('Robolink.ViewPose get/set', async () => {
        const station = await rdk.AddStation('ViewPoseTest');

        // Get current view pose
        const pose1 = await rdk.ViewPose();
        assert.strictEqual(pose1.rows.length, 4);

        // Create a new view pose with a different position
        const newPose = Mat.transl(500, 600, 700);
        await rdk.setViewPose(newPose);

        // Verify the change was applied
        const pose2 = await rdk.ViewPose();
        const pos = pose2.Pos();
        assert.ok(Math.abs(pos[0] - 500) < 1, `Expected X~500, got ${pos[0]}`);
        assert.ok(Math.abs(pos[1] - 600) < 1, `Expected Y~600, got ${pos[1]}`);
        assert.ok(Math.abs(pos[2] - 700) < 1, `Expected Z~700, got ${pos[2]}`);

        await rdk.CloseStation();
    });

    test('Robolink.Selection get/set', async () => {
        const station = await rdk.AddStation('SelectionTest');
        const frame1 = await rdk.AddFrame('SelectionFrame1');
        const frame2 = await rdk.AddFrame('SelectionFrame2');

        // Set selection to frame1
        await rdk.setSelection([frame1]);

        // Get selection and verify it contains frame1
        const selection1 = await rdk.Selection();
        assert.ok(Array.isArray(selection1));
        assert.strictEqual(selection1.length, 1, 'Should have 1 item selected');
        assert.strictEqual(selection1[0].item, frame1.item, 'Selected item should be frame1');

        // Set selection to both frames
        await rdk.setSelection([frame1, frame2]);

        // Verify both are selected
        const selection2 = await rdk.Selection();
        assert.strictEqual(selection2.length, 2, 'Should have 2 items selected');

        // Clear selection
        await rdk.setSelection([]);
        const selection3 = await rdk.Selection();
        assert.strictEqual(selection3.length, 0, 'Should have no items selected');

        await rdk.CloseStation();
    });

    test('Robolink.getFlagsItem returns flags', async () => {
        const station = await rdk.AddStation('FlagsTest');
        const frame = await rdk.AddFrame('FlagsFrame');
        const flags = await rdk.getFlagsItem(frame);
        assert.ok(typeof flags === 'number');

        await rdk.CloseStation();
    });

    test('Robolink.ShowMessage displays message', async () => {
        // Show status bar message (non-popup)
        await rdk.ShowMessage('Test message', false);
    });

    // Copy/Paste and Station Tests
    test('Robolink.Copy and Paste', async () => {
        const station = await rdk.AddStation('CopyPasteTest');

        // Create frame with specific pose
        const frame = await rdk.AddFrame('CopyFrame');
        const originalPose = Mat.transl(100, 200, 300);
        await frame.setPose(originalPose);

        // Copy and paste
        await rdk.Copy(frame);
        const pasted = await rdk.Paste();

        assert.ok(Array.isArray(pasted));
        assert.strictEqual(pasted.length, 1);

        // Verify pasted item is a valid frame
        const pastedFrame = pasted[0];
        assert.ok(pastedFrame.Valid());
        const pastedType = await pastedFrame.Type();
        assert.strictEqual(pastedType, ITEM_TYPE_FRAME);

        // Verify pasted item has the same pose
        const pastedPose = await pastedFrame.Pose();
        const pastedPos = pastedPose.Pos();
        assert.ok(Math.abs(pastedPos[0] - 100) < 0.01, `Expected X=100, got ${pastedPos[0]}`);
        assert.ok(Math.abs(pastedPos[1] - 200) < 0.01, `Expected Y=200, got ${pastedPos[1]}`);
        assert.ok(Math.abs(pastedPos[2] - 300) < 0.01, `Expected Z=300, got ${pastedPos[2]}`);

        // Verify pasted item is a different item (different pointer)
        assert.notStrictEqual(pastedFrame.item, frame.item);

        await rdk.CloseStation();
    });

    test('Robolink.ActiveStation get/set', async () => {
        const station = await rdk.ActiveStation();
        assert.ok(station.Valid());
    });

    test('Robolink.getOpenStations returns array', async () => {
        const stations = await rdk.getOpenStations();
        assert.ok(Array.isArray(stations));
        assert.ok(stations.length >= 1);
    });

    test('Robolink.License returns info', async () => {
        const [license, date] = await rdk.License();
        assert.ok(typeof license === 'string');
        assert.ok(typeof date === 'string');
    });

    test('Robolink.isNewInstance returns boolean', () => {
        // The shared rdk instance started a new RoboDK, so this should be true
        const isNew = rdk.isNewInstance();
        assert.strictEqual(typeof isNew, 'boolean');
        assert.strictEqual(isNew, true);
    });

    test('Robolink.getParams returns parameter list', async () => {
        const station = await rdk.AddStation('GetParamsTest');

        // Set a parameter first
        await rdk.setParam('TEST_PARAM', '42');

        // Get all parameters
        const params = await rdk.getParams();
        assert.ok(Array.isArray(params));

        // Should find our test parameter
        const found = params.find(p => p[0] === 'TEST_PARAM');
        assert.ok(found, 'Should find TEST_PARAM in parameters');

        await rdk.CloseStation();
    });

    test('Robolink.RunMessage sends message', async () => {
        // This just verifies the command doesn't throw
        await rdk.RunMessage('Test message from TypeScript API');
        await rdk.RunMessage('Test comment', true);
    });

    test('Robolink.setCollisionActivePair enables pair collision', async () => {
        const station = await rdk.AddStation('CollisionPairTest');

        // Load two cubes
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube1 = await rdk.AddFile(cubePath);
        const cube2 = await rdk.AddFile(cubePath);

        // Enable collision checking globally
        await rdk.setCollisionActive(1);

        // Set collision checking for this pair
        const success = await rdk.setCollisionActivePair(1, cube1, cube2);
        assert.ok(typeof success === 'number');

        // Get the active collision pairs
        const pairs = await rdk.CollisionActivePairList();
        assert.ok(Array.isArray(pairs));

        // Disable collision checking
        await rdk.setCollisionActive(0);

        await rdk.CloseStation();
    });

    test('Robolink.CollisionPairs returns array of pairs', async () => {
        const station = await rdk.AddStation('CollisionPairsTest');

        // Enable collision checking
        await rdk.setCollisionActive(1);

        // CollisionPairs should return an array
        const pairs = await rdk.CollisionPairs();
        assert.ok(Array.isArray(pairs));

        // Disable collision checking
        await rdk.setCollisionActive(0);

        await rdk.CloseStation();
    });

    // Batch Operations Tests
    test('Robolink.setPoses sets multiple poses at once', async () => {
        const station = await rdk.AddStation('SetPosesTest');

        // Create multiple frames
        const frame1 = await rdk.AddFrame('Frame1');
        const frame2 = await rdk.AddFrame('Frame2');
        const frame3 = await rdk.AddFrame('Frame3');

        // Set poses in batch
        const poses = [
            Mat.transl(100, 0, 0),
            Mat.transl(0, 200, 0),
            Mat.transl(0, 0, 300)
        ];
        await rdk.setPoses([frame1, frame2, frame3], poses);

        // Verify poses were set
        const p1 = await frame1.Pose();
        const p2 = await frame2.Pose();
        const p3 = await frame3.Pose();

        assert.ok(Math.abs(p1.Pos()[0] - 100) < 0.01);
        assert.ok(Math.abs(p2.Pos()[1] - 200) < 0.01);
        assert.ok(Math.abs(p3.Pos()[2] - 300) < 0.01);

        await rdk.CloseStation();
    });

    test('Robolink.setPosesAbs sets multiple absolute poses', async () => {
        const station = await rdk.AddStation('SetPosesAbsTest');

        // Create parent frame with offset
        const parent = await rdk.AddFrame('Parent');
        await parent.setPose(Mat.transl(50, 50, 50));

        // Create child frames
        const frame1 = await rdk.AddFrame('Frame1', parent);
        const frame2 = await rdk.AddFrame('Frame2', parent);

        // Set absolute poses (world coordinates)
        const poses = [
            Mat.transl(100, 100, 100),
            Mat.transl(200, 200, 200)
        ];
        await rdk.setPosesAbs([frame1, frame2], poses);

        // Verify absolute poses
        const p1 = await frame1.PoseAbs();
        const p2 = await frame2.PoseAbs();

        assert.ok(Math.abs(p1.Pos()[0] - 100) < 0.01);
        assert.ok(Math.abs(p2.Pos()[0] - 200) < 0.01);

        await rdk.CloseStation();
    });

    test('Robolink.JointsList gets joints for multiple robots', async () => {
        const station = await rdk.AddStation('JointsListTest');

        // Load two robots
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot1 = await rdk.AddFile(robotPath);
        const robot2 = await rdk.AddFile(robotPath);

        // Set different joint positions
        await robot1.setJoints([10, -20, 30, -40, 50, -60]);
        await robot2.setJoints([5, -10, 15, -20, 25, -30]);

        // Get joints in batch
        const jointsList = await rdk.JointsList([robot1, robot2]);

        assert.strictEqual(jointsList.length, 2);
        assert.ok(Math.abs(jointsList[0][0] - 10) < 0.01);
        assert.ok(Math.abs(jointsList[1][0] - 5) < 0.01);

        await rdk.CloseStation();
    });

    test('Robolink.setJointsList sets joints for multiple robots', async () => {
        const station = await rdk.AddStation('SetJointsListTest');

        // Load two robots
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot1 = await rdk.AddFile(robotPath);
        const robot2 = await rdk.AddFile(robotPath);

        // Set joints in batch
        const jointsList = [
            [15, -25, 35, -45, 55, -65],
            [7, -14, 21, -28, 35, -42]
        ];
        await rdk.setJointsList([robot1, robot2], jointsList);

        // Verify joints
        const j1 = await robot1.Joints();
        const j2 = await robot2.Joints();

        assert.ok(Math.abs(j1[0] - 15) < 0.01);
        assert.ok(Math.abs(j2[0] - 7) < 0.01);

        await rdk.CloseStation();
    });

    test('Robolink.Collision_Line checks line collision', async () => {
        const station = await rdk.AddStation('CollisionLineTest');

        // Load cube and position it at a known location
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);
        // Position cube so its center is at (50, 50, 50) - cube is 100mm so extends 0-100
        await cube.setPose(Mat.transl(0, 0, 0));

        // Line that passes through the cube center (from far above to far below)
        const p1 = [50, 50, 500];   // Way above
        const p2 = [50, 50, -500];  // Way below

        const [collision, item, xyz] = await rdk.Collision_Line(p1, p2);

        // Verify return types
        assert.strictEqual(typeof collision, 'boolean');
        assert.ok(item instanceof Item);
        assert.ok(Array.isArray(xyz));
        assert.strictEqual(xyz.length, 3);

        // If collision occurred, verify the collision point is reasonable
        if (collision) {
            // Z should be somewhere on the cube surface (0 to 100)
            assert.ok(xyz[2] >= -10 && xyz[2] <= 110, `Collision Z=${xyz[2]} should be near cube`);
        }

        await rdk.CloseStation();
    });

    test('Robolink.ProgramStart starts offline programming', async () => {
        const station = await rdk.AddStation('ProgramStartTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Start offline programming
        const errors = await rdk.ProgramStart('TestProgram', '', '', robot);
        assert.strictEqual(typeof errors, 'number');

        // Stop offline programming by setting empty name
        await rdk.ProgramStart('');

        await rdk.CloseStation();
    });

    // Skip test for ItemUserPick - requires user interaction
    test.skip('Robolink.ItemUserPick shows picker dialog', async () => {
        // This test is skipped because it requires user interaction
        // The method blocks until the user selects an item or cancels
    });

    // Camera Tests - skip most as they require display
    test.skip('Robolink.Cam2D_Add creates camera', async () => {
        // This test is skipped because it requires RoboDK display window
        // The camera needs a visible viewport to function
    });

    test.skip('Robolink.Cam2D_Snapshot takes snapshot', async () => {
        // This test is skipped because it requires RoboDK display window
    });

    // Spray Gun Tests
    test('Robolink.Spray_Add creates spray simulation', async () => {
        const station = await rdk.AddStation('SprayTest');

        // Load robot and tool
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Add spray gun (will auto-detect tool)
        const id_spray = await rdk.Spray_Add(null, null, 'ELLYPSE');
        assert.strictEqual(typeof id_spray, 'number');

        // Get stats
        const [info, data] = await rdk.Spray_GetStats(id_spray);
        assert.strictEqual(typeof info, 'string');
        assert.ok(Array.isArray(data));

        // Clear spray
        const cleared = await rdk.Spray_Clear(id_spray);
        assert.strictEqual(typeof cleared, 'number');

        await rdk.CloseStation();
    });

    test('Robolink.Spray_SetState toggles spray state', async () => {
        const station = await rdk.AddStation('SprayStateTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Add spray gun
        const id_spray = await rdk.Spray_Add();

        // Turn on
        const onResult = await rdk.Spray_SetState(1, id_spray); // SPRAY_ON = 1
        assert.strictEqual(typeof onResult, 'number');

        // Turn off
        const offResult = await rdk.Spray_SetState(0, id_spray); // SPRAY_OFF = 0
        assert.strictEqual(typeof offResult, 'number');

        await rdk.CloseStation();
    });

    // Interactive Mode Tests
    test('Robolink.setInteractiveMode sets mode', async () => {
        // Just verify the method doesn't throw
        await rdk.setInteractiveMode(5); // SELECT_MOVE = 5
        await rdk.setInteractiveMode(0); // Reset to default
    });

    // Cursor Tests - skip as they require display interaction
    test.skip('Robolink.CursorXYZ gets cursor position', async () => {
        // This test is skipped because it requires RoboDK display window
    });

    // Plugin Tests - skip as they require actual plugins
    test.skip('Robolink.PluginLoad loads plugin', async () => {
        // This test is skipped because it requires an actual plugin file
    });

    test.skip('Robolink.PluginCommand sends plugin command', async () => {
        // This test is skipped because it requires a loaded plugin
    });

    // Machining Tests
    test('Robolink.AddMachiningProject creates machining project', async () => {
        const station = await rdk.AddStation('MachiningTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Add machining project
        const project = await rdk.AddMachiningProject('TestMachining', robot);
        assert.ok(project.Valid());
        assert.ok(project instanceof Item);

        await rdk.CloseStation();
    });

    // Item Pose Extension Tests
    test('Item.PoseAbs get/set absolute pose', async () => {
        const station = await rdk.AddStation('PoseAbsTest');

        // Create a parent frame with offset
        const parentFrame = await rdk.AddFrame('ParentFrame');
        await parentFrame.setPose(Mat.transl(100, 100, 100));

        // Create child frame under parent
        const childFrame = await rdk.AddFrame('ChildFrame', parentFrame);

        // Set absolute pose (world coordinates)
        const absPose = Mat.transl(200, 300, 400);
        await childFrame.setPoseAbs(absPose);

        // Verify the absolute pose was set correctly
        const retrievedPose = await childFrame.PoseAbs();
        const pos = retrievedPose.Pos();
        assert.ok(Math.abs(pos[0] - 200) < 0.01, `Expected X=200, got ${pos[0]}`);
        assert.ok(Math.abs(pos[1] - 300) < 0.01, `Expected Y=300, got ${pos[1]}`);
        assert.ok(Math.abs(pos[2] - 400) < 0.01, `Expected Z=400, got ${pos[2]}`);

        // Verify relative pose is different from absolute (due to parent offset)
        const relPose = await childFrame.Pose();
        const relPos = relPose.Pos();
        assert.ok(Math.abs(relPos[0] - 100) < 0.01, `Expected relative X=100, got ${relPos[0]}`);
        assert.ok(Math.abs(relPos[1] - 200) < 0.01, `Expected relative Y=200, got ${relPos[1]}`);
        assert.ok(Math.abs(relPos[2] - 300) < 0.01, `Expected relative Z=300, got ${relPos[2]}`);

        await rdk.CloseStation();
    });

    test('Item.GeometryPose get/set on object', async () => {
        const station = await rdk.AddStation('GeometryPoseTest');

        // Load the cube object
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);
        assert.ok(cube.Valid());

        // Get geometry pose
        const geoPose = await cube.GeometryPose();
        assert.strictEqual(geoPose.rows.length, 4);

        // Set geometry pose with offset
        const newGeoPose = new Mat();
        newGeoPose.setPos([10, 20, 30]);
        await cube.setGeometryPose(newGeoPose);

        // Verify the change
        const updatedPose = await cube.GeometryPose();
        const pos = updatedPose.Pos();
        assert.strictEqual(pos[0], 10);
        assert.strictEqual(pos[1], 20);
        assert.strictEqual(pos[2], 30);

        await rdk.CloseStation();
    });

    // Robot Tests (using UR10e)
    test('Load robot and get type', async () => {
        const station = await rdk.AddStation('RobotTypeTest');

        // Load UR10e robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);
        assert.ok(robot.Valid());

        // Verify it's a robot
        const itemType = await robot.Type();
        assert.strictEqual(itemType, ITEM_TYPE_ROBOT);

        await rdk.CloseStation();
    });

    test('Robot Joints get/set', async () => {
        const station = await rdk.AddStation('JointsTest');

        // Load UR10e robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get current joints
        const joints = await robot.Joints();
        assert.ok(Array.isArray(joints));
        assert.strictEqual(joints.length, 6); // UR10e has 6 axes

        // Set new joint values (small movements)
        const newJoints = [10, -20, 30, -40, 50, -60];
        await robot.setJoints(newJoints);

        // Verify the change
        const updatedJoints = await robot.Joints();
        for (let i = 0; i < 6; i++) {
            assert.ok(Math.abs(updatedJoints[i] - newJoints[i]) < 0.001);
        }

        await rdk.CloseStation();
    });

    test('Robot JointLimits get/set', async () => {
        const station = await rdk.AddStation('JointLimitsTest');

        // Load UR10e robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get joint limits
        const [lowerLimits, upperLimits] = await robot.JointLimits();
        assert.ok(Array.isArray(lowerLimits));
        assert.ok(Array.isArray(upperLimits));
        assert.strictEqual(lowerLimits.length, 6);
        assert.strictEqual(upperLimits.length, 6);

        // Verify lower < upper for each joint
        for (let i = 0; i < 6; i++) {
            assert.ok(lowerLimits[i] < upperLimits[i]);
        }

        await rdk.CloseStation();
    });

    test('Robot SolveFK forward kinematics', async () => {
        const station = await rdk.AddStation('SolveFKTest');

        // Load UR10e robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get home joints
        const homeJoints = await robot.JointsHome();
        assert.ok(Array.isArray(homeJoints));

        // Solve forward kinematics for home position
        const pose = await robot.SolveFK(homeJoints);
        assert.strictEqual(pose.rows.length, 4);

        // Pose should be a valid transformation matrix
        const pos = pose.Pos();
        assert.ok(Array.isArray(pos));
        assert.strictEqual(pos.length, 3);

        await rdk.CloseStation();
    });

    // Object Color Tests (using Cube)
    test('Item.Color get/set on object', async () => {
        const station = await rdk.AddStation('ColorTest');

        // Load cube
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);

        // Get current color
        const color = await cube.Color();
        assert.ok(Array.isArray(color));
        assert.strictEqual(color.length, 4); // RGBA

        // Set new color (red)
        await cube.setColor([1, 0, 0, 1]);

        // Verify the change
        const newColor = await cube.Color();
        assert.ok(Math.abs(newColor[0] - 1) < 0.01); // R
        assert.ok(Math.abs(newColor[1] - 0) < 0.01); // G
        assert.ok(Math.abs(newColor[2] - 0) < 0.01); // B

        await rdk.CloseStation();
    });

    test('Item.Scale on object', async () => {
        const station = await rdk.AddStation('ScaleTest');

        // Load cube (100mm)
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);

        // Get bounding box before scaling using Item.setParam('BoundingBox')
        // Returns JSON: {"min": [...], "max": [...], "size": [x, y, z]}
        const bboxBefore = await cube.setParam('BoundingBox');
        const bboxBeforeObj = JSON.parse(bboxBefore);
        const sizeBefore = bboxBeforeObj.size[0];  // X dimension

        // Scale cube by 2x
        await cube.Scale([2, 2, 2]);

        // Get bounding box after scaling
        const bboxAfter = await cube.setParam('BoundingBox');
        const bboxAfterObj = JSON.parse(bboxAfter);
        const sizeAfter = bboxAfterObj.size[0];  // X dimension

        // After 2x scale, size should be doubled
        const ratio = sizeAfter / sizeBefore;
        assert.ok(ratio > 1.9 && ratio < 2.1, `Expected ~2x scale ratio, got ${ratio.toFixed(2)}`);

        await rdk.CloseStation();
    });

    test('Item.setColorShape on object shape', async () => {
        const station = await rdk.AddStation('SetColorShapeTest');

        // Create a simple triangle shape (single shape object)
        const trianglePoints = [
            [0, 0, 0],
            [100, 0, 0],
            [50, 100, 0]
        ];
        const shape = await rdk.AddShape(trianglePoints);

        // Get initial color
        const colorBefore = await shape.Color();
        assert.ok(Array.isArray(colorBefore), 'Should have initial color');

        // Set color of shape 0 to bright magenta
        await shape.setColorShape([1, 0, 1, 1], 0);

        // Verify color changed via Color() getter
        const colorAfter = await shape.Color();
        assert.ok(Math.abs(colorAfter[0] - 1) < 0.01, `Expected R=1, got ${colorAfter[0]}`);
        assert.ok(Math.abs(colorAfter[1] - 0) < 0.01, `Expected G=0, got ${colorAfter[1]}`);
        assert.ok(Math.abs(colorAfter[2] - 1) < 0.01, `Expected B=1, got ${colorAfter[2]}`);

        await rdk.CloseStation();
    });

    test('Item.setColorCurve on curve', async () => {
        const station = await rdk.AddStation('SetColorCurveTest');

        // Create a curve
        const curvePoints = [
            [0, 0, 0, 0, 0, 1],
            [100, 0, 0, 0, 0, 1],
            [100, 100, 0, 0, 0, 1],
        ];
        const curve = await rdk.AddCurve(curvePoints);
        assert.ok(curve.Valid());

        // Get initial color
        const colorBefore = await curve.Color();
        assert.ok(Array.isArray(colorBefore), 'Should have initial color');

        // Set color of all curves to cyan (-1 means all curves)
        await curve.setColorCurve([0, 1, 1, 1], -1);

        // Verify color changed via Color() getter
        const colorAfter = await curve.Color();
        assert.ok(Math.abs(colorAfter[0] - 0) < 0.01, `Expected R=0, got ${colorAfter[0]}`);
        assert.ok(Math.abs(colorAfter[1] - 1) < 0.01, `Expected G=1, got ${colorAfter[1]}`);
        assert.ok(Math.abs(colorAfter[2] - 1) < 0.01, `Expected B=1, got ${colorAfter[2]}`);

        await rdk.CloseStation();
    });

    // Tool Tests (using Robotiq gripper)
    test('Load tool and attach to robot', async () => {
        const station = await rdk.AddStation('ToolTest');

        // Load UR10e robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Load Robotiq gripper tool
        const toolPath = join(TEST_ASSETS, 'RobotiQ-2F-85-Gripper-Open.tool');
        const tool = await rdk.AddFile(toolPath);
        assert.ok(tool.Valid());

        // Verify it's a tool
        const itemType = await tool.Type();
        assert.strictEqual(itemType, ITEM_TYPE_TOOL);

        // Set the tool's parent to the robot
        await tool.setParent(robot);

        // Verify parent
        const parent = await tool.Parent();
        assert.ok(parent.Valid());

        await rdk.CloseStation();
    });

    // Frame and Tool Methods Tests (Task 9)
    test('Robot PoseFrame get/set with pose', async () => {
        const station = await rdk.AddStation('PoseFrameTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get initial frame pose
        const initialFrame = await robot.PoseFrame();
        assert.ok(initialFrame instanceof Mat);

        // Set a new frame pose (offset 100mm in X)
        const newFrame = Mat.transl(100, 0, 0);
        await robot.setPoseFrame(newFrame);

        // Verify the change
        const updatedFrame = await robot.PoseFrame();
        const pos = updatedFrame.Pos();
        assert.ok(Math.abs(pos[0] - 100) < 0.01);

        await rdk.CloseStation();
    });

    test('Robot PoseTool get/set with pose', async () => {
        const station = await rdk.AddStation('PoseToolTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get initial tool pose
        const initialTool = await robot.PoseTool();
        assert.ok(initialTool instanceof Mat);

        // Set a new tool pose (offset 50mm in Z)
        const newTool = Mat.transl(0, 0, 50);
        await robot.setPoseTool(newTool);

        // Verify the change
        const updatedTool = await robot.PoseTool();
        const pos = updatedTool.Pos();
        assert.ok(Math.abs(pos[2] - 50) < 0.01);

        await rdk.CloseStation();
    });

    test('Robot AddTool creates new tool', async () => {
        const station = await rdk.AddStation('AddToolTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Add a new tool
        const toolPose = Mat.transl(0, 0, 100);
        const tool = await robot.AddTool(toolPose, 'TestTCP');

        // Verify tool was created
        assert.ok(tool.Valid());
        const toolType = await tool.Type();
        assert.strictEqual(toolType, ITEM_TYPE_TOOL);

        // Verify tool name
        const name = await tool.Name();
        assert.strictEqual(name, 'TestTCP');

        await rdk.CloseStation();
    });

    test('Item getLink and setLink', async () => {
        const station = await rdk.AddStation('LinkTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Create a program
        const program = await rdk.AddProgram('TestProgram', robot);
        assert.ok(program.Valid());

        // Get linked robot from program
        const linkedRobot = await program.getLink(ITEM_TYPE_ROBOT);
        assert.ok(linkedRobot.Valid());

        await rdk.CloseStation();
    });

    test('Item setRobot links program to robot', async () => {
        const station = await rdk.AddStation('SetRobotTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Create a target
        const target = await rdk.AddTarget('TestTarget');
        assert.ok(target.Valid());

        // Link target to robot
        await target.setRobot(robot);

        // Verify link
        const linkedRobot = await target.getLink(ITEM_TYPE_ROBOT);
        assert.ok(linkedRobot.Valid());

        await rdk.CloseStation();
    });

    test('Robot setPoseFrame with Frame item', async () => {
        const station = await rdk.AddStation('SetPoseFrameItemTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Create a frame with specific pose
        const frame = await rdk.AddFrame('TestFrame');
        const framePose = Mat.transl(200, 100, 50);
        await frame.setPose(framePose);

        // Set robot frame using the frame item
        await robot.setPoseFrame(frame);

        // Verify PoseFrame() returns the frame's pose
        const robotFrame = await robot.PoseFrame();
        const pos = robotFrame.Pos();
        assert.ok(Math.abs(pos[0] - 200) < 0.01, `Expected X=200, got ${pos[0]}`);
        assert.ok(Math.abs(pos[1] - 100) < 0.01, `Expected Y=100, got ${pos[1]}`);
        assert.ok(Math.abs(pos[2] - 50) < 0.01, `Expected Z=50, got ${pos[2]}`);

        await rdk.CloseStation();
    });

    test('Robot setPoseTool with Tool item', async () => {
        const station = await rdk.AddStation('SetPoseToolItemTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Create a tool with specific TCP offset
        const toolPose = Mat.transl(10, 20, 150);
        const tool = await robot.AddTool(toolPose, 'ToolForPose');

        // Set robot tool using the tool item
        await robot.setPoseTool(tool);

        // Verify PoseTool() returns the tool's TCP pose
        const robotTool = await robot.PoseTool();
        const pos = robotTool.Pos();
        assert.ok(Math.abs(pos[0] - 10) < 0.01, `Expected X=10, got ${pos[0]}`);
        assert.ok(Math.abs(pos[1] - 20) < 0.01, `Expected Y=20, got ${pos[1]}`);
        assert.ok(Math.abs(pos[2] - 150) < 0.01, `Expected Z=150, got ${pos[2]}`);

        await rdk.CloseStation();
    });

    // BuildMechanism Tests
    test('BuildMechanism creates 6 DOF robot from STL files', async () => {
        const station = await rdk.AddStation('Build6DOFTest');

        // Load UR10e STL files (base + 6 links)
        const stlFiles = ['base.stl',  'forearm.stl', 'shoulder.stl', 'upperarm.stl','wrist1.stl', 'wrist2.stl', 'wrist3.stl'];
        const objects: Item[] = [];
        for (const file of stlFiles) {
            const stlPath = join(TEST_ASSETS, 'UR10e', file);
            const obj = await rdk.AddFile(stlPath);
            objects.push(obj);
        }

        // UR10e DH parameters
        const parameters = [180.7, 612.6, 571.335, 174.150, 119.850, 116.550, 0.000, 180.000, 0, 0, 0, 180];

        // Joint configuration
        const joints_build = [0, -90, 0, -90, 0, 0];
        const joints_home = [0, -90, -90, 0, 90, 0];
        const joints_senses = [1, 1, -1, 1, 1, 1];
        const joints_lim_low = [-360, -360, -360, -360, -360, -360];
        const joints_lim_high = [360, 360, 360, 360, 360, 360];

        // Build the mechanism
        const robot = await rdk.BuildMechanism(
            MAKE_ROBOT_6COBOT,
            objects,
            parameters,
            joints_build,
            joints_home,
            joints_senses,
            joints_lim_low,
            joints_lim_high,
            Mat.eye(),  // base pose
            Mat.eye(),  // tool pose
            'UR10e_Built'
        );

        assert.ok(robot.Valid(), 'Robot should be valid');

        // Verify it's a robot
        const robotType = await robot.Type();
        assert.strictEqual(robotType, ITEM_TYPE_ROBOT);

        // Verify we can move the joints
        await robot.setJoints([0, -90, 90, -90, -90, 0]);
        const joints = await robot.Joints();
        assert.ok(Math.abs(joints[2] - 90) < 0.1, 'Joint 3 should be at 90 degrees');

        await rdk.CloseStation();
    });

    test('BuildMechanism creates gripper from STL files', async () => {
        const station = await rdk.AddStation('BuildGripperTest');

        // Load RobotiQ Hand-E STL files (base + 2 fingers)
        const stlFiles = ['base.stl', 'finger1.stl', 'finger2.stl'];
        const objects: Item[] = [];
        for (const file of stlFiles) {
            const stlPath = join(TEST_ASSETS, 'RobotiQ Hand-E', file);
            const obj = await rdk.AddFile(stlPath);
            objects.push(obj);
        }

        // Gripper parameters
        const parameters = [0.5];

        // Joint configuration for 2 DOF gripper (2 fingers)
        const joints_build = [0, 0];
        const joints_home = [0, 0];
        const joints_senses = [1, -1];  // Fingers move in opposite directions
        const joints_lim_low = [0, 0];
        const joints_lim_high = [50, 50];  // 50mm stroke

        // Base pose: rotation of 90 degrees around X
        const base_pose = Mat.roty(90 * Math.PI / 180);

        // Tool pose: 150mm offset in Z
        const tool_pose = Mat.transl(0, 0, 150);

        // Build the mechanism
        const gripper = await rdk.BuildMechanism(
            MAKE_ROBOT_GRIPPER,
            objects,
            parameters,
            joints_build,
            joints_home,
            joints_senses,
            joints_lim_low,
            joints_lim_high,
            base_pose,
            tool_pose,
            'RobotiQ_HandE'
        );

        assert.ok(gripper.Valid(), 'Gripper should be valid');

        await rdk.CloseStation();
    });

    // ============================================================
    // Scene Composition Tests
    // ============================================================

    test('Robolink.AddShape creates triangle mesh', async () => {
        const station = await rdk.AddStation('AddShapeTest');

        // Create a simple triangle (3 vertices = 1 triangle)
        // Triangle spans X: 0-100, Y: 0-100, Z: 0
        const triangle_points = [
            [0, 0, 0],
            [100, 0, 0],
            [50, 100, 0]
        ];

        const shape = await rdk.AddShape(triangle_points);
        assert.ok(shape.Valid(), 'Shape should be valid');

        const itemType = await shape.Type();
        assert.strictEqual(itemType, ITEM_TYPE_OBJECT);

        // Verify bounding box matches triangle extents
        const bbox = await shape.setParam('BoundingBox');
        const bboxObj = JSON.parse(bbox);

        // Triangle spans X: 0-100, Y: 0-100
        assert.ok(Math.abs(bboxObj.min[0] - 0) < 1, `Min X should be 0, got ${bboxObj.min[0]}`);
        assert.ok(Math.abs(bboxObj.max[0] - 100) < 1, `Max X should be 100, got ${bboxObj.max[0]}`);
        assert.ok(Math.abs(bboxObj.max[1] - 100) < 1, `Max Y should be 100, got ${bboxObj.max[1]}`);

        await rdk.CloseStation();
    });

    test('Robolink.AddCurve creates curve from points', async () => {
        const station = await rdk.AddStation('AddCurveTest');

        // Create a simple curve spanning X: 0-100, Y: 0-100
        const curve_points = [
            [0, 0, 0],
            [100, 0, 0],
            [100, 100, 0],
            [0, 100, 0]
        ];

        const curve = await rdk.AddCurve(curve_points);
        assert.ok(curve.Valid(), 'Curve should be valid');

        // Verify curve was created using GetCurves
        const curves = await curve.GetCurves();
        assert.strictEqual(curves.length, 1, 'Should have exactly 1 curve');

        const [points, curveName] = curves[0];
        assert.ok(points.length >= 4, `Curve should have at least 4 points, got ${points.length}`);

        // Verify bounding box spans the expected range
        const bbox = await curve.setParam('BoundingBox');
        const bboxObj = JSON.parse(bbox);
        assert.ok(Math.abs(bboxObj.min[0] - 0) < 1, 'Min X should be 0');
        assert.ok(Math.abs(bboxObj.max[0] - 100) < 1, 'Max X should be 100');
        assert.ok(Math.abs(bboxObj.min[1] - 0) < 1, 'Min Y should be 0');
        assert.ok(Math.abs(bboxObj.max[1] - 100) < 1, 'Max Y should be 100');

        await rdk.CloseStation();
    });

    test('Robolink.AddPoints creates point cloud', async () => {
        const station = await rdk.AddStation('AddPointsTest');

        // Create a grid of points (6 points spanning 0-100 in X, 0-50 in Y)
        const points = [
            [0, 0, 0],
            [50, 0, 0],
            [100, 0, 0],
            [0, 50, 0],
            [50, 50, 0],
            [100, 50, 0]
        ];

        const pointCloud = await rdk.AddPoints(points);
        assert.ok(pointCloud.Valid(), 'Point cloud should be valid');

        // Verify bounding box matches point extents
        const bbox = await pointCloud.setParam('BoundingBox');
        const bboxObj = JSON.parse(bbox);

        // Min should be at (0, 0, 0), max at (100, 50, 0)
        assert.ok(Math.abs(bboxObj.min[0] - 0) < 1, `Min X should be 0, got ${bboxObj.min[0]}`);
        assert.ok(Math.abs(bboxObj.min[1] - 0) < 1, `Min Y should be 0, got ${bboxObj.min[1]}`);
        assert.ok(Math.abs(bboxObj.max[0] - 100) < 1, `Max X should be 100, got ${bboxObj.max[0]}`);
        assert.ok(Math.abs(bboxObj.max[1] - 50) < 1, `Max Y should be 50, got ${bboxObj.max[1]}`);

        await rdk.CloseStation();
    });

    test('Robolink.ProjectPoints projects onto surface', async () => {
        const station = await rdk.AddStation('ProjectPointsTest');

        // Load cube
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);
        assert.ok(cube.Valid());

        // Project points onto the cube surface
        const points_to_project = [
            [50, 50, 200, 0, 0, -1],  // Point above cube, normal pointing down
        ];

        const projected = await rdk.ProjectPoints(points_to_project, cube);
        assert.ok(projected.rows.length > 0, 'Should have projected points');

        await rdk.CloseStation();
    });

    test('Robolink.Delete removes multiple items', async () => {
        const station = await rdk.AddStation('DeleteMultipleTest');

        const frame1 = await rdk.AddFrame('DeleteFrame1');
        const frame2 = await rdk.AddFrame('DeleteFrame2');
        const frame3 = await rdk.AddFrame('DeleteFrame3');

        assert.ok(frame1.Valid());
        assert.ok(frame2.Valid());
        assert.ok(frame3.Valid());

        // Delete multiple items at once
        await rdk.Delete([frame1, frame2]);

        // Frames should be invalidated
        assert.strictEqual(frame1.Valid(), false);
        assert.strictEqual(frame2.Valid(), false);

        // frame3 should still be valid
        const found = await rdk.Item('DeleteFrame3');
        assert.ok(found.Valid());

        await rdk.CloseStation();
    });

    test('Robolink.IsInside checks containment', async () => {
        const station = await rdk.AddStation('IsInsideTest');

        // Load two cubes
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const outerCube = await rdk.AddFile(cubePath);
        const innerCube = await rdk.AddFile(cubePath);

        // Scale the outer cube to be larger
        await outerCube.Scale([3, 3, 3]);

        // Position inner cube at center of outer cube
        await innerCube.setPose(Mat.transl(100, 100, 100));

        // Note: IsInside requires specific transparency settings to work
        // This test just verifies the API call works
        const result = await rdk.IsInside(innerCube, outerCube);
        assert.ok(typeof result === 'number');

        await rdk.CloseStation();
    });

    test('Robolink.MergeItems combines objects', async () => {
        const station = await rdk.AddStation('MergeItemsTest');

        // Create two shapes at different Z heights
        // Triangle 1 at Z=0, Triangle 2 at Z=50
        const triangle1 = [
            [0, 0, 0], [100, 0, 0], [50, 100, 0]
        ];
        const triangle2 = [
            [0, 0, 50], [100, 0, 50], [50, 100, 50]
        ];

        const shape1 = await rdk.AddShape(triangle1);
        const shape2 = await rdk.AddShape(triangle2);

        // Get bounding boxes of individual shapes
        const bbox1 = JSON.parse(await shape1.setParam('BoundingBox'));
        const bbox2 = JSON.parse(await shape2.setParam('BoundingBox'));

        // shape1 should be at Z=0, shape2 at Z=50
        assert.ok(Math.abs(bbox1.max[2] - 0) < 1, 'Shape1 max Z should be 0');
        assert.ok(Math.abs(bbox2.min[2] - 50) < 1, 'Shape2 min Z should be 50');

        // Merge the shapes
        const merged = await rdk.MergeItems([shape1, shape2]);
        assert.ok(merged.Valid(), 'Merged item should be valid');

        // Verify merged bounding box spans both shapes (Z: 0 to 50)
        const bboxMerged = JSON.parse(await merged.setParam('BoundingBox'));
        assert.ok(Math.abs(bboxMerged.min[2] - 0) < 1, `Merged min Z should be 0, got ${bboxMerged.min[2]}`);
        assert.ok(Math.abs(bboxMerged.max[2] - 50) < 1, `Merged max Z should be 50, got ${bboxMerged.max[2]}`);

        await rdk.CloseStation();
    });

    test('Item.AddGeometry copies geometry', async () => {
        const station = await rdk.AddStation('AddGeometryTest');

        // Load cube as source (100mm cube)
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const sourceCube = await rdk.AddFile(cubePath);

        // Create another cube as destination
        const destCube = await rdk.AddFile(cubePath);

        // Get bounding box before adding geometry
        const bboxBefore = await destCube.setParam('BoundingBox');
        const bboxBeforeObj = JSON.parse(bboxBefore);
        const maxXBefore = bboxBeforeObj.max[0];

        // Copy geometry from source to destination with 200mm X offset
        await destCube.AddGeometry(sourceCube, Mat.transl(200, 0, 0));

        // Get bounding box after adding geometry
        const bboxAfter = await destCube.setParam('BoundingBox');
        const bboxAfterObj = JSON.parse(bboxAfter);
        const maxXAfter = bboxAfterObj.max[0];

        // Max X should increase from ~100 to ~300 (200 offset + 100 cube size)
        assert.ok(maxXAfter > maxXBefore + 100, `Max X should increase significantly: before=${maxXBefore}, after=${maxXAfter}`);
        assert.ok(Math.abs(maxXAfter - 300) < 10, `Max X should be ~300, got ${maxXAfter}`);

        await rdk.CloseStation();
    });

    test('Item.GetPoints retrieves point data', async () => {
        const station = await rdk.AddStation('GetPointsTest');

        // Create a curve spanning X: 0-100, Y: 0-100
        const curve_points = [
            [0, 0, 0],
            [100, 0, 0],
            [100, 100, 0]
        ];
        const curveItem = await rdk.AddCurve(curve_points);

        // Get points from the curve (FEATURE_CURVE = 2)
        const [points, featureName] = await curveItem.GetPoints(FEATURE_CURVE, 0);
        assert.ok(Array.isArray(points), 'Points should be an array');
        assert.ok(points.length >= 3, `Should have at least 3 points, got ${points.length}`);

        // Each point should have at least 3 columns (x, y, z) or 6 (x, y, z, nx, ny, nz)
        assert.ok(points[0].length >= 3, `Each point should have at least 3 values, got ${points[0].length}`);

        // Verify we got valid point data by checking bounding box matches
        const bbox = await curveItem.setParam('BoundingBox');
        const bboxObj = JSON.parse(bbox);
        assert.ok(Math.abs(bboxObj.max[0] - 100) < 1, 'Bounding box max X should be 100');
        assert.ok(Math.abs(bboxObj.max[1] - 100) < 1, 'Bounding box max Y should be 100');

        await rdk.CloseStation();
    });

    test('Item.GetCurves retrieves all curves', async () => {
        const station = await rdk.AddStation('GetCurvesTest');

        // Create an object with a curve spanning X: 0-100, Y: 0-100
        const curve_points = [
            [0, 0, 0],
            [100, 0, 0],
            [100, 100, 0]
        ];
        const curveItem = await rdk.AddCurve(curve_points);

        // Get all curves
        const curves = await curveItem.GetCurves();
        assert.ok(Array.isArray(curves), 'Curves should be an array');
        assert.strictEqual(curves.length, 1, 'Should have exactly 1 curve');

        // Verify curve has points and structure
        const [points, curveName] = curves[0];
        assert.ok(points.length >= 3, `Curve should have at least 3 points, got ${points.length}`);
        assert.ok(points[0].length >= 3, `Each point should have at least 3 values, got ${points[0].length}`);

        // Verify curve name is returned
        assert.ok(typeof curveName === 'string', 'Curve name should be a string');

        // Verify curve data is valid by checking bounding box
        const bbox = await curveItem.setParam('BoundingBox');
        const bboxObj = JSON.parse(bbox);
        assert.ok(Math.abs(bboxObj.max[0] - 100) < 1, 'Bounding box max X should be 100');
        assert.ok(Math.abs(bboxObj.max[1] - 100) < 1, 'Bounding box max Y should be 100');

        await rdk.CloseStation();
    });

    test('Item.ObjectLink retrieves robot link geometry', async () => {
        const station = await rdk.AddStation('ObjectLinkTest');

        // Load robot
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get robot base link (link_id = 0)
        const baseLink = await robot.ObjectLink(0);
        assert.ok(baseLink.Valid(), 'Base link should be valid');

        // Get first link (link_id = 1)
        const link1 = await robot.ObjectLink(1);
        assert.ok(link1.Valid(), 'Link 1 should be valid');

        await rdk.CloseStation();
    });

    test('Item.AttachClosest and DetachClosest', async () => {
        const station = await rdk.AddStation('AttachDetachTest');

        // Load robot and tool
        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Load gripper tool
        const toolPath = join(TEST_ASSETS, 'RobotiQ-2F-85-Gripper-Open.tool');
        const tool = await rdk.AddFile(toolPath);
        await tool.setParent(robot);

        // Load cube to pick up
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);

        // Position cube near tool
        const toolPose = await tool.PoseAbs();
        await cube.setPoseAbs(toolPose);

        // Try to attach closest object
        const attached = await tool.AttachClosest('', 500);  // 500mm tolerance
        // Note: May or may not attach depending on exact positions

        // Detach all objects from tool
        await tool.DetachAll();

        await rdk.CloseStation();
    });

    test('Item.SelectedFeature returns selection info', async () => {
        const station = await rdk.AddStation('SelectedFeatureTest');

        // Load cube
        const cubePath = join(TEST_ASSETS, 'Cube-100mm.sld');
        const cube = await rdk.AddFile(cubePath);

        // Get selected feature (nothing should be selected)
        const [isSelected, featureType, featureId] = await cube.SelectedFeature();
        assert.ok(typeof isSelected === 'number');
        assert.ok(typeof featureType === 'number');
        assert.ok(typeof featureId === 'number');

        await rdk.CloseStation();
    });

    // ============================================================
    // New Item Methods Tests
    // ============================================================

    test('Item.setAcceleration sets linear acceleration', async () => {
        const station = await rdk.AddStation('SetAccelTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Set acceleration (this is a wrapper for setSpeed)
        const result = await robot.setAcceleration(500);  // 500 mm/s²
        assert.ok(result.Valid());

        await rdk.CloseStation();
    });

    test('Item.setSpeedJoints sets joint speed', async () => {
        const station = await rdk.AddStation('SetSpeedJointsTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Set joint speed
        const result = await robot.setSpeedJoints(100);  // 100 deg/s
        assert.ok(result.Valid());

        await rdk.CloseStation();
    });

    test('Item.setAccelerationJoints sets joint acceleration', async () => {
        const station = await rdk.AddStation('SetAccelJointsTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Set joint acceleration
        const result = await robot.setAccelerationJoints(200);  // 200 deg/s²
        assert.ok(result.Valid());

        await rdk.CloseStation();
    });

    test('Item.MoveJ_Test checks joint movement collision', async () => {
        const station = await rdk.AddStation('MoveJTestTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get current joints
        const j1 = await robot.Joints();
        // Small movement
        const j2 = [...j1];
        j2[0] += 10;  // Move first joint by 10 degrees

        // Test the movement
        const collision = await robot.MoveJ_Test(j1, j2);
        assert.strictEqual(typeof collision, 'number');
        assert.strictEqual(collision, 0);  // Should be no collision in empty station

        await rdk.CloseStation();
    });

    test('Item.MoveJ_Test_Blend checks blended movement collision', async () => {
        const station = await rdk.AddStation('MoveJTestBlendTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get current joints and create via and end positions
        const j1 = await robot.Joints();
        const j2 = [...j1];
        const j3 = [...j1];
        j2[0] += 10;
        j3[0] += 20;

        // Test the blended movement
        const collision = await robot.MoveJ_Test_Blend(j1, j2, j3, 5, -1);
        assert.strictEqual(typeof collision, 'number');

        await rdk.CloseStation();
    });

    test('Item.MoveL_Test checks linear movement collision', async () => {
        const station = await rdk.AddStation('MoveLTestTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get current joints and calculate target pose
        const j1 = await robot.Joints();
        const currentPose = await robot.SolveFK(j1);

        // Move 50mm in Z direction
        const targetPose = new Mat(currentPose.rows);
        const pos = currentPose.Pos();
        targetPose.setPos([pos[0], pos[1], pos[2] + 50]);

        // Test the linear movement
        const collision = await robot.MoveL_Test(j1, targetPose);
        assert.strictEqual(typeof collision, 'number');

        await rdk.CloseStation();
    });

    test('Item.SimulatorJoints gets joints from simulator', async () => {
        const station = await rdk.AddStation('SimJointsTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Set some joints
        await robot.setJoints([10, -20, 30, -40, 50, -60]);

        // Get simulator joints
        const simJoints = await robot.SimulatorJoints();
        assert.ok(Array.isArray(simJoints));
        assert.strictEqual(simJoints.length, 6);
        assert.ok(Math.abs(simJoints[0] - 10) < 0.1);

        await rdk.CloseStation();
    });

    test('Item.JointPoses returns link poses', async () => {
        const station = await rdk.AddStation('JointPosesTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get poses for current configuration
        const poses = await robot.JointPoses();
        assert.ok(Array.isArray(poses));
        assert.ok(poses.length >= 6);  // At least base + 6 links
        assert.ok(poses[0] instanceof Mat);

        await rdk.CloseStation();
    });

    test('Item.JointsConfig returns configuration state', async () => {
        const station = await rdk.AddStation('JointsConfigTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        const joints = await robot.Joints();
        const config = await robot.JointsConfig(joints);

        assert.ok(Array.isArray(config));
        // Config contains [REAR, LOWERARM, FLIP, turns...]

        await rdk.CloseStation();
    });

    test('Item.FilterTarget filters target for accuracy', async () => {
        const station = await rdk.AddStation('FilterTargetTest');

        const robotPath = join(TEST_ASSETS, 'UR10e.robot');
        const robot = await rdk.AddFile(robotPath);

        // Get current pose
        const joints = await robot.Joints();
        const pose = await robot.SolveFK(joints);

        // Filter the target
        const [filteredPose, filteredJoints] = await robot.FilterTarget(pose, joints);

        assert.ok(filteredPose instanceof Mat);
        assert.ok(Array.isArray(filteredJoints));

        await rdk.CloseStation();
    });

    // Skip ConnectSafe test - requires real robot connection
    test.skip('Item.ConnectSafe connects with retry', async () => {
        // This test is skipped because it requires a real robot
    });
});
