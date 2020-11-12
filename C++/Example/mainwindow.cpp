#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "embedexample.h"

#include <QFileDialog>
#include <QWindow>
#include <QtConcurrent/QtConcurrent>

#ifdef WIN32
// this is used to integrate RoboDK window as a child window
#include <windows.h>
#pragma comment(lib,"user32.lib")
#endif

//#include <thread>


#define M_PI 3.14159265358979323846

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{

    robodk_window = NULL;
    ui->setupUi(this);
    ui->widgetRoboDK->hide();
    adjustSize();



    // Start RoboDK API here (RoboDK will start if it is not running)
    ROBOT = NULL;
    RDK = new RoboDK();
    if (!RDK->Connected()){
        qDebug() << "Failed to start RoboDK API!!";
    }

}

MainWindow::~MainWindow() {
    robodk_window_clear();
    RDK->CloseRoboDK();
    delete ui;
    delete RDK;
}

bool MainWindow::Check_RoboDK(){
    if (RDK == NULL){
        statusBar()->showMessage("RoboDK API is not connected");
        return false;
    }
    if (!RDK->Connected()){
        statusBar()->showMessage("RoboDK is not running");
        return false;
    }
    return true;
}

bool MainWindow::Check_Robot(){
    if (!Check_RoboDK()){ return false; }

    if (ROBOT == NULL){
        statusBar()->showMessage("Select a robot first");
        return false;
    }
    if (!ROBOT->Valid()){
        statusBar()->showMessage("Robot item is not valid");
        return false;
    }
    return true;
}

void MainWindow::Select_Robot(){
    if (ROBOT != NULL){
        delete ROBOT;
        ROBOT = NULL;
    }
    ROBOT = new Item(RDK->ItemUserPick("Select a robot", RoboDK::ITEM_TYPE_ROBOT));
    //ROBOT = new Item(RDK->getItem("UR10", RoboDK::ITEM_TYPE_ROBOT));
    if (Check_Robot()){
        statusBar()->showMessage("Robot selected: " + ROBOT->Name());
    }
}

void MainWindow::on_btnLoadFile_clicked() {
    if (!Check_RoboDK()){ return; }

    QStringList files = QFileDialog::getOpenFileNames(this, tr("Open one or more files with RoboDK"));
    foreach (QString file, files){
        qDebug() << "Loading: " << file;
        RDK->AddFile(file);
    }

    if (!Check_Robot()){
        Select_Robot();
    }
}

void MainWindow::on_btnSelectRobot_clicked(){
    Select_Robot();
}


void MainWindow::on_btnGetPosition_clicked(){
    if (!Check_Robot()){ return; }

    QString separator = " , ";
    int decimals = 1;

    // Get robot joints
    tJoints joints(ROBOT->Joints());
    QString joints_str = joints.ToString(separator, decimals);
    ui->txtJoints->setText(joints_str);

    // Get robot pose
    Mat robot_pose(ROBOT->Pose());
    QString pose_str = robot_pose.ToString(separator, decimals);
    ui->txtXYZWPR->setText(pose_str);
}

void MainWindow::on_btnMoveJoints_clicked(){
    if (!Check_Robot()){ return; }

    tJoints joints;

    joints.FromString(ui->txtJoints->text());

    bool blocking = true;

    ROBOT->MoveJ(joints, blocking);

}

void MainWindow::on_btnMovePose_clicked(){
    if (!Check_Robot()){ return; }

    Mat pose;

    pose.FromString(ui->txtXYZWPR->text());

    bool blocking = true;

    ROBOT->MoveJ(pose, blocking);

}

void MainWindow::on_btnProgRun_clicked(){
    if (!Check_Robot()){ return; }

    QString program_name = ui->txtProgName->text();

    RDK->RunProgram(program_name);
}

// Example to run a second instance of the RoboDK api in parallel:
// make sure to include #include <thread>
//std::thread *t1 = new std::thread(blocking_task);
/*
void blocking_task(){
    RoboDK rdk; // important! It will not block the main thread (blocking or non blocking won'T make a difference)

    // show the blocking popup:
    rdk.Popup_ISO9283_CubeProgram();

}
*/

