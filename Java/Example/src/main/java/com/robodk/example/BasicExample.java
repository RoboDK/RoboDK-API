package com.robodk.example;

import com.robodk.api.Item;
import com.robodk.api.ItemType;
import com.robodk.api.Mat;
import com.robodk.api.RoboDK;
import com.robodk.api.exception.RdkException;

import java.util.Arrays;
import java.util.List;

/**
 * Small runnable demonstration of the RoboDK API for Java (the {@code API} module).
 * <p>
 * This is a plain {@code main} method rather than a test: it opens a real TCP connection to a
 * running RoboDK station, so it is meant to be run (and stepped through in a debugger) with
 * RoboDK open on the same machine, not executed as part of a build.
 * <p>
 * The example assumes an <b>empty station</b>: rather than looking for a robot that may not be
 * there, it builds a small scene from scratch (a reference frame, a couple of geometry
 * primitives, and a target), the same way a first-time user of the API would.
 * <p>
 * To run it:
 * <ol>
 *     <li>Start RoboDK, with an empty station open (File &gt; New Station).</li>
 *     <li>Run this class's {@code main} method (from IntelliJ IDEA, or with
 *         {@code mvn -pl Example -am exec:java}).</li>
 * </ol>
 */
public final class BasicExample {

    private BasicExample() {
    }

    public static void main(String[] args) {
        try (RoboDK robodk = new RoboDK()) {
            if (!robodk.connect()) {
                System.err.println("Could not connect to RoboDK. Is it running?");
                return;
            }

            System.out.println("Connected to RoboDK " + robodk.version()
                    + " (API version " + robodk.getApiVersion() + ", build " + robodk.getRoboDKBuild() + ")");

            // Turn off screen refresh while we build the scene: faster, and avoids flicker.
            robodk.render(false);

            // ------------------------------------------------------------------------------
            // Reference frames: a reference frame is the closest thing to a "folder" that the
            // RoboDK API can create (there is no dedicated AddFolder call in the wire protocol
            // used by the reference C# and Python APIs either) - it also happens to be genuinely
            // useful, since every item added under it inherits its pose.
            // ------------------------------------------------------------------------------
            Item cellFrame = robodk.addFrame("Demo Cell");
            cellFrame.setPose(Mat.transl(0, 0, 0));
            System.out.println("Added reference frame: " + cellFrame.getName());

            Item tableFrame = robodk.addFrame("Table", cellFrame);
            tableFrame.setPose(Mat.transl(0, 0, 0));
            System.out.println("Added child reference frame: " + tableFrame.getName()
                    + " (parent: " + tableFrame.getParent().getName() + ")");

            // ------------------------------------------------------------------------------
            // Geometry primitives: RoboDK objects are made of triangles, so "primitives" like a
            // box are built by triangulating their faces and adding them with addShape().
            // ------------------------------------------------------------------------------
            Item box = robodk.addShape(makeBox(300, 200, 50), null, false, new double[] {0.7, 0.7, 0.75, 1.0});
            box.setParent(tableFrame);
            box.setName("Table Top (300x200x50)");
            box.setPose(Mat.transl(0, 0, 25)); // Sit the box on top of the frame's origin.
            System.out.println("Added box: " + box.getName());

            Item pedestal = robodk.addShape(makeBox(80, 80, 400), null, false, new double[] {0.5, 0.5, 0.55, 1.0});
            pedestal.setParent(tableFrame);
            pedestal.setName("Pedestal (80x80x400)");
            pedestal.setPose(Mat.transl(0, 0, -200));
            System.out.println("Added box: " + pedestal.getName());

            // A reference target, 250 mm above the table, that a robot program could move to.
            Item target = robodk.addTarget("Approach", cellFrame);
            target.setPose(Mat.transl(0, 0, 250));
            System.out.println("Added target: " + target.getName());

            robodk.render(true);
            robodk.fitAll();

            // ------------------------------------------------------------------------------
            // If a robot happens to be in the station, show a few robot-level API calls too.
            // ------------------------------------------------------------------------------
            List<String> robotNames = robodk.getItemListNames(ItemType.ROBOT);
            if (robotNames.isEmpty()) {
                System.out.println("No robot in the station: add one (File > Add > ...) to see the "
                        + "robot-level calls (getJoints/getPose/solveFK) in action.");
                return;
            }

            Item robot = robodk.getItemByName(robotNames.get(0), ItemType.ROBOT);
            System.out.println("Found robot: " + robot.getName());
            System.out.println("Current joints: " + Arrays.toString(robot.getJoints()));
            System.out.println("Current pose:\n" + robot.getPose());

            // A quick tour of Mat and forward kinematics: build a pose 100 mm above the robot's
            // current pose, rotated 90 degrees around Z, and print it out (this does not move
            // the robot; MoveJ/MoveL are also available on Item if you want to actually move it).
            Mat currentPose = robot.getPose();
            Mat offsetPose = Mat.offset(currentPose, 0, 0, 100, 0, 0, 90);
            System.out.println("Offset pose (100 mm up, 90 deg around Z):\n" + offsetPose);
            System.out.println("Forward kinematics of the current joints, recomputed:\n"
                    + robot.solveFK(robot.getJoints()));

        } catch (RdkException e) {
            System.err.println("RoboDK API error: " + e.getMessage());
        }
    }

    /**
     * Builds the 12 triangles (2 per face x 6 faces) of an axis-aligned box centered at the
     * origin, as a 3xN matrix of vertices suitable for {@link RoboDK#addShape(Mat, Item, boolean, double[])}.
     *
     * @param sizeX box size along X, in mm
     * @param sizeY box size along Y, in mm
     * @param sizeZ box size along Z, in mm
     */
    private static Mat makeBox(double sizeX, double sizeY, double sizeZ) {
        double x = sizeX / 2;
        double y = sizeY / 2;
        double z = sizeZ / 2;

        // The 8 corners of the box.
        double[][] corners = {
                {-x, -y, -z}, {x, -y, -z}, {x, y, -z}, {-x, y, -z}, // bottom face (z = -z)
                {-x, -y, z}, {x, -y, z}, {x, y, z}, {-x, y, z},     // top face (z = +z)
        };

        // Each face as 2 triangles, referencing corner indices (outward-facing winding order).
        int[][] faces = {
                {0, 1, 2}, {0, 2, 3}, // bottom
                {4, 6, 5}, {4, 7, 6}, // top
                {0, 5, 1}, {0, 4, 5}, // front (y = -y)
                {1, 6, 2}, {1, 5, 6}, // right (x = +x)
                {2, 7, 3}, {2, 6, 7}, // back (y = +y)
                {3, 4, 0}, {3, 7, 4}, // left (x = -x)
        };

        double[][] vertices = new double[faces.length * 3][3];
        int row = 0;
        for (int[] face : faces) {
            for (int cornerIndex : face) {
                vertices[row++] = corners[cornerIndex];
            }
        }
        return new Mat(vertices);
    }
}
