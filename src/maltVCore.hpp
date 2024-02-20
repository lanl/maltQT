#include <QWidget>
#include <QMainWindow>
#ifndef MALTVCORE_
#define MALTVCORE_
#include "maltReaderJSON.hpp"
#include "maltVTimeline.hpp"

class MaltVCore: public QWidget {
  Q_OBJECT
public:
  MaltReaderJSON *data;
  QTabWidget *tabs;
  QWidget *a, *b;
  MaltVCore(char *fname) {
    window_ = new QMainWindow();
    window_->setWindowTitle(QString::fromStdString(fname));
    window_->setMinimumWidth(800);
    window_->setMinimumHeight(900);
    std::cout << "________________getdata" << std::endl;
    data = new MaltReaderJSON(fname);
    std::cout << "________________done" << std::endl;
    //data->print();
    auto myChart = new MaltVTimeline(data);

    window_->resize(1800, 900);
    tabs = new QTabWidget();
    tabs->setTabPosition(QTabWidget::West);
    tabs->setMovable(true);
    tabs->setDocumentMode(true);
    b = new QWidget();
    tabs->addTab(myChart,"first");
    //tabs->addTab(b,"timeline");

    // # Initialize timeline view and display it
    // self.tv = MaltQtTimeline(self.window, self.data)
    // tabs.addTab(self.tv, "Timeline")

    // # Attach tab to window
    window_->setCentralWidget(tabs);
    window_->show();
  }
private:
  QMainWindow *window_;
  //  std::vector<TimelineEntry> timeline_;
};
#endif