// then, start the thread and let it finish once the user finishes with the popup
void MainWindow::on_btnTestButton_clicked(){

    // example to listen to events
    QtConcurrent::run(this, &MainWindow::EventsLoop);
    //RDK->EventsLoop();


    if (!Check_Robot()){ return; }

    /*
    if (false) {
        //ROBOT->setPose
        Item robot_base = ROBOT->Parent();

        // Create or select a reference frame
        Item ref = RDK->getItem("Ref 1");
        if (!ref.Valid()){
            ref = RDK->AddFrame("Ref 1", &robot_base);
            ref.setPose(Mat::transl(100,200,300));
        }

        // create or load a tool
        Item tcp = RDK->getItem("Tool 1");
        if (!tcp.Valid()){
            tcp = ROBOT->AddTool(Mat::transl(0,0,150)*Mat::rotx(0.5*M_PI), "Tool 1");
        }

        // Set the robot base and tool
        ROBOT->setPoseFrame(ref);
        ROBOT->setPoseTool(tcp);

        Mat TargetPose = ROBOT->Pose();

        RDK->Render();

        Item prog = RDK->AddProgram("AutomaticProg", ROBOT);
        prog.setPoseFrame(ref);
        prog.setPoseTool(tcp);

        //Create a target (or select it)
        for (int i=0; i<=100; i++){
            QString target_name(QString("Target %1").arg(i+1));
            Item target = RDK->getItem(target_name, RoboDK::ITEM_TYPE_TARGET);
            if (!target.Valid()){
                target = RDK->AddTarget(target_name, &ref);
                target.setAsCartesianTarget();
                target.setPose(TargetPose * transl(0,0, 2*i) * rotz((i/100.0)*30.0*M_PI/180.0));
                if (i == 0){
                    prog.MoveJ(target);
                } else {
                    prog.MoveL(target);
                }
            }
        }
    }

    // manage a gripper
    if (false){
        //RDK->getItem("");
        Item gripper = ROBOT->Childs()[0];

        tJoints joints_original = gripper.Joints();

        double pjoints[] = {0};
        tJoints joints_new(pjoints, 1);
        gripper.setJoints(joints_new);

        gripper.MoveJ(joints_original);
    }

    //target.Delete();

    // example to display text in the 3D window
    if (true){
        Item station = RDK->getActiveStation();
        Item text_object = RDK->AddFile("", &station);
        text_object.setPose(transl(200,300,100));
        //text_object.setPoseAbs(transl(200,300,100));
        text_object.setName("Display 3D text");
    }

    // Other useful functions to draw primitives
    //RDK->AddShape()
    //RDK->AddCurve()
    //RDK->AddPoints()


    return;
*/



    //int runmode = RDK->RunMode(); // retrieve the run mode

    //RoboDK *RDK = new RoboDK();
    //Item *ROBOT = new Item(RDK->getItem("Motoman SV3"));

    // Draw a hexagon inside a circle of radius 100.0 mm
    int n_sides = 6;
    float size = 100.0;
    // retrieve the reference frame and the tool frame (TCP)
    Mat pose_frame = ROBOT->PoseFrame();
    Mat pose_tool = ROBOT->PoseTool();
    Mat pose_ref = ROBOT->Pose();

    // Program start
    ROBOT->MoveJ(pose_ref);
    ROBOT->setPoseFrame(pose_frame);  // set the reference frame
    ROBOT->setPoseTool(pose_tool);    // set the tool frame: important for Online Programming
    ROBOT->setSpeed(100);             // Set Speed to 100 mm/s
    ROBOT->setRounding(5);            // set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
    ROBOT->RunInstruction("CallOnStart"); // run a program
    for (int i = 0; i <= n_sides; i++) {
        // calculate angle in degrees:
        double angle = ((double) i / n_sides) * 360.0;

        // create a pose relative to the pose_ref
        Mat pose_i(pose_ref);
        pose_i.rotate(angle,0,0,1.0);
        pose_i.translate(size, 0, 0);
        pose_i.rotate(-angle,0,0,1.0);

        // add a comment (when generating code)
        ROBOT->RunInstruction("Moving to point " + QString::number(i), RoboDK::INSTRUCTION_COMMENT);

        // example to retrieve the pose as Euler angles (X,Y,Z,W,P,R)
        double xyzwpr[6];
        pose_i.ToXYZRPW(xyzwpr);

        ROBOT->MoveL(pose_i);  // move the robot
    }
    ROBOT->RunInstruction("CallOnFinish");
    ROBOT->MoveL(pose_ref);     // move back to the reference point

    return;


    // Example to iterate through all the existing targets in the station (blocking):
    QList<Item> targets = RDK->getItemList(RoboDK::ITEM_TYPE_TARGET);
    foreach (Item target, targets){
        if (target.Type() == RoboDK::ITEM_TYPE_TARGET){
            ui->statusBar->showMessage("Moving to: " + target.Name());
            qApp->processEvents();
            ROBOT->MoveJ(target);
        }
    }
    return;

    QList<Item> list = RDK->getItemList();


    Mat pose_robot_base_abs = ROBOT->PoseAbs();
    Mat pose_robot = ROBOT->Pose();
    Mat pose_tcp = ROBOT->PoseTool();

    qDebug() << "Absolute Position of the robot:";
    qDebug() << pose_robot_base_abs;

    qDebug() << "Current robot position (active tool with respect to the active reference):";
    qDebug() << pose_robot;

    qDebug() << "Position of the active TCP:";
    qDebug() << pose_tcp;

    QList<Item> tool_list = ROBOT->Childs();
    if (tool_list.length() <= 0){
        statusBar()->showMessage("No tools available for the robot " + ROBOT->Name());
        return;
    }

    Item tool = tool_list.at(0);
    qDebug() << "Using tool: " << tool.Name();

    Mat pose_robot_flange_abs = tool.PoseAbs();
    pose_tcp = tool.PoseTool();
    Mat pose_tcp_abs = pose_robot_flange_abs * pose_tcp;


    Item object = RDK->getItem("", RoboDK::ITEM_TYPE_FRAME);
    Mat pose_object_abs = object.PoseAbs();
    qDebug() << pose_tcp;

    Mat tcp_wrt_obj = pose_object_abs.inverted() * pose_tcp_abs;

    qDebug() << "Pose of the TCP with respect to the selected reference frame";
    qDebug() << tcp_wrt_obj;

    tXYZWPR xyzwpr;
    tcp_wrt_obj.ToXYZRPW(xyzwpr);

    this->statusBar()->showMessage(QString("Tool with respect to %1").arg(object.Name()) + QString(": [X,Y,Z,W,P,R]=[%1, %2, %3, %4, %5, %6] mm/deg").arg(xyzwpr[0],0,'f',3).arg(xyzwpr[1],0,'f',3).arg(xyzwpr[2],0,'f',3).arg(xyzwpr[3],0,'f',3).arg(xyzwpr[4],0,'f',3).arg(xyzwpr[5],0,'f',3) );


    // Example to define a reference frame given 3 points:
    tMatrix2D* framePts = Matrix2D_Create();
    Matrix2D_Set_Size(framePts, 3, 3);
    double *p1 = Matrix2D_Get_col(framePts, 0);
    double *p2 = Matrix2D_Get_col(framePts, 1);
    double *p3 = Matrix2D_Get_col(framePts, 2);

    // Define point 1:
    p1[0] = 100;
    p1[1] = 200;
    p1[2] = 300;

    // Define point 2:
    p2[0] = 500;
    p2[1] = 200;
    p2[2] = 300;

    // Define point 3:
    p3[0] = 100;
    p3[1] = 500;
    p3[2] = 300;
    Mat diagLocalFrame = RDK->CalibrateReference(framePts, RoboDK::CALIBRATE_FRAME_3P_P1_ON_X);
    Item localPlaneFrame = RDK->AddFrame("Plane Coord");
    localPlaneFrame.setPose(diagLocalFrame);
    Matrix2D_Delete(&framePts);
    return;




    // Inverse kinematics test:
    //Mat tool_pose = transl(10,20,30);
    //Mat ref_pose = transl(100, 100,500);

    qDebug() << "Testing pose:";
    qDebug() << "Using robot: " << ROBOT;
    Mat pose_test(0.733722985, 0.0145948902, -0.679291904, -814.060547, 0.000000000, -0.999769211, -0.0214804877, -8.96536446, -0.679448724, 0.0157607272, -0.733553648, 340.561951);
    ROBOT->setAccuracyActive(1);
    pose_test.MakeHomogeneous();
    qDebug() << pose_test;

    // Calculate a single solution (closest to the current robot position):
    tJoints joints = ROBOT->SolveIK(pose_test); //, &tool_pose, &ref_pose);
    qDebug() << "Solution : " << joints;

    // Iterate through all possible solutions
    // Calculate all nominal solutions:
    ROBOT->setAccuracyActive(0);
    auto all_solutions = ROBOT->SolveIK_All(pose_test); //, &tool_pose, &ref_pose);
    // Use accurate kinematics and calculate inverse kinematics using the closest point
    ROBOT->setAccuracyActive(1);
    for (int i=0; i<all_solutions.length(); i++){
        tJoints joints_nominal_i = all_solutions.at(i);
        qDebug() << "Nominal  solution " << i << ": " << joints_nominal_i;
        tJoints joints_accurate_i = ROBOT->SolveIK(pose_test, joints_nominal_i); //, &tool_pose, &ref_pose);
        qDebug() << "Accurate solution " << i << ": " << joints_accurate_i;
    }




    /*qDebug() << joints.ToString();
    tJoints joints = ROBOT->SolveIK(pose_problems);
    qDebug() << joints.ToString();
    */
    return;


    /*
    // Example to create the ISO cube program
        tXYZ xyz;
        xyz[0] = 100;
        xyz[1] = 200;
        xyz[2] = 300;
        RDK->Popup_ISO9283_CubeProgram(ROBOT, xyz, 100, false);
        return;
    */

}

