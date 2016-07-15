#pragma once

#include <QWidget>
#include <QLabel>

class Label : public QWidget {

  public:
    Label(QWidget *parent = 0);

  private:
    QLabel *label;
};
