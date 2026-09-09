package com.robodk.api;

import com.robodk.api.exception.RdkException;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.Closeable;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * Entry point to the RoboDK API.
 * <p>
 * A {@code RoboDK} instance represents a TCP/IP link to a running RoboDK station. Every
 * interaction with the station tree (robots, reference frames, tools, targets, programs, ...)
 * goes through this class, either directly or through an {@link Item} obtained from it.
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

    private final String roboDkServerIp;
    private final int roboDkServerStartPort;
    private final int roboDkServerEndPort;

    private Socket socket;
    private InputStream input;
    private OutputStream output;

    private int socketTimeoutMilliseconds = 10_000;
    private int connectedPort = -1;
    private int apiVersion;
    private int roboDKBuild;
    private String lastStatusMessage = "";

    /** If true, checks that provided items exist in memory and that poses are homogeneous. */
    private boolean safeMode = true;

    /** Delays screen refresh until 100 ms after the last call, for faster scripts. */
    private boolean autoUpdate = false;

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
     * @param roboDkServerIp host name or IP address where RoboDK is running
     * @param roboDkServerPort single TCP port to connect to
     */
    public RoboDK(String roboDkServerIp, int roboDkServerPort) {
        this(roboDkServerIp, roboDkServerPort, roboDkServerPort);
    }

    /**
     * Creates a new link to RoboDK, scanning a range of consecutive ports for a running
     * instance.
     *
     * @param roboDkServerIp host name or IP address where RoboDK is running
     * @param roboDkServerStartPort first port to try
     * @param roboDkServerEndPort last port to try (inclusive)
     */
    public RoboDK(String roboDkServerIp, int roboDkServerStartPort, int roboDkServerEndPort) {
        this.roboDkServerIp = roboDkServerIp;
        this.roboDkServerStartPort = roboDkServerStartPort;
        this.roboDkServerEndPort = roboDkServerEndPort;
    }

    // ------------------------------------------------------------------------------------
    // Connection management
    // ------------------------------------------------------------------------------------

    /**
     * Connects to a RoboDK station, scanning the configured port range for a running instance.
     *
     * @return {@code true} if the connection (including the API handshake) succeeded
     */
    public boolean connect() {
        disconnect();
        for (int port = roboDkServerStartPort; port <= roboDkServerEndPort; port++) {
            if (tryConnect(port) && verifyConnection()) {
                connectedPort = port;
                return true;
            }
            disconnect();
        }
        return false;
    }

    private boolean tryConnect(int port) {
        try {
            Socket newSocket = new Socket();
            newSocket.connect(new InetSocketAddress(roboDkServerIp, port), 1000);
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
            roboDKBuild = recvInt();
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
        return roboDKBuild;
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
