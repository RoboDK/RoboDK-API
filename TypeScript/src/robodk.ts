// robodk.ts
// RoboDK TypeScript API - Ported from Python
// Source of truth: robodk-api/Python/robodk/robolink.py

import * as net from 'net';
import { spawn, ChildProcess } from 'child_process';

// ============================================================
// Constants - Tree item types
// ============================================================
export const ITEM_TYPE_STATION = 1;
export const ITEM_TYPE_ROBOT = 2;
export const ITEM_TYPE_FRAME = 3;
export const ITEM_TYPE_TOOL = 4;
export const ITEM_TYPE_OBJECT = 5;
export const ITEM_TYPE_TARGET = 6;
export const ITEM_TYPE_CURVE = 7;
export const ITEM_TYPE_PROGRAM = 8;
export const ITEM_TYPE_INSTRUCTION = 9;
export const ITEM_TYPE_PROGRAM_PYTHON = 10;
export const ITEM_TYPE_MACHINING = 11;
export const ITEM_TYPE_BALLBARVALIDATION = 12;
export const ITEM_TYPE_CALIBPROJECT = 13;
export const ITEM_TYPE_VALID_ISO9283 = 14;
export const ITEM_TYPE_FOLDER = 17;
export const ITEM_TYPE_ROBOT_ARM = 18;
export const ITEM_TYPE_CAMERA = 19;
export const ITEM_TYPE_GENERIC = 20;
export const ITEM_TYPE_ROBOT_AXES = 21;
export const ITEM_TYPE_NOTES = 22;

// ============================================================
// Constants - Instruction types
// ============================================================
export const INS_TYPE_INVALID = -1;
export const INS_TYPE_MOVE = 0;
export const INS_TYPE_MOVEC = 1;
export const INS_TYPE_CHANGESPEED = 2;
export const INS_TYPE_CHANGEFRAME = 3;
export const INS_TYPE_CHANGETOOL = 4;
export const INS_TYPE_CHANGEROBOT = 5;
export const INS_TYPE_PAUSE = 6;
export const INS_TYPE_EVENT = 7;
export const INS_TYPE_CODE = 8;
export const INS_TYPE_PRINT = 9;
export const INS_TYPE_ROUNDING = 10;
export const INS_TYPE_IO = 11;
export const INS_TYPE_CUSTOM = 12;

// ============================================================
// Constants - Move types
// ============================================================
export const MOVE_TYPE_INVALID = -1;
export const MOVE_TYPE_JOINT = 1;
export const MOVE_TYPE_LINEAR = 2;
export const MOVE_TYPE_CIRCULAR = 3;
export const MOVE_TYPE_LINEARSEARCH = 5;

// ============================================================
// Constants - Station parameters request
// ============================================================
export const PATH_OPENSTATION = 'PATH_OPENSTATION';
export const FILE_OPENSTATION = 'FILE_OPENSTATION';
export const PATH_DESKTOP = 'PATH_DESKTOP';
export const PATH_LIBRARY = 'PATH_LIBRARY';

// ============================================================
// Constants - Script execution types
// ============================================================
export const RUNMODE_SIMULATE = 1;
export const RUNMODE_QUICKVALIDATE = 2;
export const RUNMODE_MAKE_ROBOTPROG = 3;
export const RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4;
export const RUNMODE_MAKE_ROBOTPROG_AND_START = 5;
export const RUNMODE_RUN_ROBOT = 6;

// ============================================================
// Constants - Program execution type
// ============================================================
export const PROGRAM_RUN_ON_SIMULATOR = 1;
export const PROGRAM_RUN_ON_ROBOT = 2;

// ============================================================
// Constants - Robot connection status
// ============================================================
export const ROBOTCOM_PROBLEMS = -3;
export const ROBOTCOM_DISCONNECTED = -2;
export const ROBOTCOM_NOT_CONNECTED = -1;
export const ROBOTCOM_READY = 0;
export const ROBOTCOM_WORKING = 1;
export const ROBOTCOM_WAITING = 2;
export const ROBOTCOM_UNKNOWN = -1000;

// ============================================================
// Constants - TCP calibration methods
// ============================================================
export const CALIBRATE_TCP_BY_POINT = 0;
export const CALIBRATE_TCP_BY_PLANE = 1;
export const CALIBRATE_TCP_BY_PLANE_SCARA = 4;

// ============================================================
// Constants - Reference frame calibration methods
// ============================================================
export const CALIBRATE_FRAME_3P_P1_ON_X = 0;
export const CALIBRATE_FRAME_3P_P1_ORIGIN = 1;
export const CALIBRATE_FRAME_6P = 2;
export const CALIBRATE_TURNTABLE = 3;
export const CALIBRATE_TURNTABLE_2X = 4;

// ============================================================
// Constants - Projection types
// ============================================================
export const PROJECTION_NONE = 0;
export const PROJECTION_CLOSEST = 1;
export const PROJECTION_ALONG_NORMAL = 2;
export const PROJECTION_ALONG_NORMAL_RECALC = 3;
export const PROJECTION_CLOSEST_RECALC = 4;
export const PROJECTION_RECALC = 5;

// ============================================================
// Constants - Euler types
// ============================================================
export const JOINT_FORMAT = -1;
export const EULER_RX_RYp_RZpp = 0;
export const EULER_RZ_RYp_RXpp = 1;
export const EULER_RZ_RYp_RZpp = 2;
export const EULER_RZ_RXp_RZpp = 3;
export const EULER_RX_RY_RZ = 4;
export const EULER_RZ_RY_RX = 5;
export const EULER_QUEATERNION = 6;

// ============================================================
// Constants - Window states
// ============================================================
export const WINDOWSTATE_HIDDEN = -1;
export const WINDOWSTATE_SHOW = 0;
export const WINDOWSTATE_MINIMIZED = 1;
export const WINDOWSTATE_NORMAL = 2;
export const WINDOWSTATE_MAXIMIZED = 3;
export const WINDOWSTATE_FULLSCREEN = 4;
export const WINDOWSTATE_CINEMA = 5;
export const WINDOWSTATE_FULLSCREEN_CINEMA = 6;
export const WINDOWSTATE_VIDEO = 7;

// ============================================================
// Constants - Instruction program call type
// ============================================================
export const INSTRUCTION_CALL_PROGRAM = 0;
export const INSTRUCTION_INSERT_CODE = 1;
export const INSTRUCTION_START_THREAD = 2;
export const INSTRUCTION_COMMENT = 3;
export const INSTRUCTION_SHOW_MESSAGE = 4;

// ============================================================
// Constants - Object selection features
// ============================================================
export const FEATURE_NONE = 0;
export const FEATURE_SURFACE = 1;
export const FEATURE_CURVE = 2;
export const FEATURE_POINT = 3;
export const FEATURE_OBJECT_MESH = 7;
export const FEATURE_SURFACE_PREVIEW = 8;
export const FEATURE_MESH = 9;
export const FEATURE_HOVER_OBJECT_MESH = 10;
export const FEATURE_HOVER_OBJECT = 11;

// ============================================================
// Constants - Spray gun simulation
// ============================================================
export const SPRAY_OFF = 0;
export const SPRAY_ON = 1;

// ============================================================
// Constants - Collision checking state
// ============================================================
export const COLLISION_OFF = 0;
export const COLLISION_ON = 1;

// ============================================================
// Constants - RoboDK Window Flags
// ============================================================
export const FLAG_ROBODK_TREE_ACTIVE = 1;
export const FLAG_ROBODK_3DVIEW_ACTIVE = 2;
export const FLAG_ROBODK_LEFT_CLICK = 4;
export const FLAG_ROBODK_RIGHT_CLICK = 8;
export const FLAG_ROBODK_DOUBLE_CLICK = 16;
export const FLAG_ROBODK_MENU_ACTIVE = 32;
export const FLAG_ROBODK_MENUFILE_ACTIVE = 64;
export const FLAG_ROBODK_MENUEDIT_ACTIVE = 128;
export const FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256;
export const FLAG_ROBODK_MENUTOOLS_ACTIVE = 512;
export const FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024;
export const FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048;
export const FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096;
export const FLAG_ROBODK_TREE_VISIBLE = 8192;
export const FLAG_ROBODK_REFERENCES_VISIBLE = 16384;
export const FLAG_ROBODK_STATUSBAR_VISIBLE = 32768;
export const FLAG_ROBODK_NONE = 0x00;
export const FLAG_ROBODK_ALL = 0xFFFF;
export const FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE;

// ============================================================
// Constants - RoboDK Item Flags
// ============================================================
export const FLAG_ITEM_SELECTABLE = 1;
export const FLAG_ITEM_EDITABLE = 2;
export const FLAG_ITEM_DRAGALLOWED = 4;
export const FLAG_ITEM_DROPALLOWED = 8;
export const FLAG_ITEM_ENABLED = 32;
export const FLAG_ITEM_AUTOTRISTATE = 64;
export const FLAG_ITEM_NOCHILDREN = 128;
export const FLAG_ITEM_USERTRISTATE = 256;
export const FLAG_ITEM_NONE = 0;
export const FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1;

// ============================================================
// Constants - Robot/mechanism types
// ============================================================
export const MAKE_ROBOT_1R = 1;
export const MAKE_ROBOT_2R = 2;
export const MAKE_ROBOT_3R = 3;
export const MAKE_ROBOT_1T = 4;
export const MAKE_ROBOT_2T = 5;
export const MAKE_ROBOT_3T = 6;
export const MAKE_ROBOT_6DOF = 7;
export const MAKE_ROBOT_7DOF = 8;
export const MAKE_ROBOT_SCARA = 9;
export const MAKE_ROBOT_GRIPPER = 10;
export const MAKE_ROBOT_6COBOT = 11;
export const MAKE_ROBOT_1T1R = 12;
export const MAKE_ROBOT_5XCNC = 13;
export const MAKE_ROBOT_3T1R = 15;
export const MAKE_ROBOT_GENERIC = 16;

// ============================================================
// Constants - Path Error bit mask
// ============================================================
export const ERROR_KINEMATIC = 0b001;
export const ERROR_PATH_LIMIT = 0b010;
export const ERROR_PATH_SINGULARITY = 0b100;
export const ERROR_PATH_NEARSINGULARITY = 0b1000;
export const ERROR_COLLISION = 0b100000;

// ============================================================
// Constants - Interactive selection option
// ============================================================
export const SELECT_RESET = -1;
export const SELECT_NONE = 0;
export const SELECT_RECTANGLE = 1;
export const SELECT_ROTATE = 2;
export const SELECT_ZOOM = 3;
export const SELECT_PAN = 4;
export const SELECT_MOVE = 5;
export const SELECT_MOVE_SHIFT = 6;
export const SELECT_MOVE_CLEAR = 7;

// ============================================================
// Constants - Display reference frames
// ============================================================
export const DISPLAY_REF_DEFAULT = -1;
export const DISPLAY_REF_NONE = 0;
export const DISPLAY_REF_TX = 0b001;
export const DISPLAY_REF_TY = 0b010;
export const DISPLAY_REF_TZ = 0b100;
export const DISPLAY_REF_RX = 0b001000;
export const DISPLAY_REF_RY = 0b010000;
export const DISPLAY_REF_RZ = 0b100000;
export const DISPLAY_REF_PXY = 0b001000000;
export const DISPLAY_REF_PXZ = 0b010000000;
export const DISPLAY_REF_PYZ = 0b100000000;

// ============================================================
// Constants - Visibility flags
// ============================================================
export const VISIBLE_REFERENCE_DEFAULT = -1;
export const VISIBLE_REFERENCE_ON = 1;
export const VISIBLE_REFERENCE_OFF = 0;
export const VISIBLE_ROBOT_NONE = 0;
export const VISIBLE_ROBOT_FLANGE = 0x01;
export const VISIBLE_ROBOT_AXIS_Base_3D = 0x01 << 1;
export const VISIBLE_ROBOT_AXIS_Base_REF = 0x01 << 2;
export const VISIBLE_ROBOT_AXIS_1_3D = 0x01 << 3;
export const VISIBLE_ROBOT_AXIS_1_REF = 0x01 << 4;
export const VISIBLE_ROBOT_AXIS_2_3D = 0x01 << 5;
export const VISIBLE_ROBOT_AXIS_2_REF = 0x01 << 6;
export const VISIBLE_ROBOT_AXIS_3_3D = 0x01 << 7;
export const VISIBLE_ROBOT_AXIS_3_REF = 0x01 << 8;
export const VISIBLE_ROBOT_AXIS_4_3D = 0x01 << 9;
export const VISIBLE_ROBOT_AXIS_4_REF = 0x01 << 10;
export const VISIBLE_ROBOT_AXIS_5_3D = 0x01 << 11;
export const VISIBLE_ROBOT_AXIS_5_REF = 0x01 << 12;
export const VISIBLE_ROBOT_AXIS_6_3D = 0x01 << 13;
export const VISIBLE_ROBOT_AXIS_6_REF = 0x01 << 14;
export const VISIBLE_ROBOT_AXIS_7_3D = 0x01 << 15;
export const VISIBLE_ROBOT_AXIS_7_REF = 0x02 << 16;
export const VISIBLE_ROBOT_DEFAULT = 0x2AAAAAAB;
export const VISIBLE_ROBOT_ALL = 0x7FFFFFFF;
export const VISIBLE_ROBOT_ALL_REFS = 0x15555555;

// ============================================================
// Constants - Sequence display flags
// ============================================================
export const SEQUENCE_DISPLAY_DEFAULT = -1;
export const SEQUENCE_DISPLAY_TOOL_POSES = 0;
export const SEQUENCE_DISPLAY_ROBOT_POSES = 256;
export const SEQUENCE_DISPLAY_ROBOT_JOINTS = 2048;
export const SEQUENCE_DISPLAY_COLOR_SELECTED = 1;
export const SEQUENCE_DISPLAY_COLOR_TRANSPARENT = 2;
export const SEQUENCE_DISPLAY_COLOR_GOOD = 3;
export const SEQUENCE_DISPLAY_COLOR_BAD = 4;
export const SEQUENCE_DISPLAY_OPTION_RESET = 1024;

// ============================================================
// Constants - Event Types (for event loop)
// ============================================================
export const EVENT_SELECTION_TREE_CHANGED = 1;
export const EVENT_ITEM_MOVED = 2;  // obsolete after RoboDK 4.2.0, use EVENT_ITEM_MOVED_POSE
export const EVENT_REFERENCE_PICKED = 3;
export const EVENT_REFERENCE_RELEASED = 4;
export const EVENT_TOOL_MODIFIED = 5;
export const EVENT_CREATED_ISOCUBE = 6;
export const EVENT_SELECTION_3D_CHANGED = 7;
export const EVENT_3DVIEW_MOVED = 8;
export const EVENT_ROBOT_MOVED = 9;
export const EVENT_KEY = 10;
export const EVENT_ITEM_MOVED_POSE = 11;
export const EVENT_COLLISIONMAP_RESET = 12;
export const EVENT_COLLISIONMAP_TOO_LARGE = 13;
export const EVENT_CALIB_MEASUREMENT = 14;
export const EVENT_SELECTION_3D_CLICK = 15;
export const EVENT_ITEM_CHANGED = 16;
export const EVENT_ITEM_RENAMED = 17;
export const EVENT_ITEM_VISIBILITY = 18;
export const EVENT_STATION_CHANGED = 19;
export const EVENT_PROGSLIDER_CHANGED = 20;
export const EVENT_PROGSLIDER_SET = 21;

// ============================================================
// Mat Class - 4x4 Transformation Matrix
// ============================================================

export class Mat {
    rows: number[][];

