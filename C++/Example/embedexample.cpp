#include "embedexample.h"
#include "ui_embedexample.h"

EmbedExample::EmbedExample(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::EmbedExample)
{
    ui->setupUi(this);
}

EmbedExample::~EmbedExample()
{
    delete ui;
}
