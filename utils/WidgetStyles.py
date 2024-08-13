from PyQt5 import QtGui, QtWidgets, QtCore

class CenterAlignDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = QtCore.Qt.AlignCenter
        super(CenterAlignDelegate, self).paint(painter, option, index)


style_tableview = """
    
    QHeaderView::section:horizontal {
        background-color: #182939;
        color: white;
        padding: 4px;   
        border-radius: 0px;
    }
    QHeaderView::section:vertical {
        background-color: #D3D3D3;
        color: dimgray;
        padding: 4px;   
        border-radius: 0px;
    }

    QTableView {
    font-family: Candara;
    font-size: 11pt;
    border: none;
    }
    QTableView::item {
        border-bottom: 1px solid lightgray;
        background: none;
        
    }
    QTableView::item:selected{
        background:#B6C9FF;
        color:gray;
    }
    QTableView::item:hover {
    background-color: #D3F1FC;
}   
    
"""