//"""Create a stack view"""
#include <QAbstractTableModel>
#include <QColor>
#include <QModelIndex>
#include <QTableView>
#include <QVariant>
#include <QWidget>
#include <vector>
#include <string>
#include "maltReaderJSON.hpp"

#ifndef MALTVSTACK_
#define MALTVSTACK_
class MaltStackTableModel : public QAbstractTableModel {
  Q_OBJECT
public:  
  std::vector<std::string> stack;
  std::vector<int> lines;
  std::vector<std::string> functions;
  std::map<std::string, struct InstrMapItem> &lookup;
  MaltStackTableModel(std::map<std::string, struct InstrMapItem> &inlookup) : lookup(inlookup) {
    lines.push_back(-1);
    functions.push_back("No Stack");
  }
  
  void load_data(std::vector<std::string> &theStack) {
    lines.clear();
    functions.clear();
    stack = theStack;
    if (stack.size() < 1) {
      lines.push_back(-1);
      functions.push_back("no stack available");
    }	else {
      for (auto &s: stack) {
	if (lookup.find(s) == lookup.end()) {
	  lines.push_back(-1);
	  functions.push_back(s);
	} else {
	  auto &d = lookup[s];
	  lines.push_back(d.line);
	  functions.push_back(d.function);
	}
      }
    }
    emit layoutChanged();
  }
  
  int rowCount(const QModelIndex &parent = QModelIndex()) const  {
    return lines.size();
  }
  int columnCount(const QModelIndex &parent = QModelIndex()) const {
    return 2;
  }
  QVariant headerData(int section, Qt::Orientation orientation, int role=Qt::DisplayRole) const {
    if (role != Qt::DisplayRole) {
      return QVariant();
    }
    if (orientation == Qt::Horizontal || orientation == Qt::Vertical) {
      if (section == 0) {
	return QVariant("Line");
      } else {
	return QVariant("function");
      }
    }
    return QVariant();
  }
  QVariant data(const QModelIndex &index, int role) const {
    auto column = index.column();
    auto row = index.row();
    if (role == Qt::DisplayRole) {
      if (column == 0) {
	return QVariant(lines[row]);
      } else {
	return QVariant(functions[row].c_str());
      }
    } else if (role == Qt::BackgroundRole) {
      return QColor(Qt::white);
    } else if (role == Qt::ForegroundRole) {
      return QColor(Qt::black);
    } else if (role == Qt::TextAlignmentRole) {
      if (column == 1) {
	return QVariant(Qt::AlignLeft);
      } else {
	return QVariant(Qt::AlignRight);
      }
    }
    return QVariant();
  }
};

class MaltVStack : public QWidget {
  Q_OBJECT
public:
  QTableView *table_view;
  MaltStackTableModel *model;
  MaltVStack(std::map<std::string, struct InstrMapItem> &inlookup) {
    model = new MaltStackTableModel(inlookup);
    table_view = new QTableView();
    table_view->setModel(model);
    table_view->verticalHeader()->hide();
  }
  void updateStack(std::vector<std::string> &theStack) {
    model->load_data(theStack);
    table_view->resizeRowsToContents();
    update();
  }
  QHeaderView *	horizontalHeader() const {
    return table_view->horizontalHeader();
  }
  QHeaderView *	verticalHeader() const {
    return table_view->verticalHeader();
  }
};
#endif
