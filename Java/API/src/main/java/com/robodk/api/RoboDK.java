package com.robodk.api;

import com.robodk.api.exception.RdkException;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.Closeable;
import java.io.DataInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Entry point to the RoboDK API.
 * <p>
 * A {@code RoboDK} instance represents a TCP/IP link to a running RoboDK station. Every
 * interaction with the station tree (robots, reference frames, tools, targets, programs, ...)
 * goes through this class, either directly or through an {@link Item} obtained from it.
 * <p>
 * If no RoboDK instance is already running on the target host, {@link #connect()} launches one
 * itself — on Windows, Linux, and macOS alike, see {@link #findRoboDKExecutable()} — the same
 * way the reference Python API does (the reference C# API only supports this on Windows).
 * <p>
 * This class also implements the low level RoboDK API wire protocol: a simple, synchronous,
 * request/response protocol made of newline terminated ASCII commands followed by binary
 * arguments (32-bit signed integers and 64-bit IEEE 754 doubles, both big-endian). The
 * {@code sendXxx}/{@code recvXxx} methods below are the Java equivalent of the
 * {@code send_xxx}/{@code rec_xxx} methods of the reference RoboDK C# and Python APIs.
 *
 * <pre>{@code
 * try (RoboDK robodk = new RoboDK()) {
 *     robodk.connect();
 *     System.out.println("Connected to RoboDK " + robodk.version());
 *     for (String name : robodk.getItemListNames(ItemType.ROBOT)) {
 *         System.out.println("Robot found: " + name);
 *     }
 * }
 * }</pre>
 */
public class RoboDK implements Closeable {

    /** Default TCP port used by the RoboDK API server (first port of the default range). */
    public static final int DEFAULT_PORT_BASE = 20500;

    /** Default number of consecutive ports scanned when looking for a running RoboDK instance. */
    public static final int DEFAULT_PORT_RANGE = 2;

    private static final String API_NAME = "RDK_API";

    private final String robodkServerIp;
    private final int robodkServerStartPort;
    private final int robodkServerEndPort;

    private Socket socket;
    private InputStream input;
    private OutputStream output;

    private int socketTimeoutMilliseconds = 10_000;
    private int connectedPort = -1;
    private int apiVersion;
    private int robodkBuild;
    private String lastStatusMessage = "";

    /** If true, checks that provided items exist in memory and that poses are homogeneous. */
    private boolean safeMode = true;

    /** Delays screen refresh until 100 ms after the last call, for faster scripts. */
    private boolean autoUpdate = false;

    /** Explicit path to the RoboDK executable; {@code null} means auto-detect. */
    private String applicationDir;

    /** Extra command-line arguments passed to RoboDK when it is launched, e.g. {@code "-NOSPLASH"}. */
    private String[] commandLineArgs = new String[0];

    /** If true, {@link #connect()} always launches a fresh RoboDK instance. */
    private boolean startNewInstance = false;

    /** How long {@link #connect()} waits for a newly launched RoboDK to report it is running. */
    private int startTimeoutMilliseconds = 60_000;

    /** The RoboDK process this instance launched, or {@code null} if it attached to one already running. */
    private Process process;

    /**
     * Creates a new link to RoboDK, connecting to a station running on {@code localhost} using
     * the default RoboDK API port range (20500-20502).
     */
    public RoboDK() {
        this("localhost", DEFAULT_PORT_BASE, DEFAULT_PORT_BASE + DEFAULT_PORT_RANGE);
    }

    /**
     * Creates a new link to RoboDK running on the given host/port.
     *
     * @param robodkServerIp host name or IP address where RoboDK is running
     * @param robodkServerPort single TCP port to connect to
     */
    public RoboDK(String robodkServerIp, int robodkServerPort) {
        this(robodkServerIp, robodkServerPort, robodkServerPort);
    }

    /**
     * Creates a new link to RoboDK, scanning a range of consecutive ports for a running
     * instance.
     *
     * @param robodkServerIp host name or IP address where RoboDK is running
     * @param robodkServerStartPort first port to try
     * @param robodkServerEndPort last port to try (inclusive)
     */
    public RoboDK(String robodkServerIp, int robodkServerStartPort, int robodkServerEndPort) {
        this.robodkServerIp = robodkServerIp;
        this.robodkServerStartPort = robodkServerStartPort;
        this.robodkServerEndPort = robodkServerEndPort;
    }

    // ------------------------------------------------------------------------------------
    // Connection management
    // ------------------------------------------------------------------------------------

    /**
     * Connects to a RoboDK station.
     * <p>
     * Unless {@link #isStartNewInstance()} is set, this first scans the configured port range
     * for an already running instance. If none is found and the target host is {@code
     * localhost} (or {@link #isStartNewInstance()} is set), a new RoboDK instance is launched —
     * on Windows, Linux, and macOS alike — and this connects to it. See
     * {@link #findRoboDKExecutable()} for how the RoboDK executable is located, and
     * {@link #setApplicationDir(String)} to override it explicitly.
     *
     * @return {@code true} if the connection (including the API handshake) succeeded
     */
    public boolean connect() {
        disconnect();

        if (!startNewInstance) {
            for (int port = robodkServerStartPort; port <= robodkServerEndPort; port++) {
                if (tryConnect(port) && verifyConnection()) {
                    connectedPort = port;
                    return true;
                }
                disconnect();
            }
        }

        if (startNewInstance || isLocalHost(robodkServerIp)) {
            return startNewRoboDKInstanceAndConnect();
        }

        return false;
    }

    /**
     * Launches a new RoboDK instance (asking it to listen on {@link #robodkServerStartPort} via
     * the {@code -PORT=} command-line argument) and connects to it.
     *
     * @throws RdkException if no RoboDK executable could be found or resolved, or if the
     *                       process could not be started
     */
    private boolean startNewRoboDKInstanceAndConnect() {
        String executable = applicationDir != null && !applicationDir.isEmpty()
                ? applicationDir
                : findRoboDKExecutable();
        if (executable == null) {
            throw new RdkException("Could not find a RoboDK installation on this machine. "
                    + "Install RoboDK from https://robodk.com/download, or set the executable "
                    + "path explicitly with setApplicationDir(...).");
        }

        File executableFile = new File(executable);
        if (!executableFile.isFile()) {
            throw new RdkException("RoboDK executable not found: " + executable);
        }
        // Best-effort: the installer normally sets this, but make sure we can actually run it
        // (relevant on Linux/macOS, where the executable bit can be lost, e.g. after a zip
        // extraction).
        if (!executableFile.canExecute()) {
            executableFile.setExecutable(true);
        }

        List<String> command = new ArrayList<>();
        command.add(executableFile.getPath());
        command.add("-PORT=" + robodkServerStartPort);
        command.addAll(Arrays.asList(commandLineArgs));

        try {
            process = new ProcessBuilder(command)
                    .redirectErrorStream(true)
                    .start();
        } catch (IOException e) {
            throw new RdkException("Unable to start RoboDK: " + executableFile.getPath(), e);
        }

        if (!waitForRoboDKToStart(process)) {
            return false;
        }

        if (tryConnect(robodkServerStartPort) && verifyConnection()) {
            connectedPort = robodkServerStartPort;
            return true;
        }
        disconnect();
        return false;
    }

    /**
     * Reads the launched process's output until a line containing "running" is seen (matching
     * both the C# and Python reference implementations' startup detection), the process exits,
     * or {@link #startTimeoutMilliseconds} elapses. Once detected, a daemon thread keeps
     * draining the process's output for its remaining lifetime so its pipe never fills up and
     * blocks it.
     */
    private boolean waitForRoboDKToStart(Process process) {
        BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));
        long deadline = System.currentTimeMillis() + startTimeoutMilliseconds;
        boolean started = false;
        try {
            String line;
            while (System.currentTimeMillis() < deadline && (line = reader.readLine()) != null) {
                if (line.toLowerCase(Locale.ROOT).contains("running")) {
                    started = true;
                    break;
                }
            }
        } catch (IOException e) {
            return false;
        }

        if (!started) {
            return false;
        }

        Thread drainer = new Thread(() -> {
            try {
                while (reader.readLine() != null) {
                    // Discard: we just need to keep the pipe from filling up.
                }
            } catch (IOException ignored) {
                // The process ended or its output stream was closed; nothing left to drain.
            }
        }, "robodk-output-drainer");
        drainer.setDaemon(true);
        drainer.start();

        return true;
    }

    private static boolean isLocalHost(String host) {
        return "localhost".equalsIgnoreCase(host)
                || "127.0.0.1".equals(host)
                || "::1".equals(host);
    }

    private boolean tryConnect(int port) {
        try {
            Socket newSocket = new Socket();
            newSocket.connect(new InetSocketAddress(robodkServerIp, port), 1000);
            newSocket.setTcpNoDelay(true);
            newSocket.setSoTimeout(socketTimeoutMilliseconds);
            this.socket = newSocket;
            this.input = new BufferedInputStream(newSocket.getInputStream());
            this.output = new BufferedOutputStream(newSocket.getOutputStream());
            return true;
        } catch (IOException e) {
            this.socket = null;
            this.input = null;
            this.output = null;
            return false;
        }
    }

    /** Performs the RoboDK API handshake on a freshly opened socket. */
    private boolean verifyConnection() {
        try {
            sendLine(API_NAME);
            sendInt(0);
            String response = recvLine();
            apiVersion = recvInt();
            robodkBuild = recvInt();
            checkStatus();
            return API_NAME.equals(response);
        } catch (RuntimeException e) {
            return false;
        }
    }

    /**
     * Closes the connection to RoboDK. Does nothing if not connected.
     */
    public void disconnect() {
        if (socket != null) {
            try {
                socket.close();
            } catch (IOException ignored) {
                // Nothing to do, the socket is being discarded anyway.
            }
        }
        socket = null;
        input = null;
        output = null;
        connectedPort = -1;
    }

    @Override
    public void close() {
        disconnect();
    }

    /**
     * Returns {@code true} if this instance currently holds an open socket to RoboDK.
     */
    public boolean isConnected() {
        return socket != null && socket.isConnected() && !socket.isClosed();
    }

    /**
     * Ensures there is a live connection to RoboDK, (re)connecting if necessary.
     *
     * @throws RdkException if not connected and a new connection attempt fails
     */
    void checkConnection() {
        if (!isConnected() && !connect()) {
            throw new RdkException("Can't connect to RoboDK API. Is RoboDK running?");
        }
    }

    // ------------------------------------------------------------------------------------
    // Properties
    // ------------------------------------------------------------------------------------

    /** RoboDK API protocol version reported by the station during the handshake. */
    public int getApiVersion() {
        return apiVersion;
    }

    /** RoboDK build id reported by the station during the handshake. */
    public int getRoboDKBuild() {
        return robodkBuild;
    }

    /** TCP port this instance is currently connected to, or -1 if not connected. */
    public int getConnectedPort() {
        return connectedPort;
    }

    /** Last status/warning/error message received from RoboDK. */
    public String getLastStatusMessage() {
        return lastStatusMessage;
    }

    public boolean isSafeMode() {
        return safeMode;
    }

    public void setSafeMode(boolean safeMode) {
        this.safeMode = safeMode;
    }

    public boolean isAutoUpdate() {
        return autoUpdate;
    }

    public void setAutoUpdate(boolean autoUpdate) {
        this.autoUpdate = autoUpdate;
    }

    /** Socket read/write timeout, in milliseconds. */
    public int getSocketTimeoutMilliseconds() {
        return socketTimeoutMilliseconds;
    }

    /** @see #getSocketTimeoutMilliseconds() */
    public void setSocketTimeoutMilliseconds(int socketTimeoutMilliseconds) {
        this.socketTimeoutMilliseconds = socketTimeoutMilliseconds;
        if (socket != null) {
            try {
                socket.setSoTimeout(socketTimeoutMilliseconds);
            } catch (IOException e) {
                throw new RdkException("Unable to update the socket timeout", e);
            }
        }
    }

    /**
     * Explicit path to the RoboDK executable to use when {@link #connect()} needs to launch a
     * new instance, or {@code null} (the default) to auto-detect it with
     * {@link #findRoboDKExecutable()}.
     */
    public String getApplicationDir() {
        return applicationDir;
    }

    /** @see #getApplicationDir() */
    public void setApplicationDir(String applicationDir) {
        this.applicationDir = applicationDir;
    }

    /**
     * Extra command-line arguments appended when {@link #connect()} launches a new RoboDK
     * instance (for example {@code "-NOSPLASH"}, {@code "-NOSHOW"}). Empty by default. These
     * have no effect if RoboDK was already running and this instance just attached to it.
     */
    public String[] getCommandLineArgs() {
        return commandLineArgs.clone();
    }

    /** @see #getCommandLineArgs() */
    public void setCommandLineArgs(String... commandLineArgs) {
        this.commandLineArgs = commandLineArgs == null ? new String[0] : commandLineArgs.clone();
    }

    /**
     * If {@code true}, {@link #connect()} always launches a fresh RoboDK instance instead of
     * first trying to attach to one already running. Defaults to {@code false}.
     */
    public boolean isStartNewInstance() {
        return startNewInstance;
    }

    /** @see #isStartNewInstance() */
    public void setStartNewInstance(boolean startNewInstance) {
        this.startNewInstance = startNewInstance;
    }

    /**
     * How long, in milliseconds, {@link #connect()} waits for a newly launched RoboDK instance
     * to report that it is running before giving up. Defaults to 60000 (60 seconds); a slow
     * first-time startup (for example while a license is being validated) may need a larger
     * value.
     */
    public int getStartTimeoutMilliseconds() {
        return startTimeoutMilliseconds;
    }

    /** @see #getStartTimeoutMilliseconds() */
    public void setStartTimeoutMilliseconds(int startTimeoutMilliseconds) {
        this.startTimeoutMilliseconds = startTimeoutMilliseconds;
    }

    /**
     * The RoboDK process this instance launched via {@link #connect()}, or {@code null} if it
     * instead attached to an already running instance (or hasn't connected yet).
     */
    public Process getProcess() {
        return process;
    }

    /**
     * Attempts to find the RoboDK executable on this machine: Windows (via the
     * {@code HKLM\SOFTWARE\RoboDK} registry key written by the RoboDK installer), Linux
     * ({@code ~/RoboDK/bin/RoboDK}), and macOS ({@code ~/Applications/RoboDK.app/...} or
     * {@code ~/RoboDK/RoboDK.app/...}).
     *
     * @return the absolute path to the RoboDK executable, or {@code null} if none was found
     */
    public static String findRoboDKExecutable() {
        return RoboDKLocator.findExecutable();
    }

    /**
     * Returns {@code true} if a RoboDK installation was found on this machine (see
     * {@link #findRoboDKExecutable()}).
     */
    public static boolean isRoboDKInstallFound() {
        return findRoboDKExecutable() != null;
    }

    // ------------------------------------------------------------------------------------
    // Public API calls
    // ------------------------------------------------------------------------------------

    /**
     * Returns the RoboDK version string (for example {@code "5.9.0"}).
     */
    public String version() {
        checkConnection();
        sendLine("Version");
        String appName = recvLine();
        int bitArch = recvInt();
        String version = recvLine();
        String dateBuild = recvLine();
        checkStatus();
        return version;
    }

    /**
     * Closes RoboDK. This will close the RoboDK window and the API connection.
     */
    public void closeRoboDK() {
        checkConnection();
        sendLine("QUIT");
        checkStatus();
        disconnect();
        process = null;
    }

    /**
     * Renders (refreshes) the 3D view.
     *
     * @param alwaysRender if false, RoboDK may skip the refresh to favor performance
     */
    public void render(boolean alwaysRender) {
        checkConnection();
        boolean autoRender = !alwaysRender;
        sendLine("Render");
        sendInt(autoRender ? 1 : 0);
        checkStatus();
    }

    /**
     * Returns the first item found in the station tree matching the given name, or an invalid
     * item (see {@link Item#isValid()}) if not found.
     *
     * @param name exact item name, as displayed in the RoboDK station tree
     * @param itemType restricts the search to a given item type, or {@link ItemType#ANY}
     */
    public Item getItemByName(String name, ItemType itemType) {
        checkConnection();
        if (itemType == null || itemType == ItemType.ANY) {
            sendLine("G_Item");
            sendLine(name);
        } else {
            sendLine("G_Item2");
            sendLine(name);
            sendInt(itemType.getValue());
        }
        Item item = recvItem();
        checkStatus();
        return item;
    }

    /**
     * Convenience overload of {@link #getItemByName(String, ItemType)} that searches for any
     * item type.
     */
    public Item getItemByName(String name) {
        return getItemByName(name, ItemType.ANY);
    }

    /**
     * Returns the names of every item in the station tree, optionally filtered by type.
     */
    public List<String> getItemListNames(ItemType itemType) {
        checkConnection();
        if (itemType == null || itemType == ItemType.ANY) {
            sendLine("G_List_Items");
        } else {
            sendLine("G_List_Items_Type");
            sendInt(itemType.getValue());
        }
        int itemCount = recvInt();
        List<String> names = new ArrayList<>(itemCount);
        for (int i = 0; i < itemCount; i++) {
            names.add(recvLine());
        }
        checkStatus();
        return names;
    }

    /**
     * Returns every item in the station tree, optionally filtered by type.
     */
    public List<Item> getItemList(ItemType itemType) {
        checkConnection();
        if (itemType == null || itemType == ItemType.ANY) {
            sendLine("G_List_Items_ptr");
        } else {
            sendLine("G_List_Items_Type_ptr");
            sendInt(itemType.getValue());
        }
        int itemCount = recvInt();
        List<Item> items = new ArrayList<>(itemCount);
        for (int i = 0; i < itemCount; i++) {
            items.add(recvItem());
        }
        checkStatus();
        return items;
    }

    /**
     * Convenience overload of {@link #getItemList(ItemType)} that returns every item in the
     * station tree.
     */
    public List<Item> getItemList() {
        return getItemList(ItemType.ANY);
    }

    // ------------------------------------------------------------------------------------
    // Station tree: adding items
    // ------------------------------------------------------------------------------------

    /**
     * Adds a new, empty station to the project and returns it.
     */
    public Item addStation(String name) {
        checkConnection();
        sendLine("NewStation");
        sendLine(name);
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /**
     * Adds a new reference frame to the station tree.
     *
     * @param name name of the new reference frame
     * @param parent item to attach the new reference frame to (for example another reference
     *               frame), or {@code null} to attach it to the active station
     */
    public Item addFrame(String name, Item parent) {
        checkConnection();
        sendLine("Add_FRAME");
        sendLine(name);
        sendItem(parent);
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /** @see #addFrame(String, Item) */
    public Item addFrame(String name) {
        return addFrame(name, null);
    }

    /**
     * Adds a new target that can be reached with a robot.
     *
     * @param name name of the new target
     * @param parent reference frame to attach the target to, or {@code null}
     * @param robot robot that will be used to reach this target, or {@code null}
     */
    public Item addTarget(String name, Item parent, Item robot) {
        checkConnection();
        sendLine("Add_TARGET");
        sendLine(name);
        sendItem(parent);
        sendItem(robot);
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /** @see #addTarget(String, Item, Item) */
    public Item addTarget(String name, Item parent) {
        return addTarget(name, parent, null);
    }

    /** @see #addTarget(String, Item, Item) */
    public Item addTarget(String name) {
        return addTarget(name, null, null);
    }

    /**
     * Adds a new, empty program to the station tree. Programs can be used to simulate a
     * sequence, generate vendor-specific robot programs (offline programming), or run programs
     * on the physical robot (online programming).
     *
     * @param name name of the new program
     * @param robot robot used by this program, or {@code null} if the station has a single robot
     */
    public Item addProgram(String name, Item robot) {
        checkConnection();
        sendLine("Add_PROG");
        sendLine(name);
        sendItem(robot);
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /** @see #addProgram(String, Item) */
    public Item addProgram(String name) {
        return addProgram(name, null);
    }

    /**
     * Loads a file (an object, a robot, a tool, another station, a robot program, ...) into the
     * open station and returns the newly added item.
     *
     * @param filename absolute path to the file to load
     * @param parent item to attach the newly loaded item to, or {@code null}
     * @throws RdkException if RoboDK failed to load the file
     */
    public Item addFile(String filename, Item parent) {
        checkConnection();
        sendLine("Add");
        sendLine(filename);
        sendItem(parent);
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(60_000, previousTimeout));
        Item newItem;
        try {
            newItem = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return newItem;
    }

    /** @see #addFile(String, Item) */
    public Item addFile(String filename) {
        return addFile(filename, null);
    }

    /**
     * Adds a shape provided as a list of triangles (each group of 3 consecutive points forms one
     * triangle) to the station, or to an existing object.
     *
     * @param trianglePoints 3xN (or 6xN, with per-vertex normals) matrix of points, N a multiple of 3
     * @param addTo existing object to add the shape to, or {@code null} to create a new object
     * @param shapeOverride if {@code true}, replaces {@code addTo}'s current shape instead of adding to it
     * @param color RGBA color in the 0-1 range (4 values), or {@code null} for the default gray
     */
    public Item addShape(Mat trianglePoints, Item addTo, boolean shapeOverride, double[] color) {
        double[] rgba = color != null ? color : new double[] {0.5, 0.5, 0.5, 1.0};
        checkColor(rgba);
        checkConnection();
        sendLine("AddShape3");
        sendMatrix(trianglePoints);
        sendItem(addTo);
        sendInt(shapeOverride ? 1 : 0);
        sendArray(rgba);
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Item newItem;
        try {
            newItem = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return newItem;
    }

    /** @see #addShape(Mat, Item, boolean, double[]) */
    public Item addShape(Mat trianglePoints, Item addTo) {
        return addShape(trianglePoints, addTo, false, null);
    }

    /** @see #addShape(Mat, Item, boolean, double[]) */
    public Item addShape(Mat trianglePoints) {
        return addShape(trianglePoints, null, false, null);
    }

    /**
     * Adds a curve provided as a list of points to the station.
     *
     * @param curvePoints 3xN (or 6xN, with per-vertex normals) matrix of points
     * @param referenceObject item to attach the newly added geometry to, or {@code null}
     * @param addToRef if {@code true}, the curve is added as part of {@code referenceObject}
     *                 (a reference object must be provided)
     * @param projectionType how the curve is projected onto {@code referenceObject}'s surface
     */
    public Item addCurve(Mat curvePoints, Item referenceObject, boolean addToRef, ProjectionType projectionType) {
        checkConnection();
        sendLine("AddWire");
        sendMatrix(curvePoints);
        sendItem(referenceObject);
        sendInt(addToRef ? 1 : 0);
        sendInt(projectionType.getValue());
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Item newItem;
        try {
            newItem = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return newItem;
    }

    /** @see #addCurve(Mat, Item, boolean, ProjectionType) */
    public Item addCurve(Mat curvePoints) {
        return addCurve(curvePoints, null, false, ProjectionType.ALONG_NORMAL_RECALC);
    }

    /**
     * Adds a list of points to the station.
     *
     * @param points 3xN (or 6xN, with per-vertex normals) matrix of points
     * @param referenceObject item to attach the newly added geometry to, or {@code null}
     * @param addToRef if {@code true}, the points are added as part of {@code referenceObject}
     * @param projectionType how the points are projected onto {@code referenceObject}'s surface
     */
    public Item addPoints(Mat points, Item referenceObject, boolean addToRef, ProjectionType projectionType) {
        checkConnection();
        sendLine("AddPoints");
        sendMatrix(points);
        sendItem(referenceObject);
        sendInt(addToRef ? 1 : 0);
        sendInt(projectionType.getValue());
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Item newItem;
        try {
            newItem = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return newItem;
    }

    /** @see #addPoints(Mat, Item, boolean, ProjectionType) */
    public Item addPoints(Mat points) {
        return addPoints(points, null, false, ProjectionType.ALONG_NORMAL_RECALC);
    }

    /**
     * Projects a list of points onto an object's surface.
     */
    public Mat projectPoints(Mat points, Item objectProject, ProjectionType projectionType) {
        checkConnection();
        sendLine("ProjectPoints");
        sendMatrix(points);
        sendItem(objectProject);
        sendInt(projectionType.getValue());
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Mat projected;
        try {
            projected = recvMatrix();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return projected;
    }

    // ------------------------------------------------------------------------------------
    // Station management
    // ------------------------------------------------------------------------------------

    /**
     * Saves an item (or, if {@code itemSave} is {@code null}, the whole open station) to a file.
     */
    public void save(String filename, Item itemSave) {
        checkConnection();
        sendLine("Save");
        sendLine(filename);
        sendItem(itemSave);
        checkStatus();
    }

    /** @see #save(String, Item) */
    public void save(String filename) {
        save(filename, null);
    }

    /**
     * Closes the current station without saving it.
     */
    public void closeStation() {
        checkConnection();
        sendLine("RemoveStn");
        checkStatus();
    }

    /**
     * Returns the currently active station.
     */
    public Item getActiveStation() {
        checkConnection();
        sendLine("G_ActiveStn");
        Item station = recvItem();
        checkStatus();
        return station;
    }

    /**
     * Sets the currently active station.
     */
    public void setActiveStation(Item station) {
        checkConnection();
        sendLine("S_ActiveStn");
        sendItem(station);
        checkStatus();
    }

    /**
     * Makes a copy of an item (and, optionally, its children) to the clipboard, to be inserted
     * with {@link #paste(Item)}.
     */
    public void copy(Item item, boolean copyChildren) {
        checkConnection();
        sendLine("Copy2");
        sendItem(item);
        sendInt(copyChildren ? 1 : 0);
        checkStatus();
    }

    /** @see #copy(Item, boolean) */
    public void copy(Item item) {
        copy(item, true);
    }

    /**
     * Pastes the item previously copied with {@link #copy(Item, boolean)} into the station,
     * attached to {@code pasteTo}.
     */
    public Item paste(Item pasteTo) {
        checkConnection();
        sendLine("Paste");
        sendItem(pasteTo);
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /** @see #paste(Item) */
    public Item paste() {
        return paste(null);
    }

    /**
     * Removes several items from the station in a single call.
     */
    public void delete(List<Item> items) {
        checkConnection();
        sendLine("RemoveLst");
        sendInt(items.size());
        for (Item item : items) {
            sendItem(item);
        }
        checkStatus();
    }

    /**
     * Shows a text message. If {@code popup} is {@code true}, this blocks until the user
     * dismisses the message box; otherwise the message is shown in the status bar only.
     */
    public void showMessage(String message, boolean popup) {
        checkConnection();
        if (popup) {
            sendLine("ShowMessage");
            sendLine(message);
            int previousTimeout = socketTimeoutMilliseconds;
            setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
            try {
                checkStatus();
            } finally {
                setSocketTimeoutMilliseconds(previousTimeout);
            }
        } else {
            sendLine("ShowMessageStatus");
            sendLine(message);
            checkStatus();
        }
    }

    /** @see #showMessage(String, boolean) */
    public void showMessage(String message) {
        showMessage(message, true);
    }

    /**
     * Shows the RoboDK main window and brings it to the front.
     */
    public void showRoboDK() {
        checkConnection();
        sendLine("RAISE");
        checkStatus();
    }

    /**
     * Hides the RoboDK main window.
     */
    public void hideRoboDK() {
        checkConnection();
        sendLine("HIDE");
        checkStatus();
    }

    /**
     * Zooms in/out the 3D view to fit every item in the station.
     */
    public void fitAll() {
        checkConnection();
        sendLine("FitAll");
        checkStatus();
    }

    /**
     * Lets the user pick an item from the station tree (or the 3D view), blocking until they do.
     *
     * @param message message shown to the user
     * @param itemType restricts the pickable items to a given type, or {@link ItemType#ANY}
     */
    public Item itemUserPick(String message, ItemType itemType) {
        checkConnection();
        sendLine("PickItem");
        sendLine(message);
        sendInt(itemType == null ? ItemType.ANY.getValue() : itemType.getValue());
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Item item;
        try {
            item = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return item;
    }

    /** @see #itemUserPick(String, ItemType) */
    public Item itemUserPick(String message) {
        return itemUserPick(message, ItemType.ANY);
    }

    /** @see #itemUserPick(String, ItemType) */
    public Item itemUserPick() {
        return itemUserPick("Pick one item", ItemType.ANY);
    }

    // ------------------------------------------------------------------------------------
    // Selection
    // ------------------------------------------------------------------------------------

    /** Returns the items currently selected in the station tree / 3D view. */
    public List<Item> getSelectedItems() {
        checkConnection();
        sendLine("G_Selection");
        int itemCount = recvInt();
        List<Item> items = new ArrayList<>(itemCount);
        for (int i = 0; i < itemCount; i++) {
            items.add(recvItem());
        }
        checkStatus();
        return items;
    }

    /** Sets the items currently selected in the station tree / 3D view. */
    public void setSelectedItems(List<Item> items) {
        checkConnection();
        sendLine("S_Selection");
        sendInt(items.size());
        for (Item item : items) {
            sendItem(item);
        }
        checkStatus();
    }

    // ------------------------------------------------------------------------------------
    // Collisions
    // ------------------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code objectInside} lies inside the geometry of {@code
     * objectParent}.
     */
    public boolean isInside(Item objectInside, Item objectParent) {
        checkConnection();
        sendLine("IsInside");
        sendItem(objectInside);
        sendItem(objectParent);
        int inside = recvInt();
        checkStatus();
        return inside > 0;
    }

    /**
     * Enables or disables collision checking for every item pair, returning the number of
     * pairs currently in collision.
     */
    public int setCollisionActive(boolean active) {
        checkConnection();
        sendLine("Collision_SetState");
        sendInt(active ? 1 : 0);
        int collisionCount = recvInt();
        checkStatus();
        return collisionCount;
    }

    /** Enables collision checking between every pair of items in the station. */
    public void enableCollisionCheckingForAllItems() {
        command("CollisionMap", "All");
    }

    /** Disables collision checking between every pair of items in the station. */
    public void disableCollisionCheckingForAllItems() {
        command("CollisionMap", "None");
    }

    /**
     * Returns the number of pairs of objects that are currently in a collision state.
     */
    public int collisions() {
        checkConnection();
        sendLine("Collisions");
        int collisionCount = recvInt();
        checkStatus();
        return collisionCount;
    }

    /**
     * Returns {@code true} if the two items are currently in a collision state.
     */
    public boolean collision(Item item1, Item item2, boolean useCollisionMap) {
        checkConnection();
        sendLine("Collided3");
        sendItem(item1);
        sendItem(item2);
        sendInt(useCollisionMap ? 1 : 0);
        int collisionCount = recvInt();
        checkStatus();
        return collisionCount > 0;
    }

    /** @see #collision(Item, Item, boolean) */
    public boolean collision(Item item1, Item item2) {
        return collision(item1, item2, true);
    }

    // ------------------------------------------------------------------------------------
    // Simulation / run mode
    // ------------------------------------------------------------------------------------

    /**
     * Sets the simulation playback speed. A speed of 1 means real time; the default (5) means 1
     * second of simulated time takes 1/5th of a second in real time.
     */
    public void setSimulationSpeed(double speed) {
        checkConnection();
        sendLine("SimulateSpeed");
        sendInt((int) (speed * 1000.0));
        checkStatus();
    }

    /** @see #setSimulationSpeed(double) */
    public double getSimulationSpeed() {
        checkConnection();
        sendLine("GetSimulateSpeed");
        double speed = recvInt() / 1000.0;
        checkStatus();
        return speed;
    }

    /**
     * Sets the run mode: simulate movements, validate them quickly, generate a robot program, or
     * run on the physical robot.
     */
    public void setRunMode(RunMode runMode) {
        checkConnection();
        sendLine("S_RunMode");
        sendInt(runMode.getValue());
        checkStatus();
    }

    /** @see #setRunMode(RunMode) */
    public RunMode getRunMode() {
        checkConnection();
        sendLine("G_RunMode");
        RunMode runMode = RunMode.fromValue(recvInt());
        checkStatus();
        return runMode;
    }

    // ------------------------------------------------------------------------------------
    // Station parameters
    // ------------------------------------------------------------------------------------

    /** Returns every user parameter defined in the open station. */
    public List<Map.Entry<String, String>> getParameterList() {
        checkConnection();
        sendLine("G_Params");
        int paramCount = recvInt();
        List<Map.Entry<String, String>> params = new ArrayList<>(paramCount);
        for (int i = 0; i < paramCount; i++) {
            String name = recvLine();
            String value = recvLine();
            params.add(new AbstractMap.SimpleEntry<>(name, value));
        }
        checkStatus();
        return params;
    }

    /**
     * Returns the value of a station parameter, or {@code null} if it is not defined.
     */
    public String getParameter(String parameter) {
        checkConnection();
        sendLine("G_Param");
        sendLine(parameter);
        String value = recvLine();
        checkStatus();
        return value.startsWith("UNKNOWN ") ? null : value;
    }

    /** Sets (or creates) a station parameter. */
    public void setParameter(String parameter, String value) {
        checkConnection();
        sendLine("S_Param");
        sendLine(parameter);
        sendLine(value);
        checkStatus();
    }

    /** @see #setParameter(String, String) */
    public void setParameter(String parameter, double value) {
        setParameter(parameter, toInvariantString(value));
    }

    /**
     * Sends a generic, low level command to RoboDK. Available commands are listed under
     * <b>Tools &gt; Run Script &gt; Show Commands</b> in the RoboDK GUI.
     */
    public String command(String cmd, String value) {
        checkConnection();
        sendLine("SCMD");
        sendLine(cmd);
        sendLine(value);
        String response = recvLine();
        checkStatus();
        return response;
    }

    /** @see #command(String, String) */
    public String command(String cmd) {
        return command(cmd, "");
    }

    /** @see #command(String, String) */
    public String command(String cmd, boolean value) {
        return command(cmd, value ? "1" : "0");
    }

    /** @see #command(String, String) */
    public String command(String cmd, int value) {
        return command(cmd, Integer.toString(value));
    }

    /** @see #command(String, String) */
    public String command(String cmd, double value) {
        return command(cmd, toInvariantString(value));
    }

    // ------------------------------------------------------------------------------------
    // Program execution
    // ------------------------------------------------------------------------------------

    /** Runs a program (or calls a function) by name; equivalent to {@code runCode(function, true)}. */
    public int runProgram(String function) {
        return runCode(function, true);
    }

    /**
     * Adds a program call, code, or comment to the station's main program.
     *
     * @param code the program name (if {@code codeIsFunctionCall}) or raw code/text to insert
     * @param codeIsFunctionCall if {@code true}, {@code code} is interpreted as a function/program call
     * @return the number of instructions that could be successfully added/run
     */
    public int runCode(String code, boolean codeIsFunctionCall) {
        checkConnection();
        sendLine("RunCode");
        sendInt(codeIsFunctionCall ? 1 : 0);
        sendLine(code);
        int status = recvInt();
        checkStatus();
        return status;
    }

    /**
     * Shows a message or a comment in the program generated offline (and, optionally, in the
     * simulator).
     */
    public void runMessage(String message, boolean messageIsComment) {
        checkConnection();
        sendLine("RunMessage");
        sendInt(messageIsComment ? 1 : 0);
        sendLine(message);
        checkStatus();
    }

    // ------------------------------------------------------------------------------------
    // Misc
    // ------------------------------------------------------------------------------------

    /** Returns the RoboDK license string. */
    public String getLicense() {
        checkConnection();
        sendLine("G_License2");
        String license = recvLine();
        recvLine(); // Customer id, currently unused.
        checkStatus();
        return license;
    }

    /** Sets the pose (position and orientation) of the station's camera/view. */
    public void setViewPose(Mat pose) {
        checkConnection();
        sendLine("S_ViewPose");
        sendPose(pose);
        checkStatus();
    }

    /**
     * Returns the pose (position and orientation) of the station's active camera/view.
     * <p>
     * This uses the plain {@code G_ViewPose} command (matching the Python reference API) rather
     * than the C#-only {@code G_ViewPose2} variant, which additionally takes a {@code
     * ViewPoseType} preset selector whose numeric values are not available in any reference
     * source; this command returns the same information without needing it.
     */
    public Mat getViewPose() {
        checkConnection();
        sendLine("G_ViewPose");
        Mat pose = recvPose();
        checkStatus();
        return pose;
    }

    /** Returns the current simulation time, in seconds. */
    public double getSimulationTime() {
        checkConnection();
        sendLine("GetSimTime");
        double time = recvInt() / 1000.0;
        checkStatus();
        return time;
    }

    // ------------------------------------------------------------------------------------
    // UI: window/item flags, window state
    // ------------------------------------------------------------------------------------

    /** Sets the state of the RoboDK main window; see {@link WindowState}. */
    public void setWindowState(WindowState windowState) {
        checkConnection();
        sendLine("S_WindowState");
        sendInt(windowState.getValue());
        checkStatus();
    }

    /** @see #setWindowState(WindowState) */
    public void setWindowState() {
        setWindowState(WindowState.NORMAL);
    }

    /**
     * Updates the RoboDK window flags, controlling how much access the user has to RoboDK's UI.
     * Combine {@link WindowFlags} constants with bitwise OR.
     */
    public void setWindowFlags(int flags) {
        checkConnection();
        sendLine("S_RoboDK_Rights");
        sendInt(flags);
        checkStatus();
    }

    /**
     * Updates an item's flags, controlling how much access the user has to that item's
     * tree/UI features. Combine {@link ItemFlags} constants with bitwise OR.
     */
    public void setItemFlags(Item item, int flags) {
        checkConnection();
        sendLine("S_Item_Rights");
        sendItem(item);
        sendInt(flags);
        checkStatus();
    }

    /** @see #setItemFlags(Item, int) */
    public void setItemFlags(Item item) {
        setItemFlags(item, ItemFlags.ALL);
    }

    /** Returns an item's current flags; see {@link ItemFlags}. */
    public int getItemFlags(Item item) {
        checkConnection();
        sendLine("G_Item_Rights");
        sendItem(item);
        int flags = recvInt();
        checkStatus();
        return flags;
    }

    // ------------------------------------------------------------------------------------
    // UI: interactive mode, cursor, embedded windows, user selection
    // ------------------------------------------------------------------------------------

    /**
     * Sets the interactive mode (behavior of the 3D mouse) used when navigating/selecting items
     * in the 3D view.
     *
     * @param modeType the action performed when the 3D view is interacted with
     * @param defaultRefFlags default allowed movement, as a bitwise OR of {@link DisplayRefType} constants
     * @param customItems items to customize the behavior for, or {@code null}
     * @param customRefFlags matching per-item {@link DisplayRefType} flags (same length as {@code customItems}), or {@code null}
     */
    public void setInteractiveMode(InteractiveMode modeType, int defaultRefFlags, List<Item> customItems,
                                    List<Integer> customRefFlags) {
        checkConnection();
        sendLine("S_InteractiveMode");
        sendInt(modeType.getValue());
        sendInt(defaultRefFlags);
        if (customItems == null || customRefFlags == null) {
            sendInt(-1);
        } else {
            int count = Math.min(customItems.size(), customRefFlags.size());
            sendInt(count);
            for (int i = 0; i < count; i++) {
                sendItem(customItems.get(i));
                sendInt(customRefFlags.get(i));
            }
        }
        checkStatus();
    }

    /** @see #setInteractiveMode(InteractiveMode, int, List, List) */
    public void setInteractiveMode(InteractiveMode modeType) {
        setInteractiveMode(modeType, DisplayRefType.DEFAULT, null, null);
    }

    /**
     * Returns the item under the given screen coordinates (or under the mouse cursor if not
     * provided), along with the station-relative XYZ point.
     */
    public CursorXyzResult getCursorXYZ(int xCoord, int yCoord) {
        checkConnection();
        sendLine("Proj2d3d");
        sendInt(xCoord);
        sendInt(yCoord);
        recvInt(); // Selection flag (unused).
        Item item = recvItem();
        double[] xyz = recvXyz();
        checkStatus();
        return new CursorXyzResult(item, xyz);
    }

    /** @see #getCursorXYZ(int, int) */
    public CursorXyzResult getCursorXYZ() {
        return getCursorXYZ(-1, -1);
    }

    /**
     * Embeds an external application window (identified by its window title) into the RoboDK
     * main window, as a docked panel.
     */
    public boolean embedWindow(String windowName, String dockedName, int width, int height, int pid,
                                int areaAdd, int areaAllowed, int timeoutMilliseconds) {
        checkConnection();
        sendLine("WinProcDock");
        sendLine(dockedName != null ? dockedName : windowName);
        sendLine(windowName);
        sendArray(new double[] {width, height});
        sendLine(Integer.toString(pid));
        sendInt(areaAdd);
        sendInt(areaAllowed);
        sendInt(timeoutMilliseconds);
        int result = recvInt();
        checkStatus();
        return result > 0;
    }

    /** @see #embedWindow(String, String, int, int, int, int, int, int) */
    public boolean embedWindow(String windowName) {
        return embedWindow(windowName, null, -1, -1, 0, 1, 15, 500);
    }

    /**
     * Retrieves the object feature (surface, curve, point, or mesh) currently under the mouse
     * cursor, or the last item the user hovered/selected, depending on {@code featureType}.
     */
    public GetPointsResult getPoints(ObjectSelectionType featureType) {
        checkConnection();
        sendLine("G_ObjPoint");
        sendItem(null);
        sendInt(featureType.getValue());
        sendInt(0); // Feature id filter (unused; always retrieves the current feature).
        Mat points = null;
        if (featureType == ObjectSelectionType.HOVER_OBJECT_MESH) {
            points = recvMatrix();
        }
        Item item = recvItem();
        recvInt(); // IsFrame (unused).
        ObjectSelectionType resultFeatureType = ObjectSelectionType.fromValue(recvInt());
        int featureId = recvInt();
        String name = recvLine();
        checkStatus();
        return new GetPointsResult(item, resultFeatureType, featureId, name, points);
    }

    /** @see #getPoints(ObjectSelectionType) */
    public GetPointsResult getPoints() {
        return getPoints(ObjectSelectionType.HOVER_OBJECT_MESH);
    }

    /**
     * Measures the pose of a calibrated tracking device (for example a laser tracker or a
     * stereo camera) connected as a "measurement" driver, optionally averaged over a period of
     * time and/or offset by a known tip.
     *
     * @param target target number to measure, or -1 for the default/last target
     * @param averageTimeMilliseconds time window to average the measurement over, or 0 for a single reading
     * @param tipOffset a 3-value XYZ offset (mm) applied to the measured point, or {@code null}
     */
    public MeasurePoseResult measurePose(int target, int averageTimeMilliseconds, double[] tipOffset) {
        double[] request = new double[] {target, averageTimeMilliseconds, 0.0, 0.0, 0.0};
        if (tipOffset != null && tipOffset.length >= 3) {
            request[2] = tipOffset[0];
            request[3] = tipOffset[1];
            request[4] = tipOffset[2];
        }
        checkConnection();
        sendLine("MeasPose4");
        sendArray(request);
        Mat pose = recvPose();
        double[] result = recvArray();
        checkStatus();
        return new MeasurePoseResult(pose, result[0], result[1]);
    }

    /** @see #measurePose(int, int, double[]) */
    public MeasurePoseResult measurePose() {
        return measurePose(-1, 0, null);
    }

    // ------------------------------------------------------------------------------------
    // Station tree: merging, ISO cube program, joint targets
    // ------------------------------------------------------------------------------------

    /** Merges several items (for example several curves/objects) into a single new item. */
    public Item mergeItems(List<Item> items) {
        checkConnection();
        sendLine("MergeItems");
        sendInt(items.size());
        for (Item item : items) {
            sendItem(item);
        }
        Item newItem = recvItem();
        checkStatus();
        return newItem;
    }

    /** Pops up the "Create Cube ISO9283" utility dialog and returns the resulting program (invalid until it completes). */
    public Item popupIso9283CubeProgram(Item robot) {
        checkConnection();
        sendLine("Popup_ProgISO9283");
        sendItem(robot);
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(Math.max(3_600_000, previousTimeout));
        Item program;
        try {
            program = recvItem();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return program;
    }

    /** @see #popupIso9283CubeProgram(Item) */
    public Item popupIso9283CubeProgram() {
        return popupIso9283CubeProgram(null);
    }

    /**
     * Adds a joint target to {@code program} at the given joint values, creating a hidden,
     * joint-based target as an intermediate step.
     */
    public Item addTargetJ(Item program, String targetName, double[] joints, Item robotBase, Item robot) {
        Item target = addTarget(targetName, robotBase, robot);
        if (!target.isValid()) {
            throw new RdkException("Create target '" + targetName + "' failed.");
        }
        target.setVisible(false);
        target.setAsJointTarget();
        target.setJoints(joints);
        if (robot != null) {
            target.setRobot(robot);
        }
        program.addMoveJ(target);
        return target;
    }

    /** @see #addTargetJ(Item, String, double[], Item, Item) */
    public Item addTargetJ(Item program, String targetName, double[] joints) {
        return addTargetJ(program, targetName, joints, null, null);
    }

    // ------------------------------------------------------------------------------------
    // Batch poses, sequence display
    // ------------------------------------------------------------------------------------

    /** Sets the local pose of several items in a single call. */
    public void setPoses(List<Item> items, List<Mat> poses) {
        if (items.size() != poses.size()) {
            throw new RdkException("The number of items must match the number of poses");
        }
        if (items.isEmpty()) {
            return;
        }
        checkConnection();
        sendLine("S_Hlocals");
        sendInt(items.size());
        for (int i = 0; i < items.size(); i++) {
            sendItem(items.get(i));
            sendPose(poses.get(i));
        }
        checkStatus();
    }

    /** Sets the absolute (station-relative) pose of several items in a single call. */
    public void setPosesAbs(List<Item> items, List<Mat> poses) {
        if (items.size() != poses.size()) {
            throw new RdkException("The number of items must match the number of poses");
        }
        if (items.isEmpty()) {
            return;
        }
        checkConnection();
        sendLine("S_Hlocal_AbsS");
        sendInt(items.size());
        for (int i = 0; i < items.size(); i++) {
            sendItem(items.get(i));
            sendPose(poses.get(i));
        }
        checkStatus();
    }

    /** Displays a sequence of poses (for example a path being planned) directly, as a matrix. */
    public void showSequence(Mat sequence) {
        checkConnection();
        sendLine("Show_Seq");
        sendMatrix(sequence);
        sendItem(null);
        checkStatus();
    }

    // ------------------------------------------------------------------------------------
    // Collisions: per-pair configuration
    // ------------------------------------------------------------------------------------

    /** Enables/disables collision checking for a single pair of items (optionally restricted to specific robot links). */
    public boolean setCollisionActivePair(boolean active, CollisionPair pair) {
        checkConnection();
        sendLine("Collision_SetPair");
        sendItem(pair.getItem1());
        sendItem(pair.getItem2());
        sendInt(pair.getRobotLinkId1());
        sendInt(pair.getRobotLinkId2());
        sendInt(active ? 1 : 0);
        int success = recvInt();
        checkStatus();
        return success > 0;
    }

    /** Enables/disables collision checking for several item pairs in a single call. */
    public boolean setCollisionActivePair(List<Boolean> activeStates, List<CollisionPair> pairs) {
        checkConnection();
        sendLine("Collision_SetPairList");
        int count = Math.min(activeStates.size(), pairs.size());
        sendInt(count);
        for (int i = 0; i < count; i++) {
            CollisionPair pair = pairs.get(i);
            sendItem(pair.getItem1());
            sendItem(pair.getItem2());
            sendInt(pair.getRobotLinkId1());
            sendInt(pair.getRobotLinkId2());
            sendInt(activeStates.get(i) ? 1 : 0);
        }
        int ok = recvInt();
        checkStatus();
        return ok == count;
    }

    /** Returns every item currently in a collision state. */
    public List<CollisionItem> getCollisionItems() {
        checkConnection();
        sendLine("Collision_Items");
        int count = recvInt();
        List<CollisionItem> items = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            Item item = recvItem();
            int robotLinkId = recvInt();
            items.add(new CollisionItem(item, robotLinkId));
            recvInt(); // Number of objects this item is in collision with (unused).
        }
        checkStatus();
        return items;
    }

    /** Returns every pair of items currently in a collision state. */
    public List<CollisionPair> getCollisionPairs() {
        checkConnection();
        sendLine("Collision_Pairs");
        int count = recvInt();
        List<CollisionPair> pairs = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            Item item1 = recvItem();
            int id1 = recvInt();
            Item item2 = recvItem();
            int id2 = recvInt();
            pairs.add(new CollisionPair(item1, id1, item2, id2));
        }
        checkStatus();
        return pairs;
    }

    /** Returns every pair of items for which collision checking is currently active. */
    public List<CollisionPair> collisionActivePairList() {
        checkConnection();
        sendLine("Collision_GetPairList");
        int count = recvInt();
        List<CollisionPair> pairs = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            Item item1 = recvItem();
            int id1 = recvInt();
            Item item2 = recvItem();
            int id2 = recvInt();
            pairs.add(new CollisionPair(item1, id1, item2, id2));
        }
        checkStatus();
        return pairs;
    }

    // ------------------------------------------------------------------------------------
    // Camera (2D camera simulation)
    // ------------------------------------------------------------------------------------

    /** Adds a 2D simulated camera looking at (or attached to) {@code item}, returning its handle. */
    public long cam2DAdd(Item item, String cameraParameters) {
        checkConnection();
        sendLine("Cam2D_Add");
        sendItem(item);
        sendLine(cameraParameters == null ? "" : cameraParameters);
        long camHandle = recvPtr();
        checkStatus();
        return camHandle;
    }

    /** @see #cam2DAdd(Item, String) */
    public long cam2DAdd(Item item) {
        return cam2DAdd(item, "");
    }

    /** Saves a snapshot from a simulated camera (by handle) to an image file. */
    public boolean cam2DSnapshot(String fileSaveImg, long camHandle) {
        checkConnection();
        sendLine("Cam2D_Snapshot");
        sendPtr(camHandle);
        sendLine(fileSaveImg);
        int success = recvInt();
        checkStatus();
        return success > 0;
    }

    /** Saves a snapshot from a simulated camera (by item) to an image file. */
    public boolean cam2DSnapshot(String fileSaveImg, Item cam, String cameraParameters) {
        if (fileSaveImg == null || fileSaveImg.isEmpty()) {
            throw new RdkException("Retrieving binary image data is not supported; provide a file path");
        }
        checkConnection();
        sendLine("Cam2D_PtrSnapshot");
        sendItem(cam);
        sendLine(fileSaveImg);
        sendLine(cameraParameters == null ? "" : cameraParameters);
        int success = recvInt();
        checkStatus();
        return success > 0;
    }

    /** Closes a simulated camera (by handle), or every simulated camera if {@code camHandle} is 0. */
    public boolean cam2DClose(long camHandle) {
        checkConnection();
        if (camHandle == 0) {
            sendLine("Cam2D_CloseAll");
        } else {
            sendLine("Cam2D_Close");
            sendPtr(camHandle);
        }
        int success = recvInt();
        checkStatus();
        return success > 0;
    }

    /** @see #cam2DClose(long) */
    public boolean cam2DCloseAll() {
        return cam2DClose(0);
    }

    /** Updates the parameters of a simulated camera. */
    public boolean cam2DSetParameters(String cameraParameters, long camHandle) {
        checkConnection();
        sendLine("Cam2D_SetParams");
        sendPtr(camHandle);
        sendLine(cameraParameters == null ? "" : cameraParameters);
        int success = recvInt();
        checkStatus();
        return success > 0;
    }

    // ------------------------------------------------------------------------------------
    // Plugin hosting
    // ------------------------------------------------------------------------------------

    /**
     * Sends a command to a loaded RoboDK plugin and returns its response. Blocks for up to a week
     * (matching the reference APIs), since a plugin command may itself be a long-running operation.
     */
    public String pluginCommand(String pluginName, String command, String value) {
        checkConnection();
        sendLine("PluginCommand");
        sendLine(pluginName);
        sendLine(command);
        sendLine(value);
        int previousTimeout = socketTimeoutMilliseconds;
        setSocketTimeoutMilliseconds(3_600 * 24 * 7 * 1000);
        String result;
        try {
            result = recvLine();
        } finally {
            setSocketTimeoutMilliseconds(previousTimeout);
        }
        checkStatus();
        return result;
    }

    /** Loads, unloads, or reloads a RoboDK plugin by name. */
    public boolean pluginLoad(String pluginName, PluginOperation operation) {
        switch (operation) {
            case LOAD:
                return "OK".equals(command("PluginLoad", pluginName));
            case RELOAD:
                command("PluginUnload", pluginName);
                return "OK".equals(command("PluginLoad", pluginName));
            case UNLOAD:
            default:
                return "OK".equals(command("PluginUnload", pluginName));
        }
    }

    /** @see #pluginLoad(String, PluginOperation) */
    public boolean pluginLoad(String pluginName) {
        return pluginLoad(pluginName, PluginOperation.LOAD);
    }

    // ------------------------------------------------------------------------------------
    // Spray gun simulation
    // ------------------------------------------------------------------------------------

    /** Adds a new simulated spray gun and returns its handle/id. */
    public int sprayAdd(Item tool, Item referenceObject, String parameters, Mat points, Mat geometry) {
        checkConnection();
        sendLine("Gun_Add");
        sendItem(tool);
        sendItem(referenceObject);
        sendLine(parameters == null ? "" : parameters);
        sendMatrix(points != null ? points : new Mat(0, 0));
        sendMatrix(geometry != null ? geometry : new Mat(0, 0));
        int sprayId = recvInt();
        checkStatus();
        return sprayId;
    }

    /** @see #sprayAdd(Item, Item, String, Mat, Mat) */
    public int sprayAdd() {
        return sprayAdd(null, null, "", null, null);
    }

    /** Stops simulating a spray gun (or every spray gun, if {@code sprayId} is -1), clearing its particles. */
    public int sprayClear(int sprayId) {
        checkConnection();
        sendLine("Gun_Clear");
        sendInt(sprayId);
        int result = recvInt();
        checkStatus();
        return result;
    }

    /** @see #sprayClear(int) */
    public int sprayClear() {
        return sprayClear(-1);
    }

    /** Returns statistics from a simulated spray gun (or every spray gun, if {@code sprayId} is -1). */
    public SprayGunStats sprayGetStats(int sprayId) {
        checkConnection();
        sendLine("Gun_Stats");
        sendInt(sprayId);
        String info = recvLine().replace("<br>", "\t");
        Mat data = recvMatrix();
        checkStatus();
        return new SprayGunStats(info, data);
    }

    /** @see #sprayGetStats(int) */
    public SprayGunStats sprayGetStats() {
        return sprayGetStats(-1);
    }

    /** Turns a simulated spray gun (or every spray gun, if {@code sprayId} is -1) on or off. */
    public int spraySetState(boolean on, int sprayId) {
        checkConnection();
        sendLine("Gun_SetState");
        sendInt(sprayId);
        sendInt(on ? 1 : 0);
        int result = recvInt();
        checkStatus();
        return result;
    }

    /** @see #spraySetState(boolean, int) */
    public int spraySetState(boolean on) {
        return spraySetState(on, -1);
    }

    // ------------------------------------------------------------------------------------
    // Wire protocol: status handling
    // ------------------------------------------------------------------------------------

    /**
     * Reads and interprets the status code that RoboDK sends after every API command,
     * throwing an {@link RdkException} if the command failed.
     */
    void checkStatus() {
        int status = recvInt();
        lastStatusMessage = "";
        switch (status) {
            case 0:
                return;
            case 1:
                lastStatusMessage = "Invalid item provided: the item identifier is not valid or it does not exist.";
                throw new RdkException(lastStatusMessage);
            case 2:
                // Warning: the command succeeded but RoboDK reported an issue.
                lastStatusMessage = recvLine();
                return;
            case 9:
                lastStatusMessage = "Invalid license. Contact us at: info@robodk.com";
                throw new RdkException(lastStatusMessage);
            case 3:
            case 10:
            case 11:
            case 12:
                lastStatusMessage = recvLine();
                throw new RdkException(lastStatusMessage);
            default:
                if (status > 0 && status < 100) {
                    lastStatusMessage = recvLine();
                    throw new RdkException(lastStatusMessage);
                }
                lastStatusMessage = "Unknown problem running RoboDK API function";
                throw new RdkException(lastStatusMessage);
        }
    }

    // ------------------------------------------------------------------------------------
    // Wire protocol: low level send/receive primitives
    // ------------------------------------------------------------------------------------

    /** Sends a line of text, terminated with a single {@code \n} (embedded newlines are stripped). */
    void sendLine(String line) {
        String sanitized = line.replace('\n', ' ');
        writeBytes((sanitized + "\n").getBytes(StandardCharsets.UTF_8));
    }

    /** Reads a line of text, terminated by {@code \n} (the terminator is not included). */
    String recvLine() {
        StringBuilder builder = new StringBuilder();
        int character = readByte();
        while (character != '\n') {
            builder.append((char) character);
            character = readByte();
        }
        return builder.toString();
    }

    /** Sends a 32-bit signed integer, big-endian. */
    void sendInt(int value) {
        ByteBuffer buffer = ByteBuffer.allocate(Integer.BYTES).order(ByteOrder.BIG_ENDIAN);
        buffer.putInt(value);
        writeBytes(buffer.array());
    }

    /** Reads a 32-bit signed integer, big-endian. */
    int recvInt() {
        byte[] bytes = readBytes(Integer.BYTES);
        return ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN).getInt();
    }

    /** Sends a 64-bit IEEE 754 double, big-endian. */
    void sendDouble(double value) {
        ByteBuffer buffer = ByteBuffer.allocate(Double.BYTES).order(ByteOrder.BIG_ENDIAN);
        buffer.putDouble(value);
        writeBytes(buffer.array());
    }

    /** Reads a 64-bit IEEE 754 double, big-endian. */
    double recvDouble() {
        byte[] bytes = readBytes(Double.BYTES);
        return ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN).getDouble();
    }

    /** Sends an array of doubles, prefixed by its length. A {@code null} array is sent as empty. */
    void sendArray(double[] values) {
        if (values == null) {
            sendInt(0);
            return;
        }
        sendInt(values.length);
        ByteBuffer buffer = ByteBuffer.allocate(values.length * Double.BYTES).order(ByteOrder.BIG_ENDIAN);
        for (double value : values) {
            buffer.putDouble(value);
        }
        writeBytes(buffer.array());
    }

    /** Reads an array of doubles, prefixed by its length. Returns an empty array if the length is 0. */
    double[] recvArray() {
        int count = recvInt();
        double[] values = new double[count];
        if (count > 0) {
            byte[] bytes = readBytes(count * Double.BYTES);
            ByteBuffer buffer = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN);
            for (int i = 0; i < count; i++) {
                values[i] = buffer.getDouble();
            }
        }
        return values;
    }

    /** Sends a 64-bit handle/pointer value (e.g. a camera handle), with no length prefix. */
    void sendPtr(long value) {
        ByteBuffer buffer = ByteBuffer.allocate(Long.BYTES).order(ByteOrder.BIG_ENDIAN);
        buffer.putLong(value);
        writeBytes(buffer.array());
    }

    /** Reads a 64-bit handle/pointer value (e.g. a camera handle), with no length prefix. */
    long recvPtr() {
        byte[] bytes = readBytes(Long.BYTES);
        return ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN).getLong();
    }

    /** Sends exactly 3 raw doubles (an XYZ point), with no length prefix. */
    void sendXyz(double[] xyz) {
        ByteBuffer buffer = ByteBuffer.allocate(3 * Double.BYTES).order(ByteOrder.BIG_ENDIAN);
        for (int i = 0; i < 3; i++) {
            buffer.putDouble(xyz != null && i < xyz.length ? xyz[i] : 0.0);
        }
        writeBytes(buffer.array());
    }

    /** Reads exactly 3 raw doubles (an XYZ point), with no length prefix. */
    double[] recvXyz() {
        byte[] bytes = readBytes(3 * Double.BYTES);
        ByteBuffer buffer = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN);
        double[] xyz = new double[3];
        for (int i = 0; i < 3; i++) {
            xyz[i] = buffer.getDouble();
        }
        return xyz;
    }

    /** Sends a 2-dimensional matrix (rows, then columns, then column-major doubles). */
    void sendMatrix(Mat mat) {
        sendInt(mat.rows());
        sendInt(mat.cols());
        ByteBuffer buffer = ByteBuffer.allocate(mat.rows() * mat.cols() * Double.BYTES).order(ByteOrder.BIG_ENDIAN);
        for (int col = 0; col < mat.cols(); col++) {
            for (int row = 0; row < mat.rows(); row++) {
                buffer.putDouble(mat.get(row, col));
            }
        }
        writeBytes(buffer.array());
    }

    /** Reads a 2-dimensional matrix (rows, then columns, then column-major doubles). */
    Mat recvMatrix() {
        int rows = recvInt();
        int cols = recvInt();
        Mat mat = new Mat(rows, cols);
        int byteCount = rows * cols * Double.BYTES;
        if (byteCount > 0) {
            ByteBuffer buffer = ByteBuffer.wrap(readBytes(byteCount)).order(ByteOrder.BIG_ENDIAN);
            for (int col = 0; col < cols; col++) {
                for (int row = 0; row < rows; row++) {
                    mat.set(row, col, buffer.getDouble());
                }
            }
        }
        return mat;
    }

    /**
     * Validates that a RoboDK color array has exactly 4 components (red, green, blue, alpha, each
     * in the 0-1 range), as required by every color-related API call.
     */
    /** Formats a double using an invariant, dot-decimal representation (never locale-dependent). */
    static String toInvariantString(double value) {
        return String.format(Locale.ROOT, "%s", value);
    }

    static void checkColor(double[] color) {
        if (color == null || color.length != 4) {
            throw new RdkException("Invalid color. A color must be a 4-size double array [r, g, b, a]");
        }
    }

    /** Sends a byte array, prefixed by its length. */
    void sendBytes(byte[] data) {
        sendInt(data.length);
        writeBytes(data);
    }

    /** Reads a byte array, prefixed by its length. */
    byte[] recvBytes() {
        int length = recvInt();
        return readBytes(length);
    }

    /**
     * Sends a 4x4 pose (column by column), as required by RoboDK.
     *
     * @throws RdkException if the pose is not a valid homogeneous transform
     */
    void sendPose(Mat pose) {
        if (!pose.isHomogeneous()) {
            throw new RdkException("Matrix not homogeneous, cannot be sent as a pose");
        }
        ByteBuffer buffer = ByteBuffer.allocate(16 * Double.BYTES).order(ByteOrder.BIG_ENDIAN);
        for (int col = 0; col < 4; col++) {
            for (int row = 0; row < 4; row++) {
                buffer.putDouble(pose.get(row, col));
            }
        }
        writeBytes(buffer.array());
    }

    /** Reads a 4x4 pose (column by column), as sent by RoboDK. */
    Mat recvPose() {
        byte[] bytes = readBytes(16 * Double.BYTES);
        ByteBuffer buffer = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN);
        Mat pose = new Mat();
        for (int col = 0; col < 4; col++) {
            for (int row = 0; row < 4; row++) {
                pose.set(row, col, buffer.getDouble());
            }
        }
        return pose;
    }

    /** Sends a reference to an item (its internal 64-bit identifier). A {@code null} item is sent as 0. */
    void sendItem(Item item) {
        long itemId = item == null ? 0L : item.getItemId();
        ByteBuffer buffer = ByteBuffer.allocate(Long.BYTES).order(ByteOrder.BIG_ENDIAN);
        buffer.putLong(itemId);
        writeBytes(buffer.array());
    }

    /** Reads a reference to an item: its 64-bit identifier followed by its 32-bit item type. */
    Item recvItem() {
        byte[] idBytes = readBytes(Long.BYTES);
        byte[] typeBytes = readBytes(Integer.BYTES);
        long itemId = ByteBuffer.wrap(idBytes).order(ByteOrder.BIG_ENDIAN).getLong();
        int typeValue = ByteBuffer.wrap(typeBytes).order(ByteOrder.BIG_ENDIAN).getInt();
        return new Item(this, itemId, ItemType.fromValue(typeValue));
    }

    // ------------------------------------------------------------------------------------
    // Socket helpers
    // ------------------------------------------------------------------------------------

    private void writeBytes(byte[] data) {
        try {
            output.write(data);
            output.flush();
        } catch (IOException | NullPointerException e) {
            throw new RdkException("Failed to send data to RoboDK", e);
        }
    }

    private int readByte() {
        try {
            int value = input.read();
            if (value < 0) {
                throw new RdkException("Connection to RoboDK closed unexpectedly");
            }
            return value;
        } catch (IOException | NullPointerException e) {
            throw new RdkException("Failed to read data from RoboDK", e);
        }
    }

    private byte[] readBytes(int length) {
        byte[] buffer = new byte[length];
        try {
            new DataInputStream(input).readFully(buffer);
        } catch (IOException | NullPointerException e) {
            throw new RdkException("Failed to read data from RoboDK", e);
        }
        return buffer;
    }
}