void MainWindow::on_btnTXn_clicked(){ IncrementalMove(0, -1); }
void MainWindow::on_btnTYn_clicked(){ IncrementalMove(1, -1); }
void MainWindow::on_btnTZn_clicked(){ IncrementalMove(2, -1); }
void MainWindow::on_btnRXn_clicked(){ IncrementalMove(3, -1); }
void MainWindow::on_btnRYn_clicked(){ IncrementalMove(4, -1); }
void MainWindow::on_btnRZn_clicked(){ IncrementalMove(5, -1); }

void MainWindow::on_btnTXp_clicked(){ IncrementalMove(0, +1); }
void MainWindow::on_btnTYp_clicked(){ IncrementalMove(1, +1); }
void MainWindow::on_btnTZp_clicked(){ IncrementalMove(2, +1); }
void MainWindow::on_btnRXp_clicked(){ IncrementalMove(3, +1); }
void MainWindow::on_btnRYp_clicked(){ IncrementalMove(4, +1); }
void MainWindow::on_btnRZp_clicked(){ IncrementalMove(5, +1); }

void MainWindow::IncrementalMove(int id, double sense){
    if (!Check_Robot()) { return; }

    // check the index
    if (id < 0 || id >= 6){
        qDebug()<< "Invalid id provided to for an incremental move";
        return;
    }

    // calculate the relative movement
    double step = sense * ui->spnStep->value();

    // apply to XYZWPR
    tXYZWPR xyzwpr;
    for (int i=0; i<6; i++){
        xyzwpr[i] = 0;
    }
    xyzwpr[id] = step;

    Mat pose_increment;
    pose_increment.FromXYZRPW(xyzwpr);

    Mat pose_robot = ROBOT->Pose();

    Mat pose_robot_new;

    // apply relative to the TCP:
    pose_robot_new = pose_robot * pose_increment;

    ROBOT->MoveJ(pose_robot_new);

}





