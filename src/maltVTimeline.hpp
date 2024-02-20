#include <QAbstractItemView>
#include <QApplication>
#include <QChart>
#include <QChartView>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QLineSeries>
#include <QPainter>
#include <QSizePolicy>
#include <QTableWidget>
#include <QTableWidgetItem>
#include <QVBoxLayout>
#include <QWidget>
#include <QFont>
#include <QEvent>
#include <iostream>
#include <vector>
//MaltQtStack

#ifndef MALTVTIMELINE_
#define MALTVTIMELINE_
#include "maltReaderJSON.hpp"
#include "maltVChart.hpp"
#include "maltVStack.hpp"
class MaltVTimeline : public QWidget {

  Q_OBJECT
  
public:
  int lastIndex = 0;
  bool markIndex = true;
  std::vector<QLineSeries*> series;
  std::vector<struct TimelineEntry> timeline;
  QChart  *chart;
  //MaltVChart  *chart;
  MaltVChartView *chart_view;
  MaltVStack *stack_view;
  
  MaltVTimeline(MaltReaderJSON *data) {
    std::cout << "________________getTimeline" << std::endl;
    timeline = data->getAnnotatedTimeline(); //< returns the memory timeline
    std::cout << "________________genseries" << std::endl;
    series = genSeries_(1048576.);
    std::cout << "________________chart" << std::endl;
    chart = new QChart();
    // chart = new MaltVChart();
    for (auto &s : series) {
      chart->addSeries(s);
    }
    std::cout << "________________-info" << std::endl;
    info = new QTableWidget();
    info->setEditTriggers(QAbstractItemView::NoEditTriggers);
    info->setSelectionMode(QAbstractItemView::NoSelection);
    info->setRowCount(5);
    info->setColumnCount(2);
    info->horizontalHeader()->hide();
    info->verticalHeader()->hide();
    info->setItem(0, 0, rightAlignedItem("Click"));
    info->setItem(1, 0, rightAlignedItem("Timeline"));
    info->setItem(2, 0, rightAlignedItem("To"));
    info->setItem(3, 0, rightAlignedItem("Update"));
    info->setItem(4, 0, rightAlignedItem("Table"));

    info->setItem(0, 1, leftAlignedItem("walltime, s"));
    info->setItem(1, 1, leftAlignedItem("physical, MB"));
    info->setItem(2, 1, leftAlignedItem("virtual, MB"));
    info->setItem(3, 1, leftAlignedItem("requested, MB"));
    info->setItem(4, 1, leftAlignedItem("Index"));
    info->horizontalHeader()->setStretchLastSection(true);

    
    std::cout << "________________-stack_view" << std::endl;
    stack_view = new MaltVStack(data->instrMap());
    
    chart->createDefaultAxes();
    //    chart_view = new QChartView(chart);
    chart_view = new MaltVChartView(chart);
    chart_view->setRenderHint(QPainter::Antialiasing);
    chart_view->installEventFilter(this);
    QVBoxLayout *layoutLeft = new QVBoxLayout();
    QHBoxLayout *layout = new QHBoxLayout();

    layoutLeft->addWidget(info);
    layoutLeft->addWidget(stack_view->table_view);
    
    QSizePolicy size(QSizePolicy::Preferred, QSizePolicy::Preferred);
    size.setHorizontalStretch(1);
    size.setVerticalStretch(1);
    info->setSizePolicy(size);
    size.setVerticalStretch(4);
    stack_view->table_view->setSizePolicy(size);

    size.setHorizontalStretch(4);
    size.setVerticalStretch(5);
    chart_view->setSizePolicy(size);
    

    layout->addLayout(layoutLeft);
    layout->addWidget(chart_view);
    setLayout(layout);
  }
public slots:
    void clickSeries(const QPointF p) {
      auto t = p.x();
      auto entry = closest(t, timeline);
      markIndex = false;
      memTableUpdate();
    }

