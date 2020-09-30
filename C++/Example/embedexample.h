#ifndef EMBEDEXAMPLE_H
#define EMBEDEXAMPLE_H

#include <QWidget>

namespace Ui {
class EmbedExample;
}

class EmbedExample : public QWidget
{
    Q_OBJECT

public:
    explicit EmbedExample(QWidget *parent = nullptr);
    ~EmbedExample();

private:
    Ui::EmbedExample *ui;
};

#endif // EMBEDEXAMPLE_H