void MainWindow::on_radSimulation_clicked()
{
    if (!Check_Robot()) { return; }

    // Important: stop any previous program generation (if we selected offline programming mode)
    ROBOT->Finish();

    // Set simulation mode
    RDK->setRunMode(RoboDK::RUNMODE_SIMULATE);
}

void MainWindow::on_radOfflineProgramming_clicked()
{
    if (!Check_Robot()) { return; }

    // Important: stop any previous program generation (if we selected offline programming mode)
    ROBOT->Finish();

    // Set simulation mode
    RDK->setRunMode(RoboDK::RUNMODE_MAKE_ROBOTPROG);

    // specify a program name, a folder to save the program and a post processor if desired
    RDK->ProgramStart("NewProgram");
}

void MainWindow::on_radRunOnRobot_clicked()
{
    if (!Check_Robot()) { return; }

    // Important: stop any previous program generation (if we selected offline programming mode)
    ROBOT->Finish();

    // Connect to real robot
    if (ROBOT->Connect())
    {
        // Set simulation mode
        RDK->setRunMode(RoboDK::RUNMODE_RUN_ROBOT);
    }
    else
    {
        ui->statusBar->showMessage("Can't connect to the robot. Check connection and parameters.");
    }

}

void MainWindow::on_btnMakeProgram_clicked()
{
    if (!Check_Robot()) { return; }

    // Trigger program generation
    ROBOT->Finish();

}