    constructor(rows?: number[][] | number, ncols?: number) {
        if (rows === undefined) {
            // Default: 4x4 identity matrix
            this.rows = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ];
        } else if (typeof rows === 'number') {
            // Create zero matrix of size rows x ncols
            const nrows = rows;
            const nc = ncols ?? nrows;
            this.rows = [];
            for (let i = 0; i < nrows; i++) {
                this.rows.push(new Array(nc).fill(0));
            }
        } else {
            // Copy from 2D array
            this.rows = rows.map(row => [...row]);
        }
    }

    Pos(): number[] {
        return [this.rows[0][3], this.rows[1][3], this.rows[2][3]];
    }

    setPos(pos: number[]): Mat {
        this.rows[0][3] = pos[0];
        this.rows[1][3] = pos[1];
        this.rows[2][3] = pos[2];
        return this;
    }

    static eye(size: number = 4): Mat {
        const m = new Mat(size, size);
        for (let i = 0; i < size; i++) {
            m.rows[i][i] = 1;
        }
        return m;
    }

    size(): [number, number] {
        return [this.rows.length, this.rows[0]?.length ?? 0];
    }

    tr(): Mat {
        const [nrows, ncols] = this.size();
        const result = new Mat(ncols, nrows);
        for (let i = 0; i < nrows; i++) {
            for (let j = 0; j < ncols; j++) {
                result.rows[j][i] = this.rows[i][j];
            }
        }
        return result;
    }

    tolist(): number[] {
        const result: number[] = [];
        for (const row of this.rows) {
            result.push(...row);
        }
        return result;
    }

    list(): number[] {
        return this.tolist();
    }

    VX(): number[] {
        return [this.rows[0][0], this.rows[1][0], this.rows[2][0]];
    }

    VY(): number[] {
        return [this.rows[0][1], this.rows[1][1], this.rows[2][1]];
    }

    VZ(): number[] {
        return [this.rows[0][2], this.rows[1][2], this.rows[2][2]];
    }

    toString(): string {
        return this.rows.map(row => row.map(v => v.toFixed(6)).join('\t')).join('\n');
    }

    /**
     * Multiply this matrix by another matrix or scalar.
     * @param mat - Matrix or scalar to multiply with
     */
    multiply(mat: Mat | number | number[]): Mat | number[] {
        if (typeof mat === 'number') {
            // Scalar multiplication
            const [m, n] = this.size();
            const result = new Mat(m, n);
            for (let i = 0; i < m; i++) {
                for (let j = 0; j < n; j++) {
                    result.rows[i][j] = this.rows[i][j] * mat;
                }
            }
            return result;
        }
        if (Array.isArray(mat)) {
            // Matrix times vector
            const szvect = mat.length;
            const m = this.rows.length;
            if (szvect + 1 === m) {
                // Extend vector with 1 for homogeneous coordinates
                const vectok = [...mat, 1];
                const result: number[] = [];
                for (let i = 0; i < m - 1; i++) {
                    let sum = 0;
                    for (let j = 0; j < m; j++) {
                        sum += this.rows[i][j] * vectok[j];
                    }
                    result.push(sum);
                }
                return result;
            } else if (szvect === m) {
                const result: number[] = [];
                for (let i = 0; i < m; i++) {
                    let sum = 0;
                    for (let j = 0; j < m; j++) {
                        sum += this.rows[i][j] * mat[j];
                    }
                    result.push(sum);
                }
                return result;
            } else {
                throw new Error('Invalid product: vector size mismatch');
            }
        }
        // Matrix multiplication
        const [matm, matn] = mat.size();
        const [m, n] = this.size();
        if (n !== matm) {
            throw new Error('Matrices cannot be multiplied (incompatible dimensions)');
        }
        const mat_t = mat.tr();
        const result = new Mat(m, matn);
        for (let i = 0; i < m; i++) {
            for (let j = 0; j < matn; j++) {
                let sum = 0;
                for (let k = 0; k < n; k++) {
                    sum += this.rows[i][k] * mat_t.rows[j][k];
                }
                result.rows[i][j] = sum;
            }
        }
        return result;
    }

    /**
     * Returns the inverse of a homogeneous transformation matrix.
     */
    invH(): Mat {
        const [m, n] = this.size();
        if (m !== 4 || n !== 4) {
            throw new Error('invH() requires a 4x4 homogeneous matrix');
        }
        // For a homogeneous matrix [R t; 0 1], the inverse is [R^T -R^T*t; 0 1]
        const result = this.tr();
        // Zero out the last row except for [3][3]
        result.rows[3][0] = 0;
        result.rows[3][1] = 0;
        result.rows[3][2] = 0;
        // Calculate -R^T * t
        const tx = this.rows[0][3];
        const ty = this.rows[1][3];
        const tz = this.rows[2][3];
        result.rows[0][3] = -(result.rows[0][0] * tx + result.rows[0][1] * ty + result.rows[0][2] * tz);
        result.rows[1][3] = -(result.rows[1][0] * tx + result.rows[1][1] * ty + result.rows[1][2] * tz);
        result.rows[2][3] = -(result.rows[2][0] * tx + result.rows[2][1] * ty + result.rows[2][2] * tz);
        return result;
    }

    /**
     * Alias for invH - returns the inverse of a homogeneous transformation matrix.
     */
    inv(): Mat {
        return this.invH();
    }

    /**
     * Returns a rotation matrix around the X axis (radians).
     * @param rx - Rotation angle in radians
     */
    static rotx(rx: number): Mat {
        const ct = Math.cos(rx);
        const st = Math.sin(rx);
        return new Mat([
            [1, 0, 0, 0],
            [0, ct, -st, 0],
            [0, st, ct, 0],
            [0, 0, 0, 1]
        ]);
    }

    /**
     * Returns a rotation matrix around the Y axis (radians).
     * @param ry - Rotation angle in radians
     */
    static roty(ry: number): Mat {
        const ct = Math.cos(ry);
        const st = Math.sin(ry);
        return new Mat([
            [ct, 0, st, 0],
            [0, 1, 0, 0],
            [-st, 0, ct, 0],
            [0, 0, 0, 1]
        ]);
    }

    /**
     * Returns a rotation matrix around the Z axis (radians).
     * @param rz - Rotation angle in radians
     */
    static rotz(rz: number): Mat {
        const ct = Math.cos(rz);
        const st = Math.sin(rz);
        return new Mat([
            [ct, -st, 0, 0],
            [st, ct, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]);
    }

    /**
     * Returns a translation matrix.
     * @param tx - Translation along X (or array [x, y, z])
     * @param ty - Translation along Y
     * @param tz - Translation along Z
     */
    static transl(tx: number | number[], ty: number = 0, tz: number = 0): Mat {
        let xx: number, yy: number, zz: number;
        if (Array.isArray(tx)) {
            xx = tx[0];
            yy = tx[1];
            zz = tx[2];
        } else {
            xx = tx;
            yy = ty;
            zz = tz;
        }
        return new Mat([
            [1, 0, 0, xx],
            [0, 1, 0, yy],
            [0, 0, 1, zz],
            [0, 0, 0, 1]
        ]);
    }
}

// ============================================================
// Robolink Class - Main interface to RoboDK
// ============================================================

export class Robolink {
    // checks that provided items exist in memory and poses are homogeneous
    SAFE_MODE: number = 1;

    // if AUTO_UPDATE is 1, updating and rendering objects the 3D scene will be delayed until 100 ms after the last call
    AUTO_UPDATE: number = 0;

    // If _SkipStatus flag is True, we are skipping the status flag for operations that only wait for the status and do not return anything
    _SkipStatus: boolean = false;

    // IP address of the simulator (localhost if it is the same computer), otherwise, use RL = Robolink('yourip') to set to a different IP
    IP: string = 'localhost';

    // port to start looking for the RoboDK API connection (Tools-Options-Other-RoboDK API)
    PORT_START: number = 20500;

    // port to stop looking for the RoboDK API connection
    PORT_END: number = 20500;

    // timeout for communication, in milliseconds (Python uses seconds, we use ms for Node.js)
    TIMEOUT: number = 10000;

    // Add Cameras as items (added option to use cameras as items at version v5.0.0)
    CAMERA_AS_ITEM: boolean = true;

    // activate nodelay option (faster, requires more resources)
    NODELAY: boolean = false;

    // file path to the robodk program (executable)
    APPLICATION_DIR: string = '';

    // Add shapes using files (faster but it uses the hard drive)
    _ADDSHAPE_VIA_FILE: boolean = false;

    // Raise an exception when a warning message is provided by RoboDK
    _RAISE_EXCEPTION_ON_WARNING: boolean = false;

    // Debug output through console
    DEBUG: boolean = false;

    // tcpip com
    COM: net.Socket | null = null;

    // Command line arguments to RoboDK, such as /NOSPLASH /NOSHOW to not display RoboDK
    ARGUMENTS: string[] = [];

    // Close standard output for RoboDK (RoboDK console output will no longer be visible)
    CLOSE_STD_OUT: boolean = false;

    // current port
    PORT: number = -1;

    // This variable holds the build id and is used for version checking
    BUILD: number = 0;

    // If not null, a new RoboDK instance was spawned when initiating connection
    NEW_INSTANCE: ChildProcess | null = null;

    // If true, new instances of RoboDK will be closed when this object is deleted
    QUIT_ON_CLOSE: boolean = false;

    // Remember last status message
    LAST_STATUS_MESSAGE: string = '';

    // TypeScript-specific: buffer for partial reads
    private _buffer: Buffer = Buffer.alloc(0);

    // ============================================================
    // Protocol helper: Read exactly n bytes from buffer/socket
    // ============================================================
    private async _recv(n: number): Promise<Buffer> {
        while (this._buffer.length < n) {
            const chunk = await new Promise<Buffer>((resolve, reject) => {
                if (!this.COM) {
                    reject(new Error('Not connected'));
                    return;
                }
                const onData = (data: Buffer) => {
                    this.COM?.off('data', onData);
                    this.COM?.off('error', onError);
                    resolve(data);
                };
                const onError = (err: Error) => {
                    this.COM?.off('data', onData);
                    this.COM?.off('error', onError);
                    reject(err);
                };
                this.COM.once('data', onData);
                this.COM.once('error', onError);
            });
            this._buffer = Buffer.concat([this._buffer, chunk]);
        }
        const result = this._buffer.subarray(0, n);
        this._buffer = this._buffer.subarray(n);
        return result;
    }

    // ============================================================
    // Protocol: Send/Receive Line
    // ============================================================
    _send_line(line: string): void {
        if (!this.COM) throw new Error('Not connected');
        const str = line.replace(/\n/g, '<br>') + '\n';
        this.COM.write(Buffer.from(str, 'utf-8'));
    }

    async _rec_line(): Promise<string> {
        const bytes: number[] = [];
        while (true) {
            const buf = await this._recv(1);
            if (buf[0] === 0x0A) break; // LF
            bytes.push(buf[0]);
        }
        return Buffer.from(bytes).toString('utf-8');
    }

    // ============================================================
    // Protocol: Send/Receive Item (64-bit pointer)
    // ============================================================
    _send_item(item: Item | null): void {
        if (!this.COM) throw new Error('Not connected');
        const buf = Buffer.alloc(8);
        const ptr = item ? item.item : BigInt(0);
        buf.writeBigUInt64BE(ptr, 0);
        this.COM.write(buf);
    }

    async _rec_item(): Promise<Item> {
        const ptrBuf = await this._recv(8);
        const ptr = ptrBuf.readBigUInt64BE(0);
        const typeBuf = await this._recv(4);
        const itemtype = typeBuf.readInt32BE(0);
        return new Item(this, ptr, itemtype);
    }

