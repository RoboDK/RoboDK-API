# RoboDK API for Java

This is a Maven reactor with two modules:

```
Java/
  pom.xml            Parent POM (packaging = pom): shared build config, lists the two modules
  API/               The RoboDK API library (artifact: com.robodk:robodk-api)
  Example/           A small runnable app demonstrating the library (artifact: com.robodk:robodk-api-example)
```

* **`API`** — the library itself: the socket layer, wire protocol (de)serialization, `Mat`, and
  the `RoboDK`/`Item` API calls. See [`API/README.md`](API/README.md) for details. This is what
  you'd depend on from your own project.
* **`Example`** — a plain `main()` (`com.robodk.example.BasicExample`) that depends on `API`,
  connects to a running RoboDK station, and builds a small scene from scratch (a reference
  frame with a child frame, two box primitives added as triangulated shapes, and a target),
  then exercises a few robot-level calls (joints/pose/forward kinematics) if a robot happens to
  be in the station. It assumes an **empty station**, so it works right after `File > New
  Station`, and exists to give you something runnable/debuggable against a live RoboDK
  instance, since the library itself has no unit tests.

## Building everything

```bash
cd Java
mvn clean install
```

This builds both modules; `Example` picks up `API` from the reactor (no need to `mvn install`
`API` separately first when building from the parent).

Running the example from the command line (RoboDK must already be running):

```bash
mvn -pl Example -am exec:java
```

## Opening and debugging in IntelliJ IDEA

To be able to set a breakpoint in `Example` and step *into* `API` source (not a decompiled
jar), open the **parent** project, not just the `Example` folder:

1. **File > Open...** and select the `Java` folder (the one containing this `pom.xml`, i.e. the
   parent/reactor POM) — not `Java/Example` on its own.
2. IntelliJ will detect the Maven project and prompt to load it; accept, and let it import both
   modules. You can also right-click `pom.xml` in the project tree and choose
   **Add as Maven Project** if it wasn't picked up automatically.
3. Once imported, IntelliJ creates a **module dependency** from `robodk-api-example` to
   `robodk-api` (because both are modules of the same reactor it just imported), not a plain
   jar dependency. That's what makes step-into work: the debugger resolves `API` classes to
   the actual source files under `API/src/main/java`, fully editable and steppable, rather
   than an attached/decompiled sources jar.
4. Open `Example/src/main/java/com/robodk/example/BasicExample.java`, set a breakpoint (for
   example on the `robodk.connect()` line), and either click the green gutter icon next to
   `main` and choose **Debug**, or right-click the file and choose **Debug 'BasicExample.main()'**.
   IntelliJ auto-generates the run configuration; nothing else to configure.
5. From there, **Step Into** (F7) on any `RoboDK`/`Item`/`Mat` call will take you straight into
   the corresponding file under `Java/API/src/main/java/com/robodk/api/...`, where you can set
   further breakpoints, inspect variables, etc.

Make sure RoboDK is running before you start the debug session — `BasicExample` connects to a
live station and will just print an error and return otherwise.

If you ever do open `Example` by itself (without the parent), IntelliJ will resolve `API` as an
ordinary Maven dependency instead of a module: you'd need to `mvn install` `API` first, and
stepping into its code would land you in the attached sources jar (read-only) rather than the
live source tree. Opening the parent `Java` folder avoids all of that.