void MainWindow::robodk_window_clear(){
    if (robodk_window != NULL){
        robodk_window->setParent(NULL);
        robodk_window->setFlags(Qt::Window);
        //robodk_window->deleteLater();
        robodk_window = NULL;
        ui->widgetRoboDK->layout()->deleteLater();
    }
    // Make sure RoboDK widget is hidden
    ui->widgetRoboDK->hide();

    // Adjust the main window size
    adjustSize();
}


void MainWindow::on_radShowRoboDK_clicked()
{
    if (!Check_RoboDK()){ return; }

    // Hide embedded window
    robodk_window_clear();

    RDK->setWindowState(RoboDK::WINDOWSTATE_NORMAL);
    RDK->setWindowState(RoboDK::WINDOWSTATE_SHOW);
}

void MainWindow::on_radHideRoboDK_clicked()
{
    if (!Check_RoboDK()){ return; }

    // Hide embedded window
    robodk_window_clear();

    RDK->setWindowState(RoboDK::WINDOWSTATE_HIDDEN);

}

#ifdef _MSC_VER
HWND FindTopWindow(DWORD pid)
{
    std::pair<HWND, DWORD> params = { 0, pid };

    // Enumerate the windows using a lambda to process each window
    BOOL bResult = EnumWindows([](HWND hwnd, LPARAM lParam) -> BOOL
    {
        auto pParams = (std::pair<HWND, DWORD>*)(lParam);

        DWORD processId;
        if (GetWindowThreadProcessId(hwnd, &processId) && processId == pParams->second)
        {
            // Stop enumerating
            SetLastError(-1);
            pParams->first = hwnd;
            return FALSE;
        }

        // Continue enumerating
        return TRUE;
    }, (LPARAM)&params);

    if (!bResult && GetLastError() == -1 && params.first)
    {
        return params.first;
    }

    return 0;
}
#endif

void MainWindow::on_radIntegrateRoboDK_clicked()
{
    if (!Check_RoboDK()){ return; }

    qint64 procWID = RDK->ProcessID();
    if (procWID == 0) {
        ui->statusBar->showMessage("Invalid handle. Close RoboDK and open RoboDK with this application");
        return;
    }


#ifdef _MSC_VER
    if (procWID != 0){
        qDebug() << "Using parent process=" << procWID;
        //SetParent((HWND) procWID, (HWND)widget_container->window()->winId());

        // Retrieve the top level window
        HWND wid_rdk = FindTopWindow(procWID);
        qDebug() << "HWND RoboDK window: " << wid_rdk;
        //SetParent((HWND) wid_rdk, (HWND)widget_container->winId());//->window()->winId());
        if (wid_rdk == NULL){
            ui->statusBar->showMessage("RoboDK top level window was not found...");
            return;
        }
        //HWND wid_rdk = (HWND) RDK->WindowID();
        // set parent widget
        robodk_window = QWindow::fromWinId((WId)wid_rdk);
        QWidget *new_widget = createWindowContainer(robodk_window);
        QVBoxLayout *vl = new QVBoxLayout();
        ui->widgetRoboDK->setLayout(vl);
        vl->addWidget(new_widget);
        new_widget->show();
        this->adjustSize();

        RDK->setWindowState(RoboDK::WINDOWSTATE_SHOW);
        RDK->setWindowState(RoboDK::WINDOWSTATE_FULLSCREEN_CINEMA);

        // Show the RoboDK widget (embedded screen)
        ui->widgetRoboDK->show();
    }
#endif

}



