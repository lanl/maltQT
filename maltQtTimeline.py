"""
Display timeline information in a Qt Chart with
clicks to show stack information.
"""
from PySide6 import QtCore
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from maltQtStack import MaltQtStack

class MaltQtTimeline(QWidget):
        """Creates a timeline widget"""
        def genSeries(self, label, idx, idy, values, scale=1.0):
            """Given a x and y index into values returns a QLineSeries"""
            series = QLineSeries()
            series.setName(label)
            idMax = idx if idx > idy else idy
            for v in values:
                if len(v) <= idMax:
                    print('skip ', v, idx, idy)
                    continue
                series.append(v[idx], v[idy]/scale)
            return series
            
        def __init__(self, parent, data):

            # Initialize the widget
            super().__init__(parent)
            
            self.setGeometry(parent.geometry())
            #self.setGeometry((2 * parent.width())/3, 0, parent.width()/2, parent.height())
            
            # Squirrel away data
            self.data = data

            # Create series for timeline
            timeline = self.data.getAnnotatedTimeline()
            values = timeline['values']
            fields = timeline['fields']
            idxT = fields.index('t')
            idxS = fields.index('stack')
            idxP = fields.index('physicalMem')
            idxR = fields.index('requestedMem')
            idxV = fields.index('virtualMem')

            print('print(idxT, idxS, idxP, idxR, idxV, fields)')
            print(idxT, idxS, idxP, idxR, idxV, fields)
            self.pMem = self.genSeries("Physical Memory(MB)", idxT, idxP, values, 1048576.)
            self.rMem = self.genSeries("Requested Memory(MB)", idxT, idxR, values, 1048576.)
            self.vMem = self.genSeries("Virtual Memory(MB)", idxT, idxV, values, 1048576.)
            self.stacks = [x[idxS] if idxS < len(x) else ['??','??',-1] for x in values]

            self.chart = QChart()
            self.chart.addSeries(self.pMem)
            self.chart.addSeries(self.rMem)
            self.chart.addSeries(self.vMem)
            self.chart.createDefaultAxes()

            # QWidget Layout

            # Left layout: stacks
            self.table_view = MaltQtStack(self.stacks).table_view

            resize = QHeaderView.ResizeToContents
            self.horizontal_header = self.table_view.horizontalHeader()
            self.vertical_header = self.table_view.verticalHeader()
            self.horizontal_header.setSectionResizeMode(resize)
            self.vertical_header.setSectionResizeMode(resize)
            self.horizontal_header.setStretchLastSection(True)

            # Generate chart
            self.chart_view = QChartView(self.chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)

            self.main_layout = QHBoxLayout()
            size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

            # Left layout
            size.setHorizontalStretch(1)
            self.table_view.setSizePolicy(size)
            self.main_layout.addWidget(self.table_view)
            
            # Right layout: chart
            size.setHorizontalStretch(4)
            self.chart_view.setSizePolicy(size)
            self.main_layout.addWidget(self.chart_view)

            # Set layout to the QWidget
            self.setLayout(self.main_layout)

            
        @QtCore.Slot()
        def magic(self):
            self.parent().topMagic(self.text)
            #self.text.setText(random.choice(self.hello))
            