    // ============================================================
    // Protocol: Send/Receive Pose (4x4 matrix, column-major doubles)
    // ============================================================
    _send_pose(pose: Mat): void {
        if (!this.COM) throw new Error('Not connected');
        const buf = Buffer.alloc(128);
        let offset = 0;
        // Column-major order
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 4; i++) {
                buf.writeDoubleBE(pose.rows[i][j], offset);
                offset += 8;
            }
        }
        this.COM.write(buf);
    }

    async _rec_pose(): Promise<Mat> {
        const buf = await this._recv(128);
        const pose = new Mat(4, 4);
        let offset = 0;
        // Column-major order
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 4; i++) {
                pose.rows[i][j] = buf.readDoubleBE(offset);
                offset += 8;
            }
        }
        return pose;
    }

    // ============================================================
    // Protocol: Send/Receive XYZ (3 doubles)
    // ============================================================
    _send_xyz(pos: number[]): void {
        if (!this.COM) throw new Error('Not connected');
        const buf = Buffer.alloc(24);
        for (let i = 0; i < 3; i++) {
            buf.writeDoubleBE(pos[i], i * 8);
        }
        this.COM.write(buf);
    }

    async _rec_xyz(): Promise<number[]> {
        const buf = await this._recv(24);
        return [
            buf.readDoubleBE(0),
            buf.readDoubleBE(8),
            buf.readDoubleBE(16)
        ];
    }

    // ============================================================
    // Protocol: Send/Receive Int (32-bit, big-endian)
    // ============================================================
    _send_int(value: number): void {
        if (!this.COM) throw new Error('Not connected');
        const buf = Buffer.alloc(4);
        buf.writeInt32BE(Math.round(value), 0);
        this.COM.write(buf);
    }

    async _rec_int(): Promise<number> {
        const buf = await this._recv(4);
        return buf.readInt32BE(0);
    }

    async _rec_double(): Promise<number> {
        const buf = await this._recv(8);
        return buf.readDoubleBE(0);
    }

    // ============================================================
    // Protocol: Send/Receive Pointer (64-bit)
    // ============================================================
    _send_ptr(ptr: number | bigint): void {
        if (!this.COM) throw new Error('Not connected');
        const buf = Buffer.alloc(8);
        buf.writeBigInt64BE(BigInt(ptr), 0);
        this.COM.write(buf);
    }

    async _rec_ptr(): Promise<bigint> {
        const buf = await this._recv(8);
        return buf.readBigInt64BE(0);
    }

    // ============================================================
    // Protocol: Receive raw bytes (for image data etc.)
    // ============================================================
    async _rec_bytes(): Promise<Buffer> {
        const size = await this._rec_int();
        if (size <= 0) {
            return Buffer.alloc(0);
        }
        return await this._recv(size);
    }

    // ============================================================
    // Protocol: Send/Receive Array (int count + doubles)
    // ============================================================
    _send_array(values: number[]): void {
        this._send_int(values.length);
        if (values.length > 0) {
            if (!this.COM) throw new Error('Not connected');
            const buf = Buffer.alloc(values.length * 8);
            for (let i = 0; i < values.length; i++) {
                buf.writeDoubleBE(values[i], i * 8);
            }
            this.COM.write(buf);
        }
    }

    async _rec_array(): Promise<number[]> {
        const nvalues = await this._rec_int();
        if (nvalues > 0) {
            const buf = await this._recv(nvalues * 8);
            const values: number[] = [];
            for (let i = 0; i < nvalues; i++) {
                values.push(buf.readDoubleBE(i * 8));
            }
            return values;
        }
        return [];
    }

    _send_matrix(matrix: number[][]): void {
        if (!matrix || matrix.length === 0) {
            this._send_int(0);
            this._send_int(0);
            return;
        }
        if (!this.COM) throw new Error('Not connected');
        const size1 = matrix.length;
        const size2 = matrix[0].length;
        this._send_int(size1);
        this._send_int(size2);
        // Column-major order
        const buf = Buffer.alloc(size1 * size2 * 8);
        let cnt = 0;
        for (let j = 0; j < size2; j++) {
            for (let i = 0; i < size1; i++) {
                buf.writeDoubleBE(matrix[i][j], cnt * 8);
                cnt++;
            }
        }
        this.COM.write(buf);
    }

    async _rec_matrix(): Promise<number[][]> {
        const size1 = await this._rec_int();
        const size2 = await this._rec_int();
        const recvsize = size1 * size2 * 8;
        if (recvsize > 0) {
            const buf = await this._recv(recvsize);
            const matrix: number[][] = [];
            for (let i = 0; i < size1; i++) {
                matrix.push([]);
            }
            let cnt = 0;
            // Column-major order
            for (let j = 0; j < size2; j++) {
                for (let i = 0; i < size1; i++) {
                    matrix[i][j] = buf.readDoubleBE(cnt * 8);
                    cnt++;
                }
            }
            return matrix;
        }
        return [];
    }

    // ============================================================
    // Protocol: Check Status
    // ============================================================
    async _check_status(): Promise<number> {
        const status = await this._rec_int();
        if (status === 0) {
            this.LAST_STATUS_MESSAGE = '';
            return 0;
        }
        if (status > 0 && status < 10) {
            if (status === 1) {
                this.LAST_STATUS_MESSAGE = 'Invalid item provided: The item identifier provided is not valid or it does not exist.';
            } else if (status === 2) {
                this.LAST_STATUS_MESSAGE = await this._rec_line();
                console.warn('WARNING: ' + this.LAST_STATUS_MESSAGE);
                return 0;
            } else if (status === 3) {
                this.LAST_STATUS_MESSAGE = await this._rec_line();
                throw new Error(this.LAST_STATUS_MESSAGE);
            } else if (status === 9) {
                this.LAST_STATUS_MESSAGE = 'Invalid license. Purchase a license online (www.robodk.com) or contact us at info@robodk.com.';
            } else {
                this.LAST_STATUS_MESSAGE = 'Unknown error';
            }
            throw new Error(this.LAST_STATUS_MESSAGE);
        }
        if (status < 100) {
            this.LAST_STATUS_MESSAGE = await this._rec_line();
            throw new Error(this.LAST_STATUS_MESSAGE);
        }
        return status;
    }

    // ============================================================
    // Internal: Performs a linear or joint movement.
    // ============================================================
    async _moveX(target: Item | number[] | Mat, itemrobot: Item, movetype: number, blocking: boolean = true): Promise<void> {
        const command = blocking ? 'MoveXb' : 'MoveX';
        this._send_line(command);
        this._send_int(movetype);

        if (target instanceof Item) {
            // Target is an item
            this._send_int(3);
            this._send_array([]);
            this._send_item(target);
        } else if (Array.isArray(target)) {
            // Target is joints array
            this._send_int(1);
            this._send_array(target);
            this._send_item(null);
        } else if (target instanceof Mat) {
            // Target is a pose
            this._send_int(2);
            const mattr = target.tr();
            const flatPose = [...mattr.rows[0], ...mattr.rows[1], ...mattr.rows[2], ...mattr.rows[3]];
            this._send_array(flatPose);
            this._send_item(null);
        } else {
            throw new Error('Invalid target type');
        }

        this._send_item(itemrobot);
        await this._check_status();

        if (blocking) {
            // Wait for movement to complete
            const oldTimeout = this.TIMEOUT;
            this.COM?.setTimeout(360000);
            await this._check_status();
            this.COM?.setTimeout(oldTimeout);
        }
    }

    // ============================================================
    // Internal: Performs a circular movement.
    // ============================================================
    async _moveC(target1: Item | number[] | Mat, target2: Item | number[] | Mat, itemrobot: Item, blocking: boolean = true): Promise<void> {
        const command = blocking ? 'MoveCb' : 'MoveC';
        this._send_line(command);
        this._send_int(MOVE_TYPE_CIRCULAR);

        // Target 1
        if (target1 instanceof Item) {
            this._send_int(3);
            this._send_array([]);
            this._send_item(target1);
        } else if (Array.isArray(target1)) {
            this._send_int(1);
            this._send_array(target1);
            this._send_item(null);
        } else if (target1 instanceof Mat) {
            this._send_int(2);
            const mattr = target1.tr();
            const flatPose = [...mattr.rows[0], ...mattr.rows[1], ...mattr.rows[2], ...mattr.rows[3]];
            this._send_array(flatPose);
            this._send_item(null);
        }

        // Target 2
        if (target2 instanceof Item) {
            this._send_int(3);
            this._send_array([]);
            this._send_item(target2);
        } else if (Array.isArray(target2)) {
            this._send_int(1);
            this._send_array(target2);
            this._send_item(null);
        } else if (target2 instanceof Mat) {
            this._send_int(2);
            const mattr = target2.tr();
            const flatPose = [...mattr.rows[0], ...mattr.rows[1], ...mattr.rows[2], ...mattr.rows[3]];
            this._send_array(flatPose);
            this._send_item(null);
        }

        this._send_item(itemrobot);
        await this._check_status();

        if (blocking) {
            const oldTimeout = this.TIMEOUT;
            this.COM?.setTimeout(360000);
            await this._check_status();
            this.COM?.setTimeout(oldTimeout);
        }
    }

    // ============================================================
    // Constructor
    // ============================================================
    /**
     * Create a new Robolink instance.
     * @param robodk_ip - IP address of the RoboDK API server (default='localhost')
     * @param port - Port of the RoboDK API server (default=null, uses default 20500 or ROBODK_API_PORT env var)
     * @param args - Command line arguments to pass to RoboDK on startup.
     *               Example: ['-NEWINSTANCE', '-NOUI', '-SKIPINI', '-EXIT_LAST_COM']
     *               Arguments have no effect if RoboDK is already running.
     * @param robodk_path - RoboDK installation path. Defaults to platform-specific path.
     * @param close_std_out - Close RoboDK standard output (no console output will be shown)
     * @param quit_on_close - Close RoboDK when this Robolink instance disconnects.
     *                        Only has effect if this instance started RoboDK.
     */
    constructor(
        robodk_ip: string = 'localhost',
        port: number | null = null,
        args: string | string[] = [],
        robodk_path: string | null = null,
        close_std_out: boolean = false,
        quit_on_close: boolean = false
    ) {
        // Handle args as string or array (matching Python)
        if (typeof args === 'string') {
            this.ARGUMENTS = args !== '' ? [args] : [];
        } else {
            this.ARGUMENTS = [...args];
        }

        this.IP = robodk_ip;
        this.CLOSE_STD_OUT = close_std_out;
        this.QUIT_ON_CLOSE = quit_on_close;

        // Set default RoboDK path based on platform
        if (robodk_path) {
            this.APPLICATION_DIR = robodk_path;
        } else if (process.platform === 'win32') {
            this.APPLICATION_DIR = 'C:\\RoboDK\\bin\\RoboDK.exe';
        } else if (process.platform === 'darwin') {
            this.APPLICATION_DIR = '/Applications/RoboDK.app/Contents/MacOS/RoboDK';
        } else {
            this.APPLICATION_DIR = '/opt/robodk/bin/RoboDK';
        }

        // Handle port configuration (matching Python behavior)
        if (port !== null) {
            this.PORT_START = port;
            this.PORT_END = port;
            this.PORT = port;
            this.ARGUMENTS.push(`-PORT=${port}`);
        } else if (process.env.ROBODK_API_PORT) {
            const envPort = parseInt(process.env.ROBODK_API_PORT, 10);
            this.PORT_START = envPort;
            this.PORT_END = envPort;
            this.PORT = envPort;
            this.ARGUMENTS.push(`-PORT=${envPort}`);
        } else {
            // Default port range
            this.PORT_START = 20500;
            this.PORT_END = 20500;
            this.PORT = 20500;
        }
    }

    // ============================================================
    // Connection verification
    // ============================================================
    private async _verify_connection(): Promise<boolean> {
        this._send_line('RDK_API');
        this._send_array([this.SAFE_MODE, this.AUTO_UPDATE, 0]);

        const response = await this._rec_line();
        await this._rec_int(); // ver_api
        this.BUILD = await this._rec_int();
        await this._check_status();

        return response === 'RDK_API';
    }

    private _is_connected(): number {
        return this.COM ? 1 : 0;
    }

    /**
     * Start RoboDK application and wait for it to be ready
     */
    private async _startRoboDK(): Promise<void> {
        const command = [this.APPLICATION_DIR, ...this.ARGUMENTS];
        console.log('Starting ' + this.APPLICATION_DIR);

        return new Promise((resolve, reject) => {
            try {
                this.NEW_INSTANCE = spawn(command[0], command.slice(1), {
                    stdio: ['ignore', 'pipe', 'pipe'],
                    detached: false
                });

                let resolved = false;
                let emptyLines = 0;

                const finishStartup = () => {
                    // Stop listening to stdout to allow Node.js to exit
                    // when all connections are closed
                    if (this.NEW_INSTANCE?.stdout) {
                        this.NEW_INSTANCE.stdout.removeAllListeners('data');
                        this.NEW_INSTANCE.stdout.destroy();
                    }
                    if (this.NEW_INSTANCE?.stderr) {
                        this.NEW_INSTANCE.stderr.destroy();
                    }
                    // Unref the process so it doesn't keep Node.js alive
                    this.NEW_INSTANCE?.unref();
                    resolve();
                };

                const checkLine = (line: string) => {
                    if (line.toLowerCase().includes('running') && !resolved) {
                        resolved = true;
                        // Small delay after seeing "running" to ensure API is ready
                        setTimeout(finishStartup, 500);
                    }
                };

                this.NEW_INSTANCE.stdout?.on('data', (data: Buffer) => {
                    const lines = data.toString().split('\n');
                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.length > 0) {
                            if (!this.CLOSE_STD_OUT) {
                                console.log(trimmed);
                            }
                            emptyLines = 0;
                            checkLine(trimmed);
                        } else {
                            emptyLines++;
                            // Too many empty lines means RoboDK might not have started properly
                            if (emptyLines > 10 && !resolved) {
                                resolved = true;
                                reject(new Error('RoboDK Application not properly started'));
                            }
                        }
                    }
                });

                this.NEW_INSTANCE.on('error', (err) => {
                    if (!resolved) {
                        resolved = true;
                        reject(err);
                    }
                });

                // Timeout after 30 seconds
                setTimeout(() => {
                    if (!resolved) {
                        resolved = true;
                        finishStartup();
                    }
                }, 30000);

            } catch (err) {
                reject(err);
            }
        });
    }

    /**
     * Disconnect from RoboDK.
     * If QUIT_ON_CLOSE is true and this instance started RoboDK, it will close RoboDK.
     */
    async Disconnect(): Promise<void> {
        // If we started RoboDK and quit_on_close is set, close RoboDK
        if (this.QUIT_ON_CLOSE && this.NEW_INSTANCE !== null) {
            console.log('Stopping ' + this.APPLICATION_DIR);
            // Only try to send QUIT command if we have a connection
            if (this.COM) {
                try {
                    await this.CloseRoboDK();
                } catch {
                    // Ignore errors when closing
                }
            }
            // Kill the process if it's still running
            if (this.NEW_INSTANCE && !this.NEW_INSTANCE.killed) {
                this.NEW_INSTANCE.kill();
            }
            // Wait for process to exit
            await new Promise<void>((resolve) => {
                if (this.NEW_INSTANCE) {
                    this.NEW_INSTANCE.once('exit', () => resolve());
                    // Timeout in case process doesn't exit
                    setTimeout(() => resolve(), 5000);
                } else {
                    resolve();
                }
            });
            this.NEW_INSTANCE = null;
        }

        if (this.COM) {
            this.COM.destroy();
            this.COM = null;
        }
        this._buffer = Buffer.alloc(0);
    }

    /**
     * Disconnect from the RoboDK API. This flushes any pending program generation.
     */
    async Finish(): Promise<void> {
        await this.Disconnect();
    }

    /**
     * Establish a connection with RoboDK.
     * If RoboDK is not running it will attempt to start RoboDK.
     * Returns 1 if connection succeeds, 0 otherwise.
     */
    async Connect(): Promise<number> {
        let connected = 0;

        for (let attempt = 0; attempt < 2; attempt++) {
            for (let port = this.PORT_START; port <= this.PORT_END; port++) {
                // Close previous socket if exists
                if (this.COM) {
                    this.COM.destroy();
                    this.COM = null;
                }
                this._buffer = Buffer.alloc(0);

                try {
                    // Try to connect
                    await new Promise<void>((resolve, reject) => {
                        this.COM = new net.Socket();
                        this.COM.setTimeout(1000);

                        this.COM.once('connect', () => {
                            this.COM?.setTimeout(this.TIMEOUT);
                            resolve();
                        });
                        this.COM.once('error', reject);
                        this.COM.once('timeout', () => reject(new Error('Connection timeout')));

                        this.COM.connect({ port: port, host: this.IP, family: 4 });
                    });

                    connected = this._is_connected();
                    if (connected > 0) {
                        this.PORT = port;
                        break;
                    }
                } catch {
                    // Connection failed, try next port
                }
            }

            if (connected > 0) {
                break;
            }

            // If first attempt failed and we're on localhost, try to start RoboDK
            if (attempt === 0 && (this.IP === 'localhost' || this.IP === '127.0.0.1')) {
                if (!this.APPLICATION_DIR) {
                    return 0;
                }

                try {
                    await this._startRoboDK();
                } catch {
                    return 0;
                }
            }
        }

        if (connected > 0) {
            try {
                const verified = await this._verify_connection();
                if (!verified) {
                    connected = 0;
                }
            } catch {
                connected = 0;
            }
        }

        return connected;
    }

    /**
     * Create a new API connection to RoboDK using a different communication link.
     * Use this for multi-threaded applications where each thread should have its own Robolink instance.
     */
    async NewLink(): Promise<void> {
        // Close existing connection
        if (this.COM) {
            this.COM.destroy();
            this.COM = null;
        }
        this._buffer = Buffer.alloc(0);

        // Create new socket connection
        try {
            await new Promise<void>((resolve, reject) => {
                this.COM = new net.Socket();
                this.COM.setTimeout(1000);

                if (this.NODELAY) {
                    this.COM.setNoDelay(true);
                }

                this.COM.once('connect', () => {
                    this.COM?.setTimeout(this.TIMEOUT);
                    resolve();
                });
                this.COM.once('error', reject);
                this.COM.once('timeout', () => reject(new Error('Connection timeout')));

                this.COM.connect({ port: this.PORT, host: this.IP, family: 4 });
            });

            const connected = this._is_connected();
            if (connected <= 0) {
                console.log('Failed to reconnect (1)');
                return;
            }

            // Validate the connection
            await this._verify_connection();
        } catch {
            console.log('Failed to reconnect (2)');
        }
    }

    /**
     * Check if a new RoboDK instance was created when connecting.
     * @returns True if a new RoboDK instance was spawned, false otherwise
     */
    isNewInstance(): boolean {
        return this.NEW_INSTANCE !== null;
    }

    /**
     * Returns an item by its name.
     * If there is no exact match it will return the last closest match.
     */
    async Item(name: string, itemtype?: number): Promise<Item> {
        if (itemtype === undefined) {
            this._send_line('G_Item');
            this._send_line(name);
        } else {
            this._send_line('G_Item2');
            this._send_line(name);
            this._send_int(itemtype);
        }
        const item = await this._rec_item();
        await this._check_status();
        return item;
    }

    /**
     * Returns a list of items of all available items in the currently open station.
     */
    async ItemList(filter?: number): Promise<Item[]> {
        const retlist: Item[] = [];
        if (filter === undefined) {
            this._send_line('G_List_Items_ptr');
        } else {
            this._send_line('G_List_Items_Type_ptr');
            this._send_int(filter);
        }
        const count = await this._rec_int();
        for (let i = 0; i < count; i++) {
            const item = await this._rec_item();
            retlist.push(item);
        }
        await this._check_status();
        return retlist;
    }

    /**
     * Show or raise the RoboDK window.
     */
    async ShowRoboDK(): Promise<void> {
        this._send_line('RAISE');
        await this._check_status();
    }

    /**
     * Hide the RoboDK window. RoboDK will keep running as a process.
     */
    async HideRoboDK(): Promise<void> {
        this._send_line('HIDE');
        await this._check_status();
    }

    /**
     * Close RoboDK window and finish RoboDK's execution.
     */
    async CloseRoboDK(): Promise<void> {
        this._send_line('QUIT');
        await this._check_status();
    }

    /**
     * Return RoboDK's version as a string.
     */
    async Version(): Promise<string> {
        this._send_line('Version');
        await this._rec_line(); // app_name
        await this._rec_int();  // bit_arch
        const ver4 = await this._rec_line();
        await this._rec_line(); // date_build
        await this._check_status();
        return ver4;
    }

    /**
     * Set the state of the RoboDK window.
     */
    async setWindowState(windowstate: number = WINDOWSTATE_NORMAL): Promise<void> {
        this._send_line('S_WindowState');
        this._send_int(windowstate);
        await this._check_status();
    }

    /**
     * Load a file and attach it to parent. It can be any file supported by RoboDK.
     */
    async AddFile(filename: string, parent: Item | null = null): Promise<Item> {
        this._send_line('Add');
        this._send_line(filename);
        this._send_item(parent);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices.
     * A vertex normal can be provided optionally.
     * @param triangle_points - Matrix (3xN or 6xN) of triangle vertices. N must be multiple of 3.
     * @param add_to - Item to attach the newly added geometry (optional)
     * @param override_shapes - Set to true to replace existing shapes
     * @returns Added object/shape item (invalid if failed)
     */
    async AddShape(triangle_points: Mat | number[][], add_to: Item | null = null, override_shapes: boolean = false): Promise<Item> {
        let points: Mat;
        if (triangle_points instanceof Mat) {
            points = triangle_points;
        } else {
            // Convert list to transposed matrix (column-major)
            points = new Mat(triangle_points).tr();
        }
        this._send_line('AddShape2');
        this._send_matrix(points.rows);
        this._send_item(add_to);
        this._send_int(override_shapes ? 1 : 0);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Adds a curve provided point coordinates. The provided points must be a list of vertices.
     * A vertex normal can be provided optionally.
     * @param curve_points - Matrix (3xN or 6xN) of curve points
     * @param reference_object - Item to attach the newly added geometry (optional)
     * @param add_to_ref - If true, the curve will be added as part of the object in the RoboDK item tree
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Added object/shape item (invalid if failed)
     */
    async AddCurve(curve_points: Mat | number[][], reference_object: Item | null = null, add_to_ref: boolean = false, projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Item> {
        let points: Mat;
        if (curve_points instanceof Mat) {
            points = curve_points;
        } else {
            // Convert list to transposed matrix (column-major)
            points = new Mat(curve_points).tr();
        }
        this._send_line('AddWire');
        this._send_matrix(points.rows);
        this._send_item(reference_object);
        this._send_int(add_to_ref ? 1 : 0);
        this._send_int(projection_type);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Adds a list of points to an object. The provided points must be a list of vertices.
     * A vertex normal can be provided optionally.
     * @param points - Matrix (3xN or 6xN) of points
     * @param reference_object - Item to attach the newly added geometry (optional)
     * @param add_to_ref - If true, the points will be added as part of the object in the RoboDK item tree
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Added object/shape item (invalid if failed)
     */
    async AddPoints(points: Mat | number[][], reference_object: Item | null = null, add_to_ref: boolean = false, projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Item> {
        let pointsMat: Mat;
        if (points instanceof Mat) {
            pointsMat = points;
        } else {
            // Convert list to transposed matrix (column-major)
            pointsMat = new Mat(points).tr();
        }
        this._send_line('AddPoints');
        this._send_matrix(pointsMat.rows);
        this._send_item(reference_object);
        this._send_int(add_to_ref ? 1 : 0);
        this._send_int(projection_type);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Project a point or a list of points given its coordinates.
     * The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
     * @param points - Matrix (3xN or 6xN) of points to project
     * @param object_project - Object to project the points onto
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Projected points as a matrix
     */
    async ProjectPoints(points: Mat | number[][], object_project: Item, projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Mat> {
        let pointsMat: Mat;
        if (points instanceof Mat) {
            pointsMat = points;
        } else {
            // Convert list to transposed matrix (column-major)
            pointsMat = new Mat(points).tr();
            // Safety check for backwards compatibility
            const [rows, cols] = pointsMat.size();
            if (rows !== 6 && cols === 6) {
                pointsMat = pointsMat.tr();
            }
        }
        this._send_line('ProjectPoints');
        this._send_matrix(pointsMat.rows);
        this._send_item(object_project);
        this._send_int(projection_type);
        const projected_points = await this._rec_matrix();
        await this._check_status();
        return new Mat(projected_points);
    }

    /**
     * Close the current station without suggesting to save.
     */
    async CloseStation(): Promise<void> {
        this._send_line('RemoveStn');
        await this._check_status();
    }

    /**
     * Remove a list of items from the station.
     * @param item_list - Item or list of items to remove
     */
    async Delete(item_list: Item | Item[]): Promise<void> {
        const items = Array.isArray(item_list) ? item_list : [item_list];
        this._send_line('RemoveLst');
        this._send_int(items.length);
        for (const itm of items) {
            this._send_item(itm);
            itm.item = BigInt(0);
        }
        await this._check_status();
    }

    /**
     * Save an item or station to a file. If no item is provided, the current station is saved.
     */
    async Save(filename: string, itemsave: Item | null = null): Promise<void> {
        this._send_line('Save');
        this._send_line(filename);
        this._send_item(itemsave);
        await this._check_status();
    }

    /**
     * Add a new empty station.
     */
    async AddStation(name: string = 'New Station'): Promise<Item> {
        this._send_line('NewStation');
        this._send_line(name);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Add a new target that can be reached with a robot.
     */
    async AddTarget(name: string, itemparent: Item | null = null, itemrobot: Item | null = null): Promise<Item> {
        this._send_line('Add_TARGET');
        this._send_line(name);
        this._send_item(itemparent);
        this._send_item(itemrobot);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Adds a new reference frame. Returns the new Item created.
     */
    async AddFrame(name: string, itemparent: Item | null = null): Promise<Item> {
        this._send_line('Add_FRAME');
        this._send_line(name);
        this._send_item(itemparent);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Add a new program. Optionally specify a robot to attach the program to.
     */
    async AddProgram(name: string, itemrobot: Item | null = null): Promise<Item> {
        this._send_line('Add_PROG');
        this._send_line(name);
        this._send_item(itemrobot);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Create a new robot or mechanism.
     * @param type - Type of the mechanism (MAKE_ROBOT_6DOF, MAKE_ROBOT_GRIPPER, etc.)
     * @param list_obj - List of object items that build the robot (base + links)
     * @param parameters - Robot parameters (DH parameters, etc.)
     * @param joints_build - Current state of the robot joints to build the robot
     * @param joints_home - Joints for the home position
     * @param joints_senses - Joint senses (+1 or -1 for each axis)
     * @param joints_lim_low - Lower joint limits
     * @param joints_lim_high - Upper joint limits
     * @param base - Base frame transformation
     * @param tool - Tool frame transformation
     * @param name - Robot name
     * @param robot - Existing robot to replace (optional)
     * @returns The new robot item
     */
    async BuildMechanism(
        type: number,
        list_obj: Item[],
        parameters: number[],
        joints_build: number[],
        joints_home: number[],
        joints_senses: number[],
        joints_lim_low: number[],
        joints_lim_high: number[],
        base: Mat = Mat.eye(),
        tool: Mat = Mat.eye(),
        name: string = 'New robot',
        robot: Item | null = null
    ): Promise<Item> {
        const ndofs = list_obj.length - 1;

        this._send_line('BuildMechanism');
        this._send_item(robot);
        this._send_line(name);
        this._send_int(type);
        this._send_int(ndofs);

        // Send each object item
        for (let i = 0; i < ndofs + 1; i++) {
            this._send_item(list_obj[i]);
        }

        this._send_pose(base);
        this._send_pose(tool);
        this._send_array(parameters);

        // Pad arrays to 12 elements (for up to 12 DOF)
        const padTo12 = (arr: number[]): number[] => {
            const result = [...arr];
            while (result.length < 12) {
                result.push(0);
            }
            return result;
        };

        const jb = padTo12(joints_build);
        const jh = padTo12(joints_home);
        const js = padTo12(joints_senses);
        const jl = padTo12(joints_lim_low);
        const ju = padTo12(joints_lim_high);

        // Create matrix: 5 rows (one per parameter type), 12 cols (one per joint)
        // Then transpose to get 12 rows x 5 cols
        const jointRows = [jb, jh, js, jl, ju];
        const transposed: number[][] = [];
        for (let j = 0; j < 12; j++) {
            transposed.push([jointRows[0][j], jointRows[1][j], jointRows[2][j], jointRows[3][j], jointRows[4][j]]);
        }
        this._send_matrix(transposed);

        const newRobot = await this._rec_item();
        await this._check_status();
        return newRobot;
    }

    /**
     * Display/render the scene: update the display.
     */
    async Render(always_render: boolean = false): Promise<void> {
        const auto_render = always_render ? 0 : 1;
        this._send_line('Render');
        this._send_int(auto_render);
        await this._check_status();
    }

    /**
     * Update the screen. Updates position of all robots and internal links.
     */
    async Update(): Promise<void> {
        this._send_line('Refresh');
        this._send_int(0);
        await this._check_status();
    }

    /**
     * Checks if an object is inside another object.
     * The encapsulating object must be closed-form, and both objects must be visible with at least 50% color transparency.
     * @param object_inside - Object to check if it is inside
     * @param object_container - Object that potentially contains object_inside
     * @returns 1 if object_inside is inside object_container, else 0
     */
    async IsInside(object_inside: Item, object_container: Item): Promise<number> {
        this._send_line('IsInside');
        this._send_item(object_inside);
        this._send_item(object_container);
        const inside = await this._rec_int();
        await this._check_status();
        return inside;
    }

    /**
     * Set the simulation speed. A simulation speed of 1 means real-time simulation.
     * @param speed - Ratio of speed to real time (1 = real time, 2 = 2x faster, etc.)
     */
    async setSimulationSpeed(speed: number): Promise<void> {
        this._send_line('SimulateSpeed');
        this._send_int(speed * 1000);
        await this._check_status();
    }

    /**
     * Return the simulation speed. A simulation speed of 1 means real-time simulation.
     * @returns Ratio of speed to real time
     */
    async SimulationSpeed(): Promise<number> {
        this._send_line('GetSimulateSpeed');
        const speed = await this._rec_int();
        await this._check_status();
        return speed / 1000.0;
    }

    /**
     * Retrieve the simulation time (in seconds). Time of 0 seconds starts with the first call.
     * @returns Simulation time in seconds
     */
    async SimulationTime(): Promise<number> {
        this._send_line('GetSimTime');
        const time = await this._rec_int();
        await this._check_status();
        return time / 1000.0;
    }

    /**
     * Set the run mode (behavior when running simulation or programs).
     * @param run_mode - RUNMODE_SIMULATE, RUNMODE_QUICKVALIDATE, RUNMODE_MAKE_ROBOTPROG, etc.
     */
    async setRunMode(run_mode: number = RUNMODE_SIMULATE): Promise<void> {
        this._send_line('S_RunMode');
        this._send_int(run_mode);
        await this._check_status();
    }

    /**
     * Get the current run mode (behavior when running simulation or programs).
     * @returns RUNMODE_SIMULATE, RUNMODE_QUICKVALIDATE, RUNMODE_MAKE_ROBOTPROG, etc.
     */
    async RunMode(): Promise<number> {
        this._send_line('G_RunMode');
        const run_mode = await this._rec_int();
        await this._check_status();
        return run_mode;
    }

    /**
     * Get a global parameter from RoboDK.
     * @param param - Parameter name (e.g., 'PATH_OPENSTATION')
     * @returns Parameter value
     */
    async getParam(param: string = 'PATH_OPENSTATION'): Promise<string> {
        this._send_line('G_Param');
        this._send_line(param);
        const value = await this._rec_line();
        await this._check_status();
        return value;
    }

    /**
     * Set a global parameter in RoboDK.
     * @param param - Parameter name
     * @param value - Parameter value
     */
    async setParam(param: string, value: string): Promise<void> {
        this._send_line('S_Param');
        this._send_line(param);
        this._send_line(value);
        await this._check_status();
    }

    /**
     * Get all user parameters from the open RoboDK station.
     * @returns Array of [parameter_name, parameter_value] pairs
     */
    async getParams(): Promise<Array<[string, string | number]>> {
        this._send_line('G_Params');
        const nparam = await this._rec_int();
        const params: Array<[string, string | number]> = [];
        for (let i = 0; i < nparam; i++) {
            const param = await this._rec_line();
            let value: string | number = await this._rec_line();
            // Automatically convert numeric strings to numbers
            const numValue = parseFloat(value);
            if (!isNaN(numValue) && value.replace('.', '').replace('-', '').match(/^\d+$/)) {
                value = numValue;
            }
            params.push([param, value]);
        }
        await this._check_status();
        return params;
    }

    /**
     * Send a command to RoboDK. Commands are like internal plug-in calls.
     * @param cmd - Command name
     * @param value - Command parameter
     * @returns Command result
     */
    async Command(cmd: string, value: string = ''): Promise<string> {
        this._send_line('SCMD');
        this._send_line(cmd);
        this._send_line(value);
        const result = await this._rec_line();
        await this._check_status();
        return result;
    }

    /**
     * Show a message or a comment in the program generated offline (program generation).
     * @param message - Message or comment to display
     * @param message_is_comment - If true, generates a comment instead of a popup message
     */
    async RunMessage(message: string, message_is_comment: boolean = false): Promise<void> {
        console.log('Message: ' + message);
        this._send_line('RunMessage');
        this._send_int(message_is_comment ? 1 : 0);
        this._send_line(message.replace(/\r\n/g, '<<br>>').replace(/\n/g, '<<br>>'));
        await this._check_status();
    }

    /**
     * Enable or disable collision checking.
     * @param check_state - COLLISION_ON (1) or COLLISION_OFF (0)
     * @returns Number of collisions detected
     */
    async setCollisionActive(check_state: number = 1): Promise<number> {
        this._send_line('Collision_SetState');
        this._send_int(check_state);
        const ncollisions = await this._rec_int();
        await this._check_status();
        return ncollisions;
    }

    /**
     * Return the number of pairs of objects that are currently in collision state.
     * @returns Number of collision pairs
     */
    async Collisions(): Promise<number> {
        this._send_line('Collisions');
        const ncollisions = await this._rec_int();
        await this._check_status();
        return ncollisions;
    }

    /**
     * Check if two items are in collision.
     * @param item1 - First item
     * @param item2 - Second item
     * @returns 0 if no collision, >0 if collision
     */
    async Collision(item1: Item, item2: Item): Promise<number> {
        this._send_line('Collided');
        this._send_item(item1);
        this._send_item(item2);
        const ncollisions = await this._rec_int();
        await this._check_status();
        return ncollisions;
    }

    /**
     * Return the list of items that are in collision state.
     * @returns Array of items in collision
     */
    async CollisionItems(): Promise<Item[]> {
        this._send_line('Collision_Items');
        const nitems = await this._rec_int();
        const items: Item[] = [];
        for (let i = 0; i < nitems; i++) {
            items.push(await this._rec_item());
            await this._rec_int(); // link_id (ignored)
            await this._rec_int(); // collision_times (ignored)
        }
        await this._check_status();
        return items;
    }

    /**
     * Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects.
     * Requires collision checking to be activated using setCollisionActive.
     * @param check_state - COLLISION_ON or COLLISION_OFF
     * @param item1 - First item
     * @param item2 - Second item
     * @param id1 - Link id for first item (0 for base, 1+ for joints)
     * @param id2 - Link id for second item (0 for base, 1+ for joints)
     * @returns 1 if succeeded, 0 if failed
     */
    async setCollisionActivePair(check_state: number, item1: Item, item2: Item, id1: number = 0, id2: number = 0): Promise<number> {
        this._send_line('Collision_SetPair');
        this._send_item(item1);
        this._send_item(item2);
        this._send_int(id1);
        this._send_int(id2);
        this._send_int(check_state);
        const success = await this._rec_int();
        await this._check_status();
        return success;
    }

    /**
     * Set collision checking ON or OFF for a list of pairs of objects.
     * @param list_check_state - Collision states for each pair (COLLISION_ON/COLLISION_OFF)
     * @param list_item1 - First items in each pair
     * @param list_item2 - Second items in each pair
     * @param list_id1 - Link ids for first items (optional, defaults to 0)
     * @param list_id2 - Link ids for second items (optional, defaults to 0)
     * @returns 1 if succeeded
     */
    async setCollisionActivePairList(
        list_check_state: number[],
        list_item1: Item[],
        list_item2: Item[],
        list_id1: number[] | null = null,
        list_id2: number[] | null = null
    ): Promise<number> {
        const npairs = Math.min(list_check_state.length, Math.min(list_item1.length, list_item2.length));
        this._send_line('Collision_SetPairList');
        this._send_int(npairs);
        for (let i = 0; i < npairs; i++) {
            this._send_item(list_item1[i]);
            this._send_item(list_item2[i]);
            const id1 = (list_id1 !== null && list_id1.length > i) ? list_id1[i] : 0;
            const id2 = (list_id2 !== null && list_id2.length > i) ? list_id2[i] : 0;
            this._send_int(id1);
            this._send_int(id2);
            this._send_int(list_check_state[i]);
        }
        const success = await this._rec_int();
        await this._check_status();
        return success;
    }

    /**
     * Return the list of pairs of items that are being checked for collisions.
     * @returns Array of [item1, item2, id1, id2] tuples
     */
    async CollisionActivePairList(): Promise<Array<[Item, Item, number, number]>> {
        this._send_line('Collision_GetPairList');
        const nitems = await this._rec_int();
        const item_list: Array<[Item, Item, number, number]> = [];
        for (let i = 0; i < nitems; i++) {
            const item_1 = await this._rec_item();
            const id_1 = await this._rec_int();
            const item_2 = await this._rec_item();
            const id_2 = await this._rec_int();
            item_list.push([item_1, item_2, id_1, id_2]);
        }
        await this._check_status();
        return item_list;
    }

    /**
     * Return the list of pairs of items that are in a collision state.
     * @returns Array of [item1, item2, id1, id2] tuples
     */
    async CollisionPairs(): Promise<Array<[Item, Item, number, number]>> {
        this._send_line('Collision_Pairs');
        const nitems = await this._rec_int();
        const item_list: Array<[Item, Item, number, number]> = [];
        for (let i = 0; i < nitems; i++) {
            const item_1 = await this._rec_item();
            const id_1 = await this._rec_int();
            const item_2 = await this._rec_item();
            const id_2 = await this._rec_int();
            item_list.push([item_1, item_2, id_1, id_2]);
        }
        await this._check_status();
        return item_list;
    }

    /**
     * Set the pose of the world reference frame with respect to the view (camera/screen).
     * @param pose - View pose matrix
     */
    async setViewPose(pose: Mat): Promise<void> {
        this._send_line('S_ViewPose');
        this._send_pose(pose);
        await this._check_status();
    }

    /**
     * Get the pose of the world reference frame with respect to the view (camera/screen).
     * @returns View pose matrix
     */
    async ViewPose(): Promise<Mat> {
        this._send_line('G_ViewPose');
        const pose = await this._rec_pose();
        await this._check_status();
        return pose;
    }

    /**
     * Return the list of currently selected items.
     * @returns Array of selected items
     */
    async Selection(): Promise<Item[]> {
        this._send_line('G_Selection');
        const nitems = await this._rec_int();
        const items: Item[] = [];
        for (let i = 0; i < nitems; i++) {
            items.push(await this._rec_item());
        }
        await this._check_status();
        return items;
    }

    /**
     * Set the selection in the tree.
     * @param items - Array of items to select
     */
    async setSelection(items: Item[] = []): Promise<void> {
        this._send_line('S_Selection');
        this._send_int(items.length);
        for (const item of items) {
            this._send_item(item);
        }
        await this._check_status();
    }

    /**
     * Merge multiple object items as one. A new object is created and returned.
     * Provided objects are deleted.
     * @param list_items - List of items to merge
     * @returns New merged object
     */
    async MergeItems(list_items: Item[]): Promise<Item> {
        this._send_line('MergeItems');
        this._send_int(list_items.length);
        for (const itm of list_items) {
            this._send_item(itm);
        }
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    /**
     * Set RoboDK window flags (permissions).
     * @param flags - Flags to set
     */
    async setFlagsRoboDK(flags: number = 0xFFFF): Promise<void> {
        this._send_line('S_RoboDK_Rights');
        this._send_int(flags);
        await this._check_status();
    }

    /**
     * Set item flags (permissions/display options).
     * @param item - Item to modify
     * @param flags - Flags to set
     */
    async setFlagsItem(item: Item, flags: number = 0xFFFF): Promise<void> {
        this._send_line('S_Item_Rights');
        this._send_item(item);
        this._send_int(flags);
        await this._check_status();
    }

    /**
     * Get item flags (permissions/display options).
     * @param item - Item to query
     * @returns Item flags
     */
    async getFlagsItem(item: Item): Promise<number> {
        this._send_line('G_Item_Rights');
        this._send_item(item);
        const flags = await this._rec_int();
        await this._check_status();
        return flags;
    }

    /**
     * Show a message in RoboDK.
     * @param message - Message to display
     * @param popup - True for popup dialog, false for status bar
     */
    async ShowMessage(message: string, popup: boolean = true): Promise<void> {
        if (popup) {
            this._send_line('ShowMessage');
            this._send_line(message);
            await this._check_status();
        } else {
            this._send_line('ShowMessageStatus');
            this._send_line(message);
            await this._check_status();
        }
    }

    /**
     * Copy an item to the clipboard.
     * @param item - Item to copy
     * @param copy_childs - Include child items
     */
    async Copy(item: Item, copy_childs: boolean = true): Promise<void> {
        this._send_line('Copy2');
        this._send_item(item);
        this._send_int(copy_childs ? 1 : 0);
        await this._check_status();
    }

    /**
     * Paste items from clipboard.
     * @param paste_to - Parent item to paste into
     * @param paste_times - Number of copies to paste
     * @returns Array of pasted items
     */
    async Paste(paste_to: Item | null = null, paste_times: number = 1): Promise<Item[]> {
        if (paste_times > 1) {
            this._send_line('PastN');
            this._send_item(paste_to);
            this._send_int(paste_times);
            const ntimes = await this._rec_int();
            const items: Item[] = [];
            for (let i = 0; i < ntimes; i++) {
                items.push(await this._rec_item());
            }
            await this._check_status();
            return items;
        } else {
            this._send_line('Paste');
            this._send_item(paste_to);
            const newitem = await this._rec_item();
            await this._check_status();
            return [newitem];
        }
    }

    /**
     * Get all open stations.
     * @returns Array of station items
     */
    async getOpenStations(): Promise<Item[]> {
        this._send_line('G_AllStn');
        const nstations = await this._rec_int();
        const stations: Item[] = [];
        for (let i = 0; i < nstations; i++) {
            stations.push(await this._rec_item());
        }
        await this._check_status();
        return stations;
    }

    /**
     * Get the active station.
     * @returns Active station item
     */
    async ActiveStation(): Promise<Item> {
        this._send_line('G_ActiveStn');
        const station = await this._rec_item();
        await this._check_status();
        return station;
    }

    /**
     * Set the active station.
     * @param stn - Station to activate
     */
    async setActiveStation(stn: Item): Promise<void> {
        this._send_line('S_ActiveStn');
        this._send_item(stn);
        await this._check_status();
    }

    /**
     * Get license information.
     * @returns Tuple of [license_info, expiry_date]
     */
    async License(): Promise<[string, string]> {
        this._send_line('G_License2');
        const license = await this._rec_line();
        const date = await this._rec_line();
        await this._check_status();
        return [license, date];
    }

    // ============================================================
    // Batch Operations
    // ============================================================

    /**
     * Set the relative poses of a list of items with respect to their parent.
     * @param items - List of items
     * @param poses - List of poses (must match length of items)
     */
    async setPoses(items: Item[], poses: Mat[]): Promise<void> {
        if (items.length !== poses.length) {
            throw new Error('The number of items must match the number of poses');
        }
        if (items.length === 0) {
            return;
        }
        this._send_line('S_Hlocals');
        this._send_int(items.length);
        for (let i = 0; i < items.length; i++) {
            this._send_item(items[i]);
            this._send_pose(poses[i]);
        }
        await this._check_status();
    }

    /**
     * Set the absolute poses of a list of items with respect to the station reference.
     * @param items - List of items
     * @param poses - List of absolute poses (must match length of items)
     */
    async setPosesAbs(items: Item[], poses: Mat[]): Promise<void> {
        if (items.length !== poses.length) {
            throw new Error('The number of items must match the number of poses');
        }
        if (items.length === 0) {
            return;
        }
        this._send_line('S_Hlocal_AbsS');
        this._send_int(items.length);
        for (let i = 0; i < items.length; i++) {
            this._send_item(items[i]);
            this._send_pose(poses[i]);
        }
        await this._check_status();
    }

    /**
     * Get the current joints of a list of robots.
     * @param robot_item_list - List of robot items
     * @returns List of joint arrays
     */
    async JointsList(robot_item_list: Item[]): Promise<number[][]> {
        this._send_line('G_ThetasList');
        const nrobs = robot_item_list.length;
        this._send_int(nrobs);
        const joints_list: number[][] = [];
        for (let i = 0; i < nrobs; i++) {
            this._send_item(robot_item_list[i]);
            const joints_i = await this._rec_array();
            joints_list.push(joints_i);
        }
        await this._check_status();
        return joints_list;
    }

    /**
     * Set the current joints for a list of robots.
     * @param robot_item_list - List of robot items
     * @param joints_list - List of joint arrays (must match length of robot list)
     */
    async setJointsList(robot_item_list: Item[], joints_list: number[][]): Promise<void> {
        const nrobs = robot_item_list.length;
        if (nrobs !== joints_list.length) {
            throw new Error('The size of the robot list does not match the size of the joints list');
        }
        this._send_line('S_ThetasList');
        this._send_int(nrobs);
        for (let i = 0; i < nrobs; i++) {
            this._send_item(robot_item_list[i]);
            this._send_array(joints_list[i]);
        }
        await this._check_status();
    }

    // ============================================================
    // Calibration Methods
    // ============================================================

    /**
     * Calibrate a TCP given a list of poses/joints and following a specific algorithm/method.
     * @param poses_xyzwpr - List of poses or joints as a matrix (each row is a point)
     * @param input_format - Input format (EULER_* constant or JOINT_FORMAT)
     * @param algorithm - Calibration algorithm (CALIBRATE_TCP_BY_POINT, etc.)
     * @param robot - Robot item (optional)
     * @param tool - Tool item to calibrate (optional)
     * @returns Tuple of [TCP_xyz, error_stats, errors_per_pose]
     */
    async CalibrateTool(
        poses_xyzwpr: number[][],
        input_format: number = EULER_RX_RY_RZ,
        algorithm: number | number[] = CALIBRATE_TCP_BY_POINT,
        robot: Item | null = null,
        tool: Item | null = null
    ): Promise<[number[], number[], number[]]> {
        this._send_line('CalibTCP3');
        this._send_matrix(poses_xyzwpr);
        this._send_int(input_format);
        const algoArray = Array.isArray(algorithm) ? algorithm : [algorithm];
        this._send_array(algoArray);
        this._send_item(robot);
        this._send_item(tool);
        // Extended timeout for calibration
        const oldTimeout = this.TIMEOUT;
        this.COM?.setTimeout(Math.max(3600000, this.TIMEOUT));
        const TCPxyz = await this._rec_array();
        this.COM?.setTimeout(oldTimeout);
        const errorstats = await this._rec_array();
        const errors = await this._rec_matrix();
        await this._check_status();
        // Extract error column if available
        const errorList = errors.length > 0 && errors[0].length > 1
            ? errors.map(row => row[1])
            : [];
        return [TCPxyz, errorstats, errorList];
    }

    /**
     * Calibrate a reference frame given a number of points and following a specific algorithm/method.
     * @param joints_points - Matrix of joints or points data (each row is a measurement)
     * @param method - Calibration method (CALIBRATE_FRAME_3P_P1_ON_X, etc.)
     * @param use_joints - If true, joints_points contains joint values instead of Cartesian points
     * @param robot - Robot item (optional)
     * @returns Reference frame pose, or tuple of [pose, stats] for turntable calibration
     */
    async CalibrateReference(
        joints_points: number[][],
        method: number = CALIBRATE_FRAME_3P_P1_ON_X,
        use_joints: boolean = false,
        robot: Item | null = null
    ): Promise<Mat | [Mat, number[]]> {
        this._send_line('CalibFrame');
        this._send_matrix(joints_points);
        this._send_int(use_joints ? -1 : 0);
        this._send_int(method);
        this._send_item(robot);
        const reference_pose = await this._rec_pose();
        const stats_data = await this._rec_array();
        await this._check_status();
        // Return with stats for turntable calibration
        if (stats_data.length > 3) {
            return [reference_pose, stats_data];
        }
        return reference_pose;
    }

    // ============================================================
    // Program Generation
    // ============================================================

    /**
     * Defines the name of the program when the program is generated (offline programming).
     * Set the program name to "" to disable offline programming.
     * @param programname - Name of the program
     * @param folder - Folder to save (leave empty to use default)
     * @param postprocessor - Post processor name (leave empty to use robot's default)
     * @param robot - Robot to use (optional)
     * @returns Number of errors (0 means success)
     */
    async ProgramStart(
        programname: string,
        folder: string = '',
        postprocessor: string = '',
        robot: Item | null = null
    ): Promise<number> {
        this._send_line('ProgramStart');
        this._send_line(programname);
        this._send_line(folder);
        this._send_line(postprocessor);
        this._send_item(robot);
        const errors = await this._rec_int();
        await this._check_status();
        return errors;
    }

    // ============================================================
    // Line Collision
    // ============================================================

    /**
     * Check collision between a line and any objects in the station.
     * @param p1 - Start point [x, y, z]
     * @param p2 - End point [x, y, z]
     * @param ref - Reference frame (optional, points will be transformed)
     * @returns Tuple of [collision, item, xyz_collision_point]
     */
    async Collision_Line(
        p1: number[],
        p2: number[],
        ref: Mat | null = null
    ): Promise<[boolean, Item, number[]]> {
        let point1 = p1;
        let point2 = p2;
        if (ref !== null) {
            point1 = ref.multiply(p1.slice(0, 3)) as number[];
            point2 = ref.multiply(p2.slice(0, 3)) as number[];
        }
        this._send_line('CollisionLine');
        this._send_xyz(point1);
        this._send_xyz(point2);
        const itempicked = await this._rec_item();
        const xyz = await this._rec_xyz();
        await this._check_status();
        const collision = itempicked.item !== BigInt(0);
        return [collision, itempicked, xyz];
    }

    // ============================================================
    // UI/Interactive Methods (require user interaction)
    // ============================================================

    /**
     * Shows a RoboDK popup to select one Item from the open station.
     * Note: This method blocks until the user makes a selection or cancels.
     * @param message - Message to display in the popup
     * @param itemtype_or_list - Item type filter (int) or list of items to choose from
     * @returns Selected item (invalid item if cancelled)
     */
    async ItemUserPick(
        message: string = 'Pick one item',
        itemtype_or_list: number | Item[] = -1
    ): Promise<Item> {
        if (typeof itemtype_or_list === 'number') {
            // Filter by item type
            this._send_line('PickItem');
            this._send_line(message);
            this._send_int(itemtype_or_list);
        } else {
            // Filter by item list
            this._send_line('PickItemList');
            this._send_line(message);
            this._send_int(itemtype_or_list.length);
            for (const itm of itemtype_or_list) {
                this._send_item(itm);
            }
        }
        // Extended timeout for user input (up to 1 hour)
        const oldTimeout = this.TIMEOUT;
        this.COM?.setTimeout(Math.max(3600000, this.TIMEOUT));
        const item = await this._rec_item();
        this.COM?.setTimeout(oldTimeout);
        await this._check_status();
        return item;
    }

    // ============================================================
    // 2D Camera Methods (Cam2D_*)
    // ============================================================

    /**
     * Add a 2D camera view to the station.
     * @param item_object - Object to attach the camera (optional)
     * @param cam_params - Camera parameters string (e.g., "FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480")
     * @param camera_item - Existing camera item to modify (optional)
     * @returns Camera item handle
     */
    async Cam2D_Add(item_object: Item | null = null, cam_params: string = '', camera_item: Item | null = null): Promise<Item> {
        this._send_line('Cam2D_PtrAdd');
        this._send_item(item_object);
        this._send_item(camera_item);
        this._send_line(cam_params);
        const cam_handle = await this._rec_item();
        await this._check_status();
        return cam_handle;
    }

    /**
     * Take a snapshot from a camera and save/return the image.
     * @param file_save_img - File path to save (PNG, JPEG, TIFF, etc.). Empty string returns bytes.
     * @param cam_handle - Camera handle from Cam2D_Add
     * @param params - Additional options ("Grayscale", "Depth", "Color")
     * @returns Success (1) if file saved, or image bytes if file_save_img is empty
     */
    async Cam2D_Snapshot(file_save_img: string = '', cam_handle: Item | null = null, params: string = ''): Promise<number | Buffer> {
        this._send_line('Cam2D_PtrSnapshot');
        this._send_item(cam_handle);
        this._send_line(file_save_img);
        this._send_line(params);
        // Extended timeout for large images
        const oldTimeout = this.TIMEOUT;
        this.COM?.setTimeout(Math.max(3600000, this.TIMEOUT));
        let result: number | Buffer;
        if (file_save_img === '') {
            // Return image as bytes
            result = await this._rec_bytes();
        } else {
            result = await this._rec_int();
        }
        this.COM?.setTimeout(oldTimeout);
        await this._check_status();
        return result;
    }

    /**
     * Close a 2D camera view or all cameras.
     * @param cam_handle - Camera handle to close (null = close all)
     * @returns True if successful
     */
    async Cam2D_Close(cam_handle: Item | null = null): Promise<boolean> {
        if (cam_handle === null) {
            this._send_line('Cam2D_CloseAll');
        } else {
            this._send_line('Cam2D_PtrClose');
            this._send_item(cam_handle);
        }
        const success = await this._rec_int();
        await this._check_status();
        return success > 0;
    }

    /**
     * Set parameters for a 2D camera.
     * @param params - Camera parameters string
     * @param cam_handle - Camera handle
     * @returns Success status
     */
    async Cam2D_SetParams(params: string, cam_handle: Item | null = null): Promise<number> {
        this._send_line('Cam2D_PtrSetParams');
        this._send_item(cam_handle);
        this._send_line(params);
        const success = await this._rec_int();
        await this._check_status();
        return success;
    }

    // ============================================================
    // Spray Gun Simulation Methods
    // ============================================================

    /**
     * Add a spray gun simulation.
     * @param item_tool - Tool item (auto-detect if null)
     * @param item_object - Object item (auto-detect if null)
     * @param params - Behavior parameters (e.g., "ELLYPSE PROJECT PARTICLE=SPHERE(4,8,1,1,0.5) STEP=8x8")
     * @param points - Volume as list of points (optional)
     * @param geometry - Custom particle geometry (optional)
     * @returns Spray ID handle
     */
    async Spray_Add(
        item_tool: Item | null = null,
        item_object: Item | null = null,
        params: string = '',
        points: number[][] | null = null,
        geometry: number[][] | null = null
    ): Promise<number> {
        this._send_line('Gun_Add');
        this._send_item(item_tool);
        this._send_item(item_object);
        this._send_line(params);
        this._send_matrix(points || []);
        this._send_matrix(geometry || []);
        const id_spray = await this._rec_int();
        await this._check_status();
        return id_spray;
    }

    /**
     * Set the spray gun state (ON or OFF).
     * @param state - SPRAY_ON or SPRAY_OFF
     * @param id_spray - Spray handle (-1 = apply to all)
     * @returns Success status
     */
    async Spray_SetState(state: number = SPRAY_ON, id_spray: number = -1): Promise<number> {
        this._send_line('Gun_SetState');
        this._send_int(id_spray);
        this._send_int(state);
        const success = await this._rec_int();
        await this._check_status();
        return success;
    }

    /**
     * Get spray gun statistics.
     * @param id_spray - Spray handle (-1 = all sprays)
     * @returns Tuple of [info_string, data_matrix]
     */
    async Spray_GetStats(id_spray: number = -1): Promise<[string, number[][]]> {
        this._send_line('Gun_Stats');
        this._send_int(id_spray);
        const info = (await this._rec_line()).replace(/<br>/g, '\t');
        const data = await this._rec_matrix();
        await this._check_status();
        return [info, data];
    }

    /**
     * Clear spray gun particles.
     * @param id_spray - Spray handle (-1 = apply to all)
     * @returns Success status
     */
    async Spray_Clear(id_spray: number = -1): Promise<number> {
        this._send_line('Gun_Clear');
        this._send_int(id_spray);
        const success = await this._rec_int();
        await this._check_status();
        return success;
    }

    // ============================================================
    // Interactive Mode Methods
    // ============================================================

    /**
     * Set the interactive mode to define the behavior when navigating and selecting items.
     * @param mode_type - Interactive mode (SELECT_MOVE, etc.)
     * @param default_ref_flags - Default motion reference flags
     * @param custom_objects - List of items for custom behavior
     * @param custom_ref_flags - Matching list of flags for custom items
     */
    async setInteractiveMode(
        mode_type: number = SELECT_MOVE,
        default_ref_flags: number = DISPLAY_REF_DEFAULT,
        custom_objects: Item[] | null = null,
        custom_ref_flags: number[] | null = null
    ): Promise<void> {
        this._send_line('S_InteractiveMode');
        this._send_int(mode_type);
        this._send_int(default_ref_flags);
        if (custom_objects === null || custom_ref_flags === null) {
            this._send_int(-1);
        } else {
            const nitems = Math.min(custom_objects.length, custom_ref_flags.length);
            this._send_int(nitems);
            for (let i = 0; i < nitems; i++) {
                this._send_item(custom_objects[i]);
                this._send_int(custom_ref_flags[i]);
            }
        }
        await this._check_status();
    }

    /**
     * Get the 3D position of the cursor (mouse) in the RoboDK window.
     * @param x_coord - X pixel coordinate (-1 = current cursor)
     * @param y_coord - Y pixel coordinate (-1 = current cursor)
     * @returns Tuple of [xyz_position, item_under_cursor]
     */
    async CursorXYZ(x_coord: number = -1, y_coord: number = -1): Promise<[number[], Item]> {
        this._send_line('Proj2d3d');
        this._send_int(x_coord);
        this._send_int(y_coord);
        await this._rec_int(); // selection flag (ignored)
        const item = await this._rec_item();
        const xyz = await this._rec_xyz();
        await this._check_status();
        return [xyz, item];
    }

    // ============================================================
    // Plugin Methods
    // ============================================================

    /**
     * Load or unload a RoboDK plugin.
     * @param plugin_name - Plugin DLL/SO/dylib path or name
     * @param load - 1=load (default), 0=unload, >=2=reload
     * @returns True if successful
     */
    async PluginLoad(plugin_name: string = '', load: number = 1): Promise<boolean> {
        let result = '';
        if (load) {
            if (load >= 2) {
                // Reload: unload then load
                result = await this.Command('PluginUnload', plugin_name);
                result = await this.Command('PluginLoad', plugin_name);
            } else {
                result = await this.Command('PluginLoad', plugin_name);
            }
        } else {
            result = await this.Command('PluginUnload', plugin_name);
        }
        return result === 'OK';
    }

    /**
     * Send a command to a RoboDK plugin.
     * @param plugin_name - Plugin name matching PluginName() in plugin
     * @param plugin_command - Command handled by plugin
     * @param value - Optional value handled by plugin
     * @returns Plugin response string
     */
    async PluginCommand(plugin_name: string, plugin_command: string = '', value: string = ''): Promise<string> {
        this._send_line('PluginCommand');
        this._send_line(plugin_name);
        this._send_line(plugin_command);
        this._send_line(String(value));
        // Extended timeout for long-running plugin operations
        const oldTimeout = this.TIMEOUT;
        this.COM?.setTimeout(Math.max(604800000, this.TIMEOUT)); // 7 days max
        const result = await this._rec_line();
        this.COM?.setTimeout(oldTimeout);
        await this._check_status();
        return result;
    }

    // ============================================================
    // Machining Methods
    // ============================================================

    /**
     * Deprecated. Use AddMachiningProject instead.
     * @param name - Program name
     * @param itemrobot - Robot to use
     */
    async AddMillingProject(name: string = 'Milling settings', itemrobot: Item | null = null): Promise<Item> {
        return this.AddMachiningProject(name, itemrobot);
    }

    /**
     * Add a new machining project. A machining project is used to configure and generate robot programs for machining.
     * @param name - Project name
     * @param itemrobot - Robot to use
     * @returns Machining project item
     */
    async AddMachiningProject(name: string = 'Milling settings', itemrobot: Item | null = null): Promise<Item> {
        this._send_line('Add_MACHINING');
        this._send_line(name);
        this._send_item(itemrobot);
        const newitem = await this._rec_item();
        await this._check_status();
        return newitem;
    }

    // ============================================================
    // Event Methods
    // ============================================================

    /**
     * Start this connection as an event communication channel.
     * Use EventsLoop or WaitForEvent to process events.
     * Important: A dedicated Robolink instance should be used for events.
     * @param filter_events - Optional list of event types to listen for. If not provided, all events are reported.
     * @returns true if successfully started listening for events
     */
    async EventsListen(filter_events?: number[]): Promise<boolean> {
        // Close existing connection and create a fresh one for events
        if (this.COM) {
            this.COM.destroy();
            this.COM = null;
        }

        const net = require('net') as typeof import('net');
        return new Promise((resolve) => {
            const socket = new net.Socket();
            socket.setNoDelay(true);

            socket.on('error', (err) => {
                console.error('Event socket error:', err);
                resolve(false);
            });

            socket.connect(this.PORT, this.IP, async () => {
                this.COM = socket;

                // Verify connection
                const connected = await this._is_connected();
                if (connected <= 0) {
                    console.error('Failed to connect for events');
                    resolve(false);
                    return;
                }

                try {
                    await this._verify_connection();

                    if (filter_events === undefined || filter_events.length === 0) {
                        this._send_line('RDK_EVT');
                    } else {
                        this._send_line('RDK_EVT_FILTER');
                        this._send_int(filter_events.length);
                        for (const evt of filter_events) {
                            this._send_int(evt);
                        }
                    }

                    this._send_int(0);
                    const response = await this._rec_line();
                    const ver_evt = await this._rec_int();
                    const status = await this._rec_int();

                    if (response !== 'RDK_EVT' || status !== 0) {
                        console.error('Event handshake failed:', response, status);
                        resolve(false);
                        return;
                    }

                    // Set long timeout for event waiting (1 hour)
                    socket.setTimeout(3600000);
                    console.log('Events loop started');
                    resolve(true);
                } catch (err) {
                    console.error('Failed to start events:', err);
                    resolve(false);
                }
            });
        });
    }

    /**
     * Wait for a new event from RoboDK.
     * This method blocks until an event is received.
     * @returns Object containing event type and item, or null if connection closed
     */
    async WaitForEvent(): Promise<{ event: number; item: Item } | null> {
        if (!this.COM) {
            return null;
        }

        try {
            const evt = await this._rec_int();
            const item = await this._rec_item();
            return { event: evt, item: item };
        } catch (err) {
            // Connection closed or timeout
            return null;
        }
    }

    /**
     * Receive additional event data based on event type.
     * Call this after WaitForEvent for events that have additional data.
     * @param event_type - The event type returned by WaitForEvent
     * @returns Additional event data, or null if no additional data
     */
    async ReceiveEventData(event_type: number): Promise<any> {
        if (!this.COM) return null;

        try {
            // Import event constants for comparison
            const EVENT_SELECTION_3D_CHANGED = 7;
            const EVENT_KEY = 10;
            const EVENT_ITEM_MOVED_POSE = 11;
            const EVENT_CALIB_MEASUREMENT = 14;
            const EVENT_ITEM_RENAMED = 17;
            const EVENT_ITEM_VISIBILITY = 18;
            const EVENT_PROGSLIDER_SET = 21;

            if (event_type === EVENT_SELECTION_3D_CHANGED) {
                // data: pose (16), xyz (3), ijk (3), feature_type (1), feature_id (1)
                const data = await this._rec_array();
                return {
                    pose_abs: new Mat([
                        [data[0], data[4], data[8], data[12]],
                        [data[1], data[5], data[9], data[13]],
                        [data[2], data[6], data[10], data[14]],
                        [data[3], data[7], data[11], data[15]]
                    ]),
                    xyz: [data[16], data[17], data[18]],
                    ijk: [data[19], data[20], data[21]],
                    feature_type: Math.floor(data[22]),
                    feature_id: Math.floor(data[23])
                };
            } else if (event_type === EVENT_KEY) {
                const key_press = await this._rec_int();
                const key_id = await this._rec_int();
                const modifiers = await this._rec_int();
                return { key_press, key_id, modifiers };
            } else if (event_type === EVENT_ITEM_MOVED_POSE) {
                const nvalues = await this._rec_int();
                const pose_rel = await this._rec_pose();
                return { nvalues, pose_rel };
            } else if (event_type === EVENT_CALIB_MEASUREMENT) {
                const data = await this._rec_array();
                return {
                    status: data[0],
                    measure_id: data[1]
                };
            } else if (event_type === EVENT_ITEM_RENAMED) {
                const name = await this._rec_line();
                return { name };
            } else if (event_type === EVENT_ITEM_VISIBILITY) {
                const data = await this._rec_array();
                return {
                    visible_object: data[0],
                    visible_frame: data[1]
                };
            } else if (event_type === EVENT_PROGSLIDER_SET) {
                const slider_index = await this._rec_int();
                return { slider_index };
            }

            // No additional data for other events
            return null;
        } catch (err) {
            return null;
        }
    }
}

// ============================================================
// Item Class - Represents an item in the RoboDK tree
// ============================================================

export class Item {
    // it is recommended to keep the link as a reference and not a duplicate
    link: Robolink;
    type: number;
    item: bigint;

    constructor(link: Robolink, item_ptr: bigint = BigInt(0), itemtype: number = -1) {
        this.link = link;
        this.type = itemtype;
        this.item = item_ptr;
    }

    /**
     * Returns true if this item is the same as another item.
     * @param item2 - Item to compare with
     */
    equals(item2: Item): boolean {
        return this.item === item2.item;
    }

    /**
     * Returns the Robolink instance associated with this item.
     */
    RDK(): Robolink {
        return this.link;
    }

    // """Generic item calls"""

    /**
     * Return the type of the item (robot, object, tool, frame, ...).
     */
    async Type(): Promise<number> {
        this.link._send_line('G_Item_Type');
        this.link._send_item(this);
        const itemtype = await this.link._rec_int();
        await this.link._check_status();
        return itemtype;
    }

    /**
     * Copy the item to the clipboard.
     * @param copy_children - Copy children items too
     */
    async Copy(copy_children: boolean = true): Promise<void> {
        await this.link.Copy(this, copy_children);
    }

    /**
     * Paste clipboard contents to this item.
     */
    async Paste(): Promise<Item[]> {
        return this.link.Paste(this);
    }

    /**
     * Add a file to an item (e.g., add NC program to robot).
     * @param filename - Path to file
     */
    async AddFile(filename: string): Promise<Item> {
        this.link._send_line('Add_FILE');
        this.link._send_line(filename);
        this.link._send_item(this);
        const newitem = await this.link._rec_item();
        await this.link._check_status();
        return newitem;
    }

    /**
     * Save an item to a file.
     * @param filename - Path to save
     */
    async Save(filename: string): Promise<void> {
        this.link._send_line('Save');
        this.link._send_item(this);
        this.link._send_line(filename);
        await this.link._check_status();
    }

    /**
     * Check if this item is in collision with another item.
     * @param item_check - Item to check collision with
     */
    async Collision(item_check: Item): Promise<boolean> {
        return await this.link.Collision(this, item_check) > 0;
    }

    /**
     * Check if a point is inside an object.
     * @param objectItem - Object to check
     */
    async IsInside(objectItem: Item): Promise<boolean> {
        this.link._send_line('IsInside');
        this.link._send_item(this);
        this.link._send_item(objectItem);
        const inside = await this.link._rec_int();
        await this.link._check_status();
        return inside > 0;
    }

    /**
     * Makes a copy of the geometry from another item adding it at a given position (pose), relative to this item.
     * @param fromitem - Item to copy geometry from
     * @param pose - Pose offset for the copied geometry
     */
    async AddGeometry(fromitem: Item, pose: Mat): Promise<void> {
        this.link._send_line('CopyFaces');
        this.link._send_item(fromitem);
        this.link._send_item(this);
        this.link._send_pose(pose);
        await this.link._check_status();
    }

    /**
     * Remove this item and all its children from the station.
     */
    async Delete(): Promise<void> {
        if (this.item === BigInt(0)) {
            throw new Error('Item is not valid or was already deleted');
        }
        this.link._send_line('Remove');
        this.link._send_item(this);
        this.item = BigInt(0);
        await this.link._check_status();
    }

    /**
     * Checks if the item is valid.
     */
    Valid(): boolean {
        return this.item !== BigInt(0);
    }

    /**
     * Attaches the item to a new parent (changes absolute position).
     * @param parent - Parent item to attach to
     */
    async setParent(parent: Item): Promise<Item> {
        this.link._send_line('S_Parent');
        this.link._send_item(this);
        this.link._send_item(parent);
        await this.link._check_status();
        return this;
    }

    /**
     * Attaches the item to a new parent (maintains absolute position).
     * @param parent - Parent item to attach to
     */
    async setParentStatic(parent: Item): Promise<Item> {
        this.link._send_line('S_Parent_Static');
        this.link._send_item(this);
        this.link._send_item(parent);
        await this.link._check_status();
        return this;
    }

    /**
     * Attach the closest object to the tool.
     * Returns the item that was attached. Use item.Valid() to check if an object was attached to the tool.
     * @param keyword - Keyword needed for an object to be grabbable (leave empty to consider all objects)
     * @param tolerance_mm - Distance tolerance to use (at most) to consider grabbing objects. -1 means default.
     * @param list_objects - List of candidate objects to consider to grab
     * @returns Item that was attached (invalid if none)
     */
    async AttachClosest(keyword: string = '', tolerance_mm: number = -1, list_objects: Item[] = []): Promise<Item> {
        this.link._send_line('Attach_Closest2');
        this.link._send_item(this);
        this.link._send_line(keyword);
        this.link._send_array([tolerance_mm]);
        this.link._send_int(list_objects.length);
        for (const obji of list_objects) {
            this.link._send_item(obji);
        }
        const item_attached = await this.link._rec_item();
        await this.link._check_status();
        return item_attached;
    }

    /**
     * Detach the closest object attached to the tool.
     * @param parent - New parent item to attach to (optional). If not provided, the items held by the tool will be placed at the station root.
     * @returns Item that was detached (invalid if none)
     */
    async DetachClosest(parent: Item | null = null): Promise<Item> {
        this.link._send_line('Detach_Closest');
        this.link._send_item(this);
        this.link._send_item(parent);
        const item_detached = await this.link._rec_item();
        await this.link._check_status();
        return item_detached;
    }

    /**
     * Detaches any object attached to a tool.
     * @param parent - New parent item to attach to (optional). If not provided, the items held by the tool will be placed at the station root.
     */
    async DetachAll(parent: Item | null = null): Promise<void> {
        this.link._send_line('Detach_All');
        this.link._send_item(this);
        this.link._send_item(parent);
        await this.link._check_status();
    }

    /**
     * Return the parent item of this item.
     */
    async Parent(): Promise<Item> {
        this.link._send_line('G_Parent');
        this.link._send_item(this);
        const parent = await this.link._rec_item();
        await this.link._check_status();
        return parent;
    }

    /**
     * Return a list of the child items attached to this item.
     */
    async Childs(): Promise<Item[]> {
        this.link._send_line('G_Childs');
        this.link._send_item(this);
        const nitems = await this.link._rec_int();
        const itemlist: Item[] = [];
        for (let i = 0; i < nitems; i++) {
            itemlist.push(await this.link._rec_item());
        }
        await this.link._check_status();
        return itemlist;
    }

    /**
     * Returns true if the item is visible, false otherwise.
     */
    async Visible(): Promise<boolean> {
        this.link._send_line('G_Visible');
        this.link._send_item(this);
        const visible = await this.link._rec_int();
        await this.link._check_status();
        return visible !== 0;
    }

    /**
     * Sets the item visibility.
     */
    async setVisible(visible: boolean, visible_frame: number = -1): Promise<Item> {
        this.link._send_line('S_Visible');
        this.link._send_item(this);
        this.link._send_int(visible ? 1 : 0);
        this.link._send_int(visible_frame);
        await this.link._check_status();
        return this;
    }

    /**
     * Returns the item name displayed in the RoboDK station tree.
     */
    async Name(): Promise<string> {
        this.link._send_line('G_Name');
        this.link._send_item(this);
        const name = await this.link._rec_line();
        await this.link._check_status();
        return name;
    }

    /**
     * Set the name of the item displayed in the station tree.
     */
    async setName(name: string): Promise<Item> {
        this.link._send_line('S_Name');
        this.link._send_item(this);
        this.link._send_line(name);
        await this.link._check_status();
        return this;
    }

    /**
     * Set a specific variable value for an item.
     * @param varname - Variable name
     * @param value - Variable value
     */
    async setValue(varname: string, value: string): Promise<void> {
        this.link._send_line('S_Gen_Val');
        this.link._send_item(this);
        this.link._send_line(varname);
        this.link._send_line(value);
        await this.link._check_status();
    }

    /**
     * Set the pose of the item with respect to its parent.
     */
    async setPose(pose: Mat): Promise<Item> {
        this.link._send_line('S_Hlocal');
        this.link._send_item(this);
        this.link._send_pose(pose);
        await this.link._check_status();
        return this;
    }

    /**
     * Returns the pose of the item with respect to its parent.
     */
    async Pose(): Promise<Mat> {
        this.link._send_line('G_Hlocal');
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Set the geometry pose (pose of geometry with respect to item reference).
     * @param pose - Geometry pose matrix
     * @param apply - Apply the pose to vertices
     */
    async setGeometryPose(pose: Mat, apply: boolean = false): Promise<void> {
        this.link._send_line('S_Hgeo2');
        this.link._send_item(this);
        this.link._send_pose(pose);
        this.link._send_int(apply ? 1 : 0);
        await this.link._check_status();
    }

    /**
     * Returns the geometry pose (pose of geometry with respect to item reference).
     */
    async GeometryPose(): Promise<Mat> {
        this.link._send_line('G_Hgeom');
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Set the absolute pose of the item (world coordinates).
     * @param pose - Absolute pose matrix
     */
    async setPoseAbs(pose: Mat): Promise<Item> {
        this.link._send_line('S_Hlocal_Abs');
        this.link._send_item(this);
        this.link._send_pose(pose);
        await this.link._check_status();
        return this;
    }

    /**
     * Returns the absolute pose of the item (world coordinates).
     */
    async PoseAbs(): Promise<Mat> {
        this.link._send_line('G_Hlocal_Abs');
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Changes the color of an item.
     * @param tocolor - New color [R, G, B, A]
     * @param fromcolor - Color to replace (null for all)
     * @param tolerance - Tolerance (0 for exact match)
     */
    async Recolor(tocolor: number[], fromcolor: number[] | null = null, tolerance: number = 0.1): Promise<void> {
        this.link._send_line('Recolor');
        this.link._send_item(this);
        const colorArray = fromcolor ? [...tocolor, ...fromcolor, tolerance] : [...tocolor, 0, 0, 0, 0, tolerance];
        this.link._send_array(colorArray);
        await this.link._check_status();
    }

    /**
     * Set the color of an item.
     * @param tocolor - Color as [R, G, B, A] with values 0-1
     */
    async setColor(tocolor: number[]): Promise<void> {
        this.link._send_line('S_Color');
        this.link._send_item(this);
        this.link._send_array(tocolor);
        await this.link._check_status();
    }

    /**
     * Set the color of an object shape. It can also be used for tools.
     * @param tocolor - Color as [R, G, B, A] with values 0-1
     * @param shape_id - ID of the shape: the ID is the order in which the shape was added using AddShape()
     */
    async setColorShape(tocolor: number[], shape_id: number): Promise<void> {
        this.link._send_line('S_ShapeColor');
        this.link._send_item(this);
        this.link._send_int(shape_id);
        this.link._send_array(tocolor);
        await this.link._check_status();
    }

    /**
     * Set the color of a curve object. It can also be used for tools.
     * @param tocolor - Color as [R, G, B, A] with values 0-1
     * @param curve_id - ID of the curve: the ID is the order in which the curve was added using AddCurve(). Use -1 for all curves.
     */
    async setColorCurve(tocolor: number[], curve_id: number = -1): Promise<void> {
        this.link._send_line('S_CurveColor');
        this.link._send_item(this);
        this.link._send_int(curve_id);
        this.link._send_array(tocolor);
        await this.link._check_status();
    }

    /**
     * Returns the color of an item (RGBA values 0-1).
     */
    async Color(): Promise<number[]> {
        this.link._send_line('G_Color');
        this.link._send_item(this);
        const color = await this.link._rec_array();
        await this.link._check_status();
        return color;
    }

    /**
     * Apply a scale to an object.
     * @param scale - Scale factor (float for uniform, [x,y,z] for per-axis)
     */
    async Scale(scale: number | number[]): Promise<void> {
        const scaleArray = Array.isArray(scale) ? scale : [scale, scale, scale];
        this.link._send_line('Scale');
        this.link._send_item(this);
        this.link._send_array(scaleArray);
        await this.link._check_status();
    }

    /**
     * Adds a shape to this object. The shape is defined by triangle vertices.
     * @param triangle_points - Matrix (3xN or 6xN) of triangle vertices, or list of [x,y,z] or [x,y,z,i,j,k]
     * @returns Added shape item
     */
    async AddShape(triangle_points: Mat | number[][]): Promise<Item> {
        return this.link.AddShape(triangle_points, this);
    }

    /**
     * Adds a curve to this object. The curve is defined by a list of points.
     * @param curve_points - Matrix (3xN or 6xN) of curve points
     * @param add_to_ref - If true, the curve will be added as part of the object
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Added curve item
     */
    async AddCurve(curve_points: Mat | number[][], add_to_ref: boolean = false, projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Item> {
        return this.link.AddCurve(curve_points, this, add_to_ref, projection_type);
    }

    /**
     * Adds points to this object.
     * @param points - Matrix (3xN or 6xN) of points
     * @param add_to_ref - If true, the points will be added as part of the object
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Added points item
     */
    async AddPoints(points: Mat | number[][], add_to_ref: boolean = false, projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Item> {
        return this.link.AddPoints(points, this, add_to_ref, projection_type);
    }

    /**
     * Project points onto this object surface.
     * @param points - Matrix (3xN or 6xN) of points to project
     * @param projection_type - Type of projection (PROJECTION_* constants)
     * @returns Projected points as a matrix
     */
    async ProjectPoints(points: Mat | number[][], projection_type: number = PROJECTION_ALONG_NORMAL_RECALC): Promise<Mat> {
        return this.link.ProjectPoints(points, this, projection_type);
    }

    /**
     * Retrieve the currently selected feature for this object.
     * @returns Tuple of [is_selected, feature_type, feature_id]
     */
    async SelectedFeature(): Promise<[number, number, number]> {
        this.link._send_line('G_ObjSelection');
        this.link._send_item(this);
        const is_selected = await this.link._rec_int();
        const feature_type = await this.link._rec_int();
        const feature_id = await this.link._rec_int();
        await this.link._check_status();
        return [is_selected, feature_type, feature_id];
    }

    /**
     * Retrieves the point under the mouse cursor, a curve or the 3D points of an object.
     * The points are provided in [XYZijk] format in relative coordinates.
     * @param feature_type - FEATURE_SURFACE, FEATURE_CURVE, FEATURE_POINT, etc.
     * @param feature_id - ID of the feature (used with FEATURE_CURVE)
     * @returns Tuple of [points_list, feature_name]
     */
    async GetPoints(feature_type: number = FEATURE_SURFACE, feature_id: number = 0): Promise<[number[][], string]> {
        if (feature_type >= FEATURE_HOVER_OBJECT_MESH) {
            throw new Error('Invalid feature type. Use FEATURE_SURFACE, FEATURE_MESH or equivalent.');
        }
        this.link._send_line('G_ObjPoint');
        this.link._send_item(this);
        this.link._send_int(feature_type);
        this.link._send_int(feature_id);
        const points = await this.link._rec_matrix();
        const feature_name = await this.link._rec_line();
        await this.link._check_status();
        return [points, feature_name];
    }

    /**
     * Retrieve all curves from this object.
     * The points are provided in [XYZijk] format in relative coordinates.
     * @returns List of tuples [points_matrix, curve_name] for each curve
     */
    async GetCurves(): Promise<Array<[number[][], string]>> {
        this.link._send_line('G_ObjCurves');
        this.link._send_item(this);
        this.link._send_int(FEATURE_CURVE);
        const ncrv = await this.link._rec_int();
        const allcurves: Array<[number[][], string]> = [];
        for (let i = 0; i < ncrv; i++) {
            const points = await this.link._rec_matrix();
            const curve_name = await this.link._rec_line();
            allcurves.push([points, curve_name]);
        }
        await this.link._check_status();
        return allcurves;
    }

    /**
     * Set a target as a Cartesian target.
     */
    async setAsCartesianTarget(): Promise<Item> {
        this.link._send_line('S_Target_As_RT');
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Set a target as a joint target.
     */
    async setAsJointTarget(): Promise<Item> {
        this.link._send_line('S_Target_As_JT');
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Returns true if a target is a joint target, false if Cartesian.
     */
    async isJointTarget(): Promise<boolean> {
        this.link._send_line('Target_Is_JT');
        this.link._send_item(this);
        const isJoint = await this.link._rec_int();
        await this.link._check_status();
        return isJoint > 0;
    }

    /**
     * Returns the current joint position of a robot or target.
     */
    async Joints(): Promise<number[]> {
        this.link._send_line('G_Thetas');
        this.link._send_item(this);
        const joints = await this.link._rec_array();
        await this.link._check_status();
        return joints;
    }

    /**
     * Return the home joints of a robot.
     */
    async JointsHome(): Promise<number[]> {
        this.link._send_line('G_Home');
        this.link._send_item(this);
        const joints = await this.link._rec_array();
        await this.link._check_status();
        return joints;
    }

    /**
     * Set the home position of the robot in the joint space.
     * @param joints - Robot joints
     */
    async setJointsHome(joints: number[]): Promise<Item> {
        this.link._send_line('S_Home');
        this.link._send_array(joints);
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Returns an item pointer to a robot link. This is useful to show/hide certain robot links or alter their geometry.
     * @param link_id - Link index (0 for the robot base, 1 for the first link, ...)
     * @returns Item representing the robot link
     */
    async ObjectLink(link_id: number = 0): Promise<Item> {
        this.link._send_line('G_LinkObjId');
        this.link._send_item(this);
        this.link._send_int(link_id);
        const item = await this.link._rec_item();
        await this.link._check_status();
        return item;
    }

    /**
     * Returns an item pointer to a robot, object, tool or program linked to this item.
     * @param type_linked - Type of the linked item (ITEM_TYPE_*)
     */
    async getLink(type_linked: number = ITEM_TYPE_ROBOT): Promise<Item> {
        this.link._send_line('G_LinkType');
        this.link._send_item(this);
        this.link._send_int(type_linked);
        const item = await this.link._rec_item();
        await this.link._check_status();
        return item;
    }

    /**
     * Sets a link between this item and the specified item.
     * @param item - Item to link
     */
    async setLink(item: Item | null): Promise<Item> {
        const linkItem = item || new Item(this.link);
        this.link._send_line('S_Link_ptr');
        this.link._send_item(linkItem);
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Set the current joints of a robot or target.
     */
    async setJoints(joints: number[]): Promise<Item> {
        this.link._send_line('S_Thetas');
        this.link._send_array(joints);
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Retrieve the joint limits of a robot.
     * Returns [lower_limits, upper_limits, joint_type].
     */
    async JointLimits(): Promise<[number[], number[], number]> {
        this.link._send_line('G_RobLimits');
        this.link._send_item(this);
        const lower = await this.link._rec_array();
        const upper = await this.link._rec_array();
        const joint_type = await this.link._rec_int() / 1000.0;
        await this.link._check_status();
        return [lower, upper, joint_type];
    }

    /**
     * Update the robot joint limits.
     * @param lower_limit - Lower joint limits
     * @param upper_limit - Upper joint limits
     */
    async setJointLimits(lower_limit: number[], upper_limit: number[]): Promise<void> {
        this.link._send_line('S_RobLimits');
        this.link._send_item(this);
        this.link._send_array(lower_limit);
        this.link._send_array(upper_limit);
        await this.link._check_status();
    }

    /**
     * Assigns a specific robot to a program, target or robot machining project.
     * @param robot - Robot to link
     */
    async setRobot(robot: Item | null = null): Promise<Item> {
        return this.setLink(robot);
    }

    /**
     * Sets the reference frame of a robot (user frame).
     * @param frame - Reference frame as an Item or pose Mat
     */
    async setPoseFrame(frame: Item | Mat): Promise<void> {
        if (frame instanceof Item) {
            this.link._send_line('S_Link_ptr');
            this.link._send_item(frame);
        } else {
            this.link._send_line('S_Frame');
            this.link._send_pose(frame);
        }
        this.link._send_item(this);
        await this.link._check_status();
    }

    /**
     * Set the robot tool pose (TCP) with respect to the robot flange.
     * @param tool - Tool pose as an Item or pose Mat
     */
    async setPoseTool(tool: Item | Mat): Promise<void> {
        if (tool instanceof Item) {
            this.link._send_line('S_Tool_ptr');
            this.link._send_item(tool);
        } else {
            this.link._send_line('S_Tool');
            this.link._send_pose(tool);
        }
        this.link._send_item(this);
        await this.link._check_status();
    }

    /**
     * Returns the pose of the robot tool (TCP) with respect to the robot flange.
     */
    async PoseTool(): Promise<Mat> {
        this.link._send_line('G_Tool');
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Returns the pose of the robot reference frame with respect to the robot base.
     */
    async PoseFrame(): Promise<Mat> {
        this.link._send_line('G_Frame');
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Add a tool to a robot given the tool pose and tool name.
     * @param tool_pose - Tool pose (TCP) with respect to the robot flange
     * @param tool_name - Name of the tool
     */
    async AddTool(tool_pose: Mat, tool_name: string = 'New TCP'): Promise<Item> {
        this.link._send_line('AddToolEmpty');
        this.link._send_item(this);
        this.link._send_pose(tool_pose);
        this.link._send_line(tool_name);
        const newtool = await this.link._rec_item();
        await this.link._check_status();
        return newtool;
    }

    /**
     * Calculate the forward kinematics of the robot for the provided joints.
     * Returns the pose of the robot flange with respect to the robot base reference.
     * @param joints - Robot joints
     * @param tool - Optionally provide the tool used to calculate the forward kinematics
     * @param reference - Optionally provide the reference frame
     */
    async SolveFK(joints: number[], tool: Mat | null = null, reference: Mat | null = null): Promise<Mat> {
        // Note: The RoboDK protocol for G_FK does not include tool/reference parameters
        // Those would need to be applied via matrix math if needed
        this.link._send_line('G_FK');
        this.link._send_array(joints);
        this.link._send_item(this);
        const pose = await this.link._rec_pose();
        await this.link._check_status();
        return pose;
    }

    /**
     * Calculates the inverse kinematics for a given specified pose.
     * Returns the joints solution. If there is no solution it returns an empty array.
     * @param pose - Pose of the robot flange with respect to the robot base frame
     * @param joints_approx - Preferred joint solution (leave null to return closest match)
     * @param tool - Tool pose with respect to the robot flange (TCP)
     * @param reference - Reference pose (reference frame with respect to the robot base)
     */
    async SolveIK(pose: Mat, joints_approx: number[] | null = null, tool: Mat | null = null, reference: Mat | null = null): Promise<number[]> {
        // Apply tool and reference transformations if provided
        let targetPose = pose;
        if (tool !== null) {
            // Would need matrix inversion - simplified for now
            // In Python: pose = pose * robomath.invH(tool)
        }
        if (reference !== null) {
            // In Python: pose = reference * pose
        }

        let joints: number[];
        if (joints_approx === null) {
            this.link._send_line('G_IK');
            this.link._send_pose(targetPose);
            this.link._send_item(this);
            joints = await this.link._rec_array();
        } else {
            this.link._send_line('G_IK_jnts');
            this.link._send_pose(targetPose);
            this.link._send_array(joints_approx);
            this.link._send_item(this);
            joints = await this.link._rec_array();
        }
        await this.link._check_status();
        return joints;
    }

    /**
     * Calculates all inverse kinematics solutions for the specified robot and pose.
     * Returns a list of joints as a 2D matrix.
     * @param pose - Pose of the robot flange with respect to the robot base frame
     * @param tool - Tool pose with respect to the robot flange
     * @param reference - Reference pose
     */
    async SolveIK_All(pose: Mat, tool: Mat | null = null, reference: Mat | null = null): Promise<number[][]> {
        // Apply tool and reference transformations if provided
        let targetPose = pose;
        if (tool !== null) {
            // Would need matrix inversion
        }
        if (reference !== null) {
            // Would need matrix multiplication
        }

        this.link._send_line('G_IK_cmpl');
        this.link._send_pose(targetPose);
        this.link._send_item(this);
        const matrix = await this.link._rec_matrix();
        await this.link._check_status();
        return matrix;
    }

    // Connect and Move methods

    /**
     * Move a robot to a specific target ("Move Joint" mode).
     * This function waits until the robot finishes its movements.
     */
    async MoveJ(target: Item | number[] | Mat): Promise<void> {
        await this.link._moveX(target, this, MOVE_TYPE_JOINT, true);
    }

    /**
     * Move a robot to a specific target ("Move Linear" mode).
     * This function waits until the robot finishes its movements.
     */
    async MoveL(target: Item | number[] | Mat): Promise<void> {
        await this.link._moveX(target, this, MOVE_TYPE_LINEAR, true);
    }

    /**
     * Move a robot to a specific target ("Move Circular" mode).
     * @param target1 - Pose along the circle movement
     * @param target2 - Final circle target
     */
    async MoveC(target1: Item | number[] | Mat, target2: Item | number[] | Mat): Promise<void> {
        await this.link._moveC(target1, target2, this, true);
    }

    /**
     * Moves a robot to a specific target and stops when a specific input switch is detected.
     * @param target - Target to move to
     */
    async SearchL(target: Item | number[] | Mat): Promise<number[]> {
        this.link._send_line('SearchL');
        this.link._send_int(MOVE_TYPE_LINEARSEARCH);

        if (target instanceof Item) {
            this.link._send_int(3);
            this.link._send_array([]);
            this.link._send_item(target);
        } else if (Array.isArray(target)) {
            this.link._send_int(1);
            this.link._send_array(target);
            this.link._send_item(null);
        } else if (target instanceof Mat) {
            this.link._send_int(2);
            const mattr = target.tr();
            const flatPose = [...mattr.rows[0], ...mattr.rows[1], ...mattr.rows[2], ...mattr.rows[3]];
            this.link._send_array(flatPose);
            this.link._send_item(null);
        }

        this.link._send_item(this);
        await this.link._check_status();

        // Wait for movement with extended timeout
        const oldTimeout = this.link.TIMEOUT;
        this.link.COM?.setTimeout(360000);
        await this.link._check_status();
        this.link.COM?.setTimeout(oldTimeout);

        // Return the collision joints
        return this.Joints();
    }

    /**
     * Sets the linear speed of a robot.
     * @param speed_linear - Linear speed in mm/s (-1 = no change)
     * @param speed_joints - Joint speed in deg/s (-1 = no change)
     * @param accel_linear - Linear acceleration in mm/s^2 (-1 = no change)
     * @param accel_joints - Joint acceleration in deg/s^2 (-1 = no change)
     */
    async setSpeed(speed_linear: number, speed_joints: number = -1, accel_linear: number = -1, accel_joints: number = -1): Promise<Item> {
        this.link._send_line('S_Speed4');
        this.link._send_item(this);
        this.link._send_array([speed_linear, speed_joints, accel_linear, accel_joints]);
        await this.link._check_status();
        return this;
    }

    /**
     * Sets the rounding accuracy to smooth the edges of corners.
     * @param rounding_mm - Rounding accuracy in mm (-1 for best accuracy/point-to-point)
     */
    async setRounding(rounding_mm: number): Promise<Item> {
        this.link._send_line('S_ZoneData');
        this.link._send_int(rounding_mm * 1000);
        this.link._send_item(this);
        await this.link._check_status();
        return this;
    }

    /**
     * Checks if a robot or program is currently running (busy or moving).
     * Returns 1 if moving, 0 if stopped.
     */
    async Busy(): Promise<number> {
        this.link._send_line('IsBusy');
        this.link._send_item(this);
        const busy = await this.link._rec_int();
        await this.link._check_status();
        return busy;
    }

    /**
     * Stop a program or a robot.
     */
    async Stop(): Promise<void> {
        this.link._send_line('Stop');
        this.link._send_item(this);
        await this.link._check_status();
    }

    /**
     * Waits (blocks) until the robot finishes its movement.
     * @param timeout - Maximum time to wait in seconds
     */
    async WaitMove(timeout: number = 360000): Promise<void> {
        this.link._send_line('WaitMove');
        this.link._send_item(this);
        await this.link._check_status();
        const oldTimeout = this.link.TIMEOUT;
        this.link.COM?.setTimeout(Math.max(timeout * 1000, this.link.TIMEOUT));
        await this.link._check_status();
        this.link.COM?.setTimeout(oldTimeout);
    }

    /**
     * Wait until a program finishes or a robot completes its movement.
     */
    async WaitFinished(): Promise<void> {
        while (await this.Busy()) {
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }

    /**
     * Connect to a real robot and wait for a connection to succeed.
     * Returns 1 if connection succeeded, or 0 if it failed.
     * @param robot_ip - Robot IP (leave blank to use the IP selected in connection panel)
     * @param blocking - Wait for connection to complete
     */
    async ConnectRobot(robot_ip: string = '', blocking: boolean = true): Promise<number> {
        this.link._send_line('Connect2');
        this.link._send_item(this);
        this.link._send_line(robot_ip);
        this.link._send_int(blocking ? 1 : 0);
        const status = await this.link._rec_int();
        await this.link._check_status();
        return status;
    }

    /**
     * Disconnect from a real robot.
     * Returns 1 if disconnected successfully, 0 if it failed.
     */
    async DisconnectRobot(): Promise<number> {
        this.link._send_line('Disconnect');
        this.link._send_item(this);
        const status = await this.link._rec_int();
        await this.link._check_status();
        return status;
    }

    /**
     * Check connection status with a real robot.
     * Returns [status_code, status_message].
     */
    async ConnectedState(): Promise<[number, string]> {
        this.link._send_line('ConnectedState');
        this.link._send_item(this);
        const status = await this.link._rec_int();
        const msg = await this.link._rec_line();
        await this.link._check_status();
        return [status, msg];
    }

    /**
     * Returns the robot connection parameters.
     * Returns [robotIP, port, remote_path, FTP_user, FTP_pass].
     */
    async ConnectionParams(): Promise<[string, number, string, string, string]> {
        this.link._send_line('ConnectParams');
        this.link._send_item(this);
        const robot_ip = await this.link._rec_line();
        const port = await this.link._rec_int();
        const remote_path = await this.link._rec_line();
        const ftp_user = await this.link._rec_line();
        const ftp_pass = await this.link._rec_line();
        await this.link._check_status();
        return [robot_ip, port, remote_path, ftp_user, ftp_pass];
    }

    /**
     * Set the robot connection parameters.
     * @param robot_ip - Robot IP
     * @param port - Communication port
     * @param remote_path - Path to transfer files on the robot controller
     * @param ftp_user - FTP username
     * @param ftp_pass - FTP password
     */
    async setConnectionParams(robot_ip: string, port: number, remote_path: string, ftp_user: string, ftp_pass: string): Promise<void> {
        this.link._send_line('setConnectParams');
        this.link._send_item(this);
        this.link._send_line(robot_ip);
        this.link._send_int(port);
        this.link._send_line(remote_path);
        this.link._send_line(ftp_user);
        this.link._send_line(ftp_pass);
        await this.link._check_status();
    }

    // ============================================================
    // I/O and Program Methods (Task 12)
    // ============================================================

    /**
     * Set a Digital Output (DO).
     * @param io_var - Digital Output (string or number)
     * @param io_value - Value to set
     */
    async setDO(io_var: string | number, io_value: string | number): Promise<void> {
        this.link._send_line('setDO');
        this.link._send_item(this);
        this.link._send_line(String(io_var));
        this.link._send_line(String(io_value));
        await this.link._check_status();
    }

    /**
     * Set an Analog Output (AO).
     * @param io_var - Analog Output (string or number)
     * @param io_value - Value to set
     */
    async setAO(io_var: string | number, io_value: string | number): Promise<void> {
        this.link._send_line('setAO');
        this.link._send_item(this);
        this.link._send_line(String(io_var));
        this.link._send_line(String(io_value));
        await this.link._check_status();
    }

    /**
     * Get a Digital Input (DI).
     * @param io_var - Digital Input (string or number)
     */
    async getDI(io_var: string | number): Promise<string> {
        this.link._send_line('getDI');
        this.link._send_item(this);
        this.link._send_line(String(io_var));
        const value = await this.link._rec_line();
        await this.link._check_status();
        return value;
    }

    /**
     * Get an Analog Input (AI).
     * @param io_var - Analog Input (string or number)
     */
    async getAI(io_var: string | number): Promise<string> {
        this.link._send_line('getAI');
        this.link._send_item(this);
        this.link._send_line(String(io_var));
        const value = await this.link._rec_line();
        await this.link._check_status();
        return value;
    }

    /**
     * Wait for a digital input to attain a given value.
     * @param io_var - Digital input (string or number)
     * @param io_value - Value to wait for
     * @param timeout_ms - Timeout in milliseconds (-1 for infinite)
     */
    async waitDI(io_var: string | number, io_value: string | number, timeout_ms: number = -1): Promise<void> {
        this.link._send_line('waitDI');
        this.link._send_item(this);
        this.link._send_line(String(io_var));
        this.link._send_line(String(io_value));
        this.link._send_int(timeout_ms * 1000);
        await this.link._check_status();
    }

    /**
     * Pause instruction for a robot or insert a pause instruction to a program.
     * @param time_ms - Time in milliseconds (-1 to pause until resumed)
     */
    async Pause(time_ms: number = -1): Promise<void> {
        this.link._send_line('RunPause');
        this.link._send_item(this);
        this.link._send_int(time_ms * 1000);
        await this.link._check_status();
    }

    // ============================================================
    // Program Instruction Methods (Task 13)
    // ============================================================

    /**
     * Add a joint move instruction to a program.
     * @param target - Target item
     */
    async addMoveJ(target: Item): Promise<void> {
        this.link._send_line('Add_INSMOVE');
        this.link._send_item(target);
        this.link._send_item(this);
        this.link._send_int(MOVE_TYPE_JOINT);
        await this.link._check_status();
    }

    /**
     * Add a linear move instruction to a program.
     * @param target - Target item
     */
    async addMoveL(target: Item): Promise<void> {
        this.link._send_line('Add_INSMOVE');
        this.link._send_item(target);
        this.link._send_item(this);
        this.link._send_int(MOVE_TYPE_LINEAR);
        await this.link._check_status();
    }

    /**
     * Add a circular move instruction to a program.
     * @param target1 - Via target item
     * @param target2 - End target item
     */
    async addMoveC(target1: Item, target2: Item): Promise<void> {
        this.link._send_line('Add_INSMOVEC');
        this.link._send_item(target1);
        this.link._send_item(target2);
        this.link._send_item(this);
        await this.link._check_status();
    }

    /**
     * Returns the number of instructions in a program.
     */
    async InstructionCount(): Promise<number> {
        this.link._send_line('Prog_Nins');
        this.link._send_item(this);
        const count = await this.link._rec_int();
        await this.link._check_status();
        return count;
    }

    /**
     * Select an instruction in a program.
     * @param ins_id - Instruction ID to select (0-based)
     */
    async InstructionSelect(ins_id: number = -1): Promise<void> {
        this.link._send_line('Prog_SelIns');
        this.link._send_item(this);
        this.link._send_int(ins_id);
        await this.link._check_status();
    }

    /**
     * Delete an instruction from a program.
     * @param ins_id - Instruction ID to delete (0-based)
     */
    async InstructionDelete(ins_id: number = 0): Promise<boolean> {
        this.link._send_line('Prog_DelIns');
        this.link._send_item(this);
        this.link._send_int(ins_id);
        const success = await this.link._rec_int();
        await this.link._check_status();
        return success > 0;
    }

    /**
     * Show or hide all program instructions.
     * @param show - True to show, false to hide
     */
    async ShowInstructions(show: boolean = true): Promise<void> {
        this.link._send_line('Prog_ShowIns');
        this.link._send_item(this);
        this.link._send_int(show ? 1 : 0);
        await this.link._check_status();
    }

    /**
     * Show or hide all program targets.
     * @param show - True to show, false to hide
     */
    async ShowTargets(show: boolean = true): Promise<void> {
        this.link._send_line('Prog_ShowTargets');
        this.link._send_item(this);
        this.link._send_int(show ? 1 : 0);
        await this.link._check_status();
    }

    /**
     * Set a specific item parameter.
     * Select Tools-Run Script-Show Commands to see all available commands for items.
     * @param param - Parameter/command name
     * @param value - Parameter value (optional, not all commands require a value)
     * @returns Command result string
     */
    async setParam(param: string, value: string = ''): Promise<string> {
        this.link._send_line('ICMD');
        this.link._send_item(this);
        this.link._send_line(param);
        this.link._send_line(value.replace(/\n/g, '<br>'));
        const result = await this.link._rec_line();
        await this.link._check_status();
        return result;
    }

    // ============================================================
    // Speed and Acceleration Shortcut Methods
    // ============================================================

    /**
     * Sets the linear acceleration of a robot in mm/s².
     * @param accel_linear - Acceleration in mm/s²
     */
    async setAcceleration(accel_linear: number): Promise<Item> {
        return this.setSpeed(-1, -1, accel_linear, -1);
    }

    /**
     * Sets the joint speed of a robot in deg/s for rotary joints and mm/s for linear joints.
     * @param speed_joints - Speed in deg/s (rotary) or mm/s (linear)
     */
    async setSpeedJoints(speed_joints: number): Promise<Item> {
        return this.setSpeed(-1, speed_joints, -1, -1);
    }

    /**
     * Sets the joint acceleration of a robot in deg/s² for rotary joints and mm/s² for linear joints.
     * @param accel_joints - Acceleration in deg/s² (rotary) or mm/s² (linear)
     */
    async setAccelerationJoints(accel_joints: number): Promise<Item> {
        return this.setSpeed(-1, -1, -1, accel_joints);
    }

    // ============================================================
    // Collision Test Methods
    // ============================================================

    /**
     * Checks if a joint movement is feasible and free of collisions.
     * The robot will move to the collision point if a collision is detected.
     * @param j1 - Start joints
     * @param j2 - End joints
     * @param minstep_deg - Maximum joint step in degrees (-1 for default)
     * @returns 0 if no collision, >0 for number of collision pairs
     */
    async MoveJ_Test(j1: number[], j2: number[], minstep_deg: number = -1): Promise<number> {
        this.link._send_line('CollisionMove');
        this.link._send_item(this);
        this.link._send_array(j1);
        this.link._send_array(j2);
        this.link._send_int(minstep_deg * 1000);
        // Extended timeout for long operations
        const oldTimeout = this.link.TIMEOUT;
        this.link.COM?.setTimeout(Math.max(3600000, this.link.TIMEOUT));
        const collision = await this.link._rec_int();
        this.link.COM?.setTimeout(oldTimeout);
        await this.link._check_status();
        return collision;
    }

    /**
     * Checks if a joint movement with blending is feasible and free of collisions.
     * @param j1 - Start joints
     * @param j2 - Via joints
     * @param j3 - Final destination joints
     * @param blend_deg - Blend radius in degrees
     * @param minstep_deg - Maximum joint step in degrees (-1 for default)
     * @returns 0 if no collision, >0 for number of collision pairs
     */
    async MoveJ_Test_Blend(j1: number[], j2: number[], j3: number[], blend_deg: number = 5, minstep_deg: number = -1): Promise<number> {
        this.link._send_line('CollisionMoveBlend');
        this.link._send_item(this);
        this.link._send_array(j1);
        this.link._send_array(j2);
        this.link._send_array(j3);
        this.link._send_int(minstep_deg * 1000);
        this.link._send_int(blend_deg * 1000);
        // Extended timeout for long operations
        const oldTimeout = this.link.TIMEOUT;
        this.link.COM?.setTimeout(Math.max(3600000, this.link.TIMEOUT));
        const collision = await this.link._rec_int();
        this.link.COM?.setTimeout(oldTimeout);
        await this.link._check_status();
        return collision;
    }

    /**
     * Checks if a linear movement is feasible and free of collisions.
     * @param j1 - Start joints
     * @param pose - End pose (TCP with respect to reference frame)
     * @param minstep_mm - Linear step in mm (-1 for default)
     * @returns 0 if no collision, -2 if unreachable, -1 if no linear path, >0 for collision pairs
     */
    async MoveL_Test(j1: number[], pose: Mat, minstep_mm: number = -1): Promise<number> {
        this.link._send_line('CollisionMoveL');
        this.link._send_item(this);
        this.link._send_array(j1);
        this.link._send_pose(pose);
        this.link._send_int(minstep_mm * 1000);
        // Extended timeout for long operations
        const oldTimeout = this.link.TIMEOUT;
        this.link.COM?.setTimeout(Math.max(3600000, this.link.TIMEOUT));
        const collision = await this.link._rec_int();
        this.link.COM?.setTimeout(oldTimeout);
        await this.link._check_status();
        return collision;
    }

    // ============================================================
    // Robot State Methods
    // ============================================================

    /**
     * Return the current joint position from the simulator only (never from real robot).
     * Use this when RoboDK is connected to a real robot but you need simulator joints.
     * @returns Joint values from simulator
     */
    async SimulatorJoints(): Promise<number[]> {
        this.link._send_line('G_Thetas_Sim');
        this.link._send_item(this);
        const joints = await this.link._rec_array();
        await this.link._check_status();
        return joints;
    }

    /**
     * Returns the poses of the joint links for a provided robot configuration.
     * @param joints - Robot joints (null for current position)
     * @returns Array of 4x4 homogeneous matrices (index 0 is base frame)
     */
    async JointPoses(joints: number[] | null = null): Promise<Mat[]> {
        this.link._send_line('G_LinkPoses');
        this.link._send_item(this);
        this.link._send_array(joints || []);
        const nlinks = await this.link._rec_int();
        const poses: Mat[] = [];
        for (let i = 0; i < nlinks; i++) {
            poses.push(await this.link._rec_pose());
        }
        await this.link._check_status();
        return poses;
    }

    /**
     * Returns the robot configuration state for a set of robot joints.
     * @param joints - Robot joints
     * @returns Configuration state [REAR, LOWERARM, FLIP, turns]
     */
    async JointsConfig(joints: number[]): Promise<number[]> {
        this.link._send_line('G_Thetas_Config');
        this.link._send_array(joints);
        this.link._send_item(this);
        const config = await this.link._rec_array();
        await this.link._check_status();
        return config;
    }

    /**
     * Filters a target to improve accuracy. Requires a calibrated robot.
     * @param pose - Pose of the robot TCP with respect to reference frame
     * @param joints_approx - Approximate joints to define preferred configuration
     * @returns Tuple of [filtered_pose, filtered_joints]
     */
    async FilterTarget(pose: Mat, joints_approx: number[] | null = null): Promise<[Mat, number[]]> {
        this.link._send_line('FilterTarget');
        this.link._send_pose(pose);
        this.link._send_array(joints_approx || [0, 0, 0, 0, 0, 0]);
        this.link._send_item(this);
        const pose_filtered = await this.link._rec_pose();
        const joints_filtered = await this.link._rec_array();
        await this.link._check_status();
        return [pose_filtered, joints_filtered];
    }

    /**
     * Connect to a real robot with retry logic.
     * @param robot_ip - Robot IP (blank for connection panel IP)
     * @param max_attempts - Maximum connection attempts
     * @param wait_connection - Seconds to wait between attempts
     * @returns Connection state (0 = ready, <0 = error)
     */
    async ConnectSafe(robot_ip: string = '', max_attempts: number = 5, wait_connection: number = 4): Promise<number> {
        // Check if already connected
        let [con_status, status_msg] = await this.ConnectedState();
        console.log(status_msg);
        if (con_status === ROBOTCOM_READY) {
            return con_status;
        }

        const refresh_rate = 200; // ms
        let trycount = 0;
        let timer1 = Date.now();

        // Start non-blocking connection
        await this.ConnectRobot(robot_ip, false);
        await new Promise(resolve => setTimeout(resolve, refresh_rate));

        while (true) {
            // Poll connection status
            for (let i = 0; i < 10; i++) {
                [con_status, status_msg] = await this.ConnectedState();
                console.log(status_msg);
                if (con_status === ROBOTCOM_READY) {
                    return con_status;
                }
                await new Promise(resolve => setTimeout(resolve, refresh_rate));
            }

            // If disconnected, try to reconnect
            if (con_status < 0) {
                console.log('Trying to reconnect...');
                await this.DisconnectRobot();
            }

            await new Promise(resolve => setTimeout(resolve, refresh_rate));
            await this.ConnectRobot(robot_ip, false);

            // Check timeout
            if (Date.now() - timer1 > wait_connection * 1000) {
                timer1 = Date.now();
                trycount++;
                if (trycount >= max_attempts) {
                    console.log('Failed to connect: Timed out');
                    break;
                }
            }

            await new Promise(resolve => setTimeout(resolve, refresh_rate));
        }

        return con_status;
    }
}