/// <summary>
/// This is a sample function that is executed when a new RoboDK Event occurs.
/// </summary>
/// <param name="evt"></param>
/// <param name="itm"></param>
/// <returns></returns>
bool MainWindow::SampleRoboDkEvent(int evt, Item itm)
{
    qDebug() << "";
    qDebug() << "**** New event ****";

    //If this runs in a seperate thread from the api instance thaw sapwned it you won't be able to do
    //Regular api calls like item.Valid()
    //if (itm.Valid())
    //{
        //qDebug() << "  Item: " + itm.Name() + " -> Type: " + itm.Type();
    //}
    //else
    //{
        //Console.WriteLine("  Item not applicable");
    //}

    switch (evt)
    {
        case RoboDK::EVENT_SELECTION_TREE_CHANGED:
            qDebug() << "Event: Selection changed (the tree was selected)";
            break;
        case RoboDK::EVENT_ITEM_MOVED:
            qDebug() << "Event: Item Moved";
            break;
        case RoboDK::EVENT_REFERENCE_PICKED:
            qDebug() << "Event: Reference Picked";
            break;
        case RoboDK::EVENT_REFERENCE_RELEASED:
            qDebug() << "Event: Reference Released";
            break;
        case RoboDK::EVENT_TOOL_MODIFIED:
            qDebug() << "Event: Tool Modified";
            break;
        case RoboDK::EVENT_3DVIEW_MOVED:
            qDebug() << "Event: 3D view moved"; // use ViewPose to retrieve the pose of the camera
            break;
        case RoboDK::EVENT_ROBOT_MOVED:
            qDebug() << "Event: Robot moved";
            break;

        // Important: The following events require consuming additional data from the _COM_EVT buffer
        case RoboDK::EVENT_SELECTION_3D_CHANGED:
        {
            qDebug() << "Event: Selection changed";
            // data contains the following information (24 values):
            // pose (16), xyz selection (3), ijk normal (3), picked feature id (1), picked id (1)
            //double[] data = RDK._recv_Array(RDK->_COM_EVT);
            double data[24];
            int valueCount;
            RDK->Event_Receive_3D_POS(data,&valueCount);
            //
            Mat pose_abs = Mat(data);
            double xyz[3] = { data[16], data[17], data[18] };
            double ijk[3] = { data[19], data[20], data[21] };
            int feature_type = data[22];
            int feature_id = data[23];
            qDebug() << "Additional event data - Absolute position (PoseAbs):";
            qDebug() << pose_abs.ToString();
            qDebug() << "Additional event data - Point and Normal (point selected in relative coordinates)";
            qDebug() << QString::number(xyz[0]) + "," + QString::number(xyz[1]) + "," + QString::number(xyz[2]);
            qDebug() << QString::number(ijk[0]) + "," + QString::number(ijk[1]) + "," + QString::number(ijk[2]);
            qDebug() << "Feature Type and ID";
            qDebug() << QString::number(feature_type) + "-" + QString::number(feature_id);
            break;
        }
        case RoboDK::EVENT_KEY:
        {
            int mouseData[3];
            RDK->Event_Receive_Mouse_data(mouseData);
            int key_press = mouseData[0]; // 1 = key pressed, 0 = key released
            int key_id = mouseData[1]; // Key id as per Qt mappings: https://doc.qt.io/qt-5/qt.html#Key-enum
            int modifiers = mouseData[2]; // Modifier bits as per Qt mappings: https://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum
            qDebug() << "Event: Key pressed: " + QString::number(key_id) + " " + ((key_press > 0) ? "Pressed" : "Released") + ". Modifiers: " + QString::number(modifiers);
            break;
        }
        case RoboDK::EVENT_ITEM_MOVED_POSE:
        {
            Mat pose_rel;
            bool flag = RDK->Event_Receive_Event_Moved(&pose_rel);
            //int nvalues = _recv_Int(_COM_EVT);
            //Mat pose_rel = _recv_Pose(_COM_EVT);
            if (flag == false)
            {
                // future compatibility
            }
            qDebug() << "Event: item moved. Relative pose: " + pose_rel.ToString();
            break;
        }
        default:
            qDebug() << "Unknown event " + QString::number(evt);
            break;
    }
    return true;
}

bool MainWindow::EventsLoop()
{
    RDK->EventsListen();

    qDebug() << "Events loop started";
    while (RDK->Event_Connected())
    {
        int evt;
        Item itm;
        RDK->WaitForEvent(evt,itm);
        SampleRoboDkEvent(evt, itm);
    }
    qDebug() << "Event loop finished";
    return true;
}




void MainWindow::on_btnEmbed_clicked()
{
    if (!Check_RoboDK()){ return; }
    on_radShowRoboDK_clicked();
    EmbedExample *newWindow = new EmbedExample();
    newWindow->show();
    QString windowName = newWindow->windowTitle();
    qDebug() << windowName;
    RDK->EmbedWindow(windowName);

}
