#include <QColor>
#include <QPainter>
#include <QPen>
#include <QChart>
#include <QChartView>
#include <QMouseEvent>
#include <iostream>
#include <QValueAxis>
#ifndef MALTVCHART_
#define MALTVCHART_

// circular dependency :-(
//class MaltVTiming;
class MaltVChartView : public QChartView {
  Q_OBJECT
public:
  float t;
  int index = 0;
  int lastIndex = -1;
  QChart *myChart;

  MaltVChartView(QChart *chart) : QChartView(chart) {
    myChart = chart;
    setDragMode(QGraphicsView::NoDrag);
  }
  
  void setDrawCondition(int index, float t) {
    this->index = index;
    this->t = t;
    if (index != lastIndex) {
      myChart->update();
    }
  }
  
  void drawForeground(QPainter *painter, const QRectF &rect) {
    //        """This is where we draw the red line when the timeline is clicked"""
    QChartView::drawForeground(painter, rect);
    
    if (index == lastIndex) {
      return;
    }
    lastIndex = index;
    auto pen = QPen(QColor("red"));
    pen.setWidthF(0.25);
    painter->setPen(pen);
    
    auto area = myChart->plotArea();
    auto xAxis = static_cast<const QValueAxis*>(myChart->axes(Qt::Horizontal).first());
    auto hmin = float(xAxis->min());
    auto hmax = float(xAxis->max());
    auto ratio = (t - hmin) / (hmax - hmin);
    auto tpos = area.x() + area.width() * ratio;
    auto point = QPointF(tpos, area.y());
    auto point2 = QPointF(tpos, area.y() + area.height());
    painter->drawLine(point, point2);
  }
};
#endif
