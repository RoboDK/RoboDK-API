#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>


// TIP: use #define RDK_SKIP_NAMESPACE to avoid using namespaces
#include "robodk_api.h"


using namespace RoboDK_API;


namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

    void Select_Robot();

    bool Check_RoboDK();
    bool Check_Robot();

    void IncrementalMove(int id, double sense);


private slots:
    void on_btnLoadFile_clicked();
    void on_btnShowRoboDK_clicked();
    void on_btnHideRoboDK_clicked();
    void on_btnSelectRobot_clicked();
    void on_btnTestButton_clicked();
    void on_btnGetPosition_clicked();
    void on_btnMoveJoints_clicked();
    void on_btnMovePose_clicked();
    void on_btnProgRun_clicked();
    void on_btnTXn_clicked();
    void on_btnTYn_clicked();
    void on_btnTZn_clicked();
    void on_btnRXn_clicked();
    void on_btnRYn_clicked();
    void on_btnRZn_clicked();
    void on_btnTXp_clicked();
    void on_btnTYp_clicked();
    void on_btnTZp_clicked();
    void on_btnRXp_clicked();
    void on_btnRYp_clicked();
    void on_btnRZp_clicked();


private:
    Ui::MainWindow *ui;


    RoboDK *RDK;
    Item *ROBOT;
};

#endif // MAINWINDOW_H