  bool eventFilter(QObject *widget, QEvent *event) {
    if (widget == chart_view ) {
      if (event->type() == QEvent::MouseMove) {
	std::cout << "move move" << std::endl;
	QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
	clickSeries(chart->mapToValue(mouseEvent->pos()));
	return true;
      } else if (event->type() == QEvent::MouseButtonPress) {
	QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
	clickSeries(chart->mapToValue(mouseEvent->pos()));
	return true;
      } else if (event->type() == QEvent::KeyPress ) {
	QKeyEvent *keyEvent = static_cast<QKeyEvent *>(event);
	auto key = keyEvent->key();
	auto modifiers = QApplication::keyboardModifiers();
	int shift = (modifiers & Qt::ShiftModifier ? 10:1);
	if (key == Qt::Key_Left) {
	  lastIndex -= shift;
	  if (lastIndex < 0) {
	    lastIndex = 0;
	  }
	  memTableUpdate();
	  return true;
	} else if ( key == Qt::Key_Right) {
	  lastIndex += shift;
	  if (lastIndex >= timeline.size()) {
	    lastIndex = timeline.size()-1;
	  }
	  memTableUpdate();
	  return true;
	}
      }
    }
    return QWidget::eventFilter(widget, event);
  }

private:
  //    """Creates a timeline widget"""
  void memTableUpdate() {
    // """Updates the information in the memory table"""
    auto &e = timeline[lastIndex];
    stack_view->updateStack(e.stack);
    info->setItem(0, 0, rightAlignedItemFloat(e.t));
    info->setItem(1, 0, rightAlignedItemFloat(e.physicalM/1048576.));
    info->setItem(2, 0, rightAlignedItemFloat(e.virtualM/1048576.));
    info->setItem(3, 0, rightAlignedItemFloat(e.requestedM/1048576.));
    chart_view->setDrawCondition(lastIndex, e.t);
  }
  QTableWidget *info;
  QTableWidgetItem *rightAlignedItem(const char *theText) {
    // """Returns a right aligned table item"""
    auto item = new QTableWidgetItem(theText);
    item->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
    item->setFont(QFont("Courier New"));
    return item;
  }

  template <typename T>
  QTableWidgetItem *rightAlignedItemFloat(const T value) {
    // """Returns a right aligned table item"""
    char c[128];
    snprintf(c,128, "%.3f", float(double(value)));
    return rightAlignedItem(c);
  }
  
  QTableWidgetItem *leftAlignedItem(const char *theText) {
    // """Returns a right aligned table item"""
    auto item = new QTableWidgetItem(theText);
    item->setTextAlignment(Qt::AlignLeft | Qt::AlignVCenter);
    item->setFont(QFont("Courier New"));
    return item;
  }
  
  std::vector<QLineSeries*> genSeries_(float scale=1.0) {
    //"""Given a x and y index into values returns a QLineSeries"""
    std::vector<QLineSeries*> retVal;
    auto phys = new QLineSeries();
    auto virt = new QLineSeries();
    auto req = new QLineSeries();

    retVal.push_back(phys);
    retVal.push_back(virt);
    retVal.push_back(req);
    
    connect(phys, &QLineSeries::clicked, this, &MaltVTimeline::clickSeries);
    connect(virt, &QLineSeries::clicked, this, &MaltVTimeline::clickSeries);
    connect(req, &QLineSeries::clicked, this, &MaltVTimeline::clickSeries);

    phys->setName("physical");
    virt->setName("virtual");
    req->setName("requested");
    for (auto &entry: timeline) {
      phys->append(entry.t, float(double(entry.physicalM)/scale));
      virt->append(entry.t, float(double(entry.virtualM)/scale));
      req->append(entry.t, float(double(entry.requestedM)/scale));
    }
    return retVal;
  }
  
  const struct TimelineEntry closest(float t, std::vector<struct TimelineEntry>timeline) {
    // return closest entry in time
    auto dt = abs(t) + abs(timeline[0].t);
    auto last = timeline[0];
    int index = 0;
    for (auto &x : timeline) {
      if (dt >= abs(t-x.t)) {
	dt = abs(t-x.t);
	last = x;
	lastIndex = index;
      }
      if (x.t > last.t) {
	return x;
      }
      index++;
    }
    return last;
  }
};
#endif
