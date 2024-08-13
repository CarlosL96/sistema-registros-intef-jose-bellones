from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QColor, QIcon, QCursor
from PyQt5.QtCore import Qt, QRect, QEvent, pyqtSignal
from PyQt5.QtWidgets import QStyledItemDelegate
import pandas as pd
import numpy as np


class TableModel(QtCore.QAbstractTableModel):
    checkboxToggled = pyqtSignal(int, int, bool)

    def __init__(self, data, editable_columns=None, icon_columns=None, checkBox_columns = None):
        super(TableModel, self).__init__()
        self._data = data
        self.colors = dict()
        self._icon_columns = set(icon_columns) if icon_columns else set()
        self._editable_columns = set(
            editable_columns) if editable_columns else set()
        self._checkBox_columns = set(
            checkBox_columns) if checkBox_columns else set()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if index.column() in self._checkBox_columns:
                return None  # Devolver None para evitar mostrar texto en las celdas de checkbox
            else:
                return str(value) if pd.notna(value) else ""
        elif role == Qt.TextColorRole:
            value = self._data.iloc[index.row(), index.column()]
            if value is None or str(value) == "nan" or str(value) == "-":
                return Qt.red
        elif role == Qt.BackgroundRole:
            color = self.colors.get((index.row(), index.column()))
            if color is not None:
                return color
        elif role == Qt.DecorationRole:
            if index.column() in self._icon_columns:
                icon_path = self._data.iloc[index.row(), index.column()]
                if pd.notna(icon_path):
                    return QIcon(icon_path)
        elif role == Qt.CheckStateRole:
            if index.column() in self._checkBox_columns:
                value = self._data.iloc[index.row(), index.column()]
                return Qt.Checked if value else Qt.Unchecked
        elif role == Qt.TextAlignmentRole:
            if index.column() in self._icon_columns:
                return Qt.AlignCenter

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def flags(self, index):
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() in self._editable_columns:
            default_flags |= Qt.ItemIsEditable
        if index.column() in self._checkBox_columns:
            default_flags |= Qt.ItemIsUserCheckable
        return default_flags
       

    def setData(self, index, value, role):
        if role == Qt.EditRole and index.column() in self._editable_columns:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        elif role == Qt.CheckStateRole and index.column() in self._checkBox_columns:
            # Emitir señal cuando se marca/desmarca una casilla de verificación
            is_checked = value == Qt.Checked
            self._data.iloc[index.row(), index.column()] = is_checked
            self.dataChanged.emit(index, index)
            self.checkboxToggled.emit(index.row(), index.column(), is_checked)
            return True
        return False


    def clear(self):
        self.beginResetModel()
        self._data = pd.DataFrame()
        self.endResetModel()

    def setEditableColumns(self, editable_columns):
        self._editable_columns = set(editable_columns)
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(0), self.columnCount(0)),
        )

    def change_color(self, row, column, color):
        ix = self.index(row, column)
        self.colors[(row, column)] = color
        self.dataChanged.emit(ix, ix, (Qt.BackgroundRole,))

    def get_dataframe(self):
        return self._data.copy()


class IconDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, icon_columns=None):
        super().__init__(parent)
        self.hovered_index = None
        self.icon_columns = icon_columns or []

    def paint(self, painter, option, index):
        if index.column() in self.icon_columns:
            if index == self.hovered_index:
                painter.save()
                painter.fillRect(option.rect, QBrush(QColor(220, 220, 255)))
                painter.restore()

            icon = QIcon(index.data(Qt.DecorationRole))
            if not icon.isNull():
                size = option.rect.size()
                icon_size = icon.actualSize(size)
                icon_scale = 0.7
                x = option.rect.x() + (size.width() - icon_size.width()*icon_scale) / 2
                y = option.rect.y() + (size.height() - icon_size.height()*icon_scale) / 2
                icon.paint(painter, QRect(int(x), int(y), int(
                    icon_size.width()*icon_scale), int(icon_size.height()*icon_scale)))
        else:
            super(IconDelegate, self).paint(painter, option, index)

    def updateCursor(self, index):
        if index.column() in self.icon_columns:
            self.parent().viewport().setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.parent().viewport().setCursor(QCursor(Qt.ArrowCursor))

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseMove or event.type() == QEvent.HoverEnter:
            self.hovered_index = index
            self.parent().viewport().update()
            self.updateCursor(index)

        return super().editorEvent(event, model, option, index)
