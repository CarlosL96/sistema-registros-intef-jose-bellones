from ui.mainUi import Ui_MainWindow
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from utils.PandasTableModel import TableModel
from utils.WidgetStyles import style_tableview, CenterAlignDelegate
from utils.CalendarDialog import CalendarDialog
from utils.LoadingDialog import Worker, LoadingDialog
from db.db import createConnectionPool, getConnection
from datetime import datetime
import pandas as pd
import traceback


class UtilsUILogic:
    def __init__(self, mainWindow: Ui_MainWindow, icon):
        self.mainWindow = mainWindow
        self.icon = icon
        self.connectionPool = self.getPool()

    def getPool(self):
        try:
            pool = createConnectionPool()
            return pool
        except Exception as e:
            traceback.print_exc()
            self.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error de comunicación la Base de datos, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error saving product records:", e)

    def updateUI(self, mainWindow):
        self.mainWindow = mainWindow

    def showMessageBox(self, title, text, icon, buttons):
        msg = QMessageBox()
        if not icon:
            icon = QMessageBox.Critical
        msg.setIcon(icon)
        msg.setWindowIcon(self.icon)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(buttons)
        retval = msg.exec_()
        return retval

    def show_calendar(self, strTitle="Seleccione una fecha"):
        dialog = CalendarDialog(self.mainWindow, icon=self.icon)
        dialog.setWindowTitle(strTitle)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.selected_date
            formatted_date = selected_date.toString("dd/MM/yyyy")
            return formatted_date

    def populateTableViewFromDataFrame(self, refTable: QTableView, refData: pd.DataFrame, stretchMode=True):
        model = TableModel(refData)
        refTable.setModel(model)
        refTable.setStyleSheet(style_tableview)
        refTable.setShowGrid(False)
        refTable.verticalHeader().setVisible(False)
        delegate = CenterAlignDelegate(refTable)
        refTable.setItemDelegate(delegate)
        if stretchMode:
            header = refTable.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def resizeColumnsToContents(self, refTable: QTableView):
        header = refTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def executeSQL(self, strSQL, loadingPrompt="Consultando a la base de datos", params=None):
        self.results = []
        def sql(self, strSQL):
            try:
                connection = getConnection()
                cursor = connection.cursor()
                if params:
                    cursor.execute(strSQL, params)
                else:
                    cursor.execute(strSQL)
                self.results = cursor.fetchall()
            except Exception as e:
                traceback.print_exc()
                self.utils.showMessageBox(
                    "Ha ocurrido un error", "Ocurrió un error inesperado durante la consulta a la base de datos, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
                print("Error saving product records:", e)
            finally:
                if not cursor is None:
                    cursor.close()
                    connection.close()
        self.loading_dialog = LoadingDialog(loadingPrompt)
        self.worker = Worker(sql, self, strSQL)
        self.loading_dialog.start(self.worker)        
        return self.results

    def executeSQLInsertOrUpdate(self, strSQL, params, loadingPrompt="Consultando a la base de datos"):
        def insert(self, strSQL, params):
            try:
                connection = getConnection()
                cursor = connection.cursor()
                cursor.execute(strSQL, params)
                connection.commit()
            except Exception as e:
                traceback.print_exc()
                self.utils.howMessageBox(
                    "Ha ocurrido un error", "Ocurrió un error inesperado durante el proceso, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
                print("Error saving product records:", e)
            finally:
                if not cursor is None:
                    cursor.close()
                    connection.close()
        self.loading_dialog = LoadingDialog(loadingPrompt)
        self.worker = Worker(insert, self, strSQL, params)
        self.loading_dialog.start(self.worker)

    def executeSQLInsertOrUpdateMany(self, strSQL, params, loadingPrompt="Consultando a la base de datos"):
        def insertMany(self, strSQL, params):
            try:
                connection = getConnection()
                cursor = connection.cursor()
                cursor.executemany(strSQL, params)
                connection.commit()
            except Exception as e:
                traceback.print_exc()
                self.utils.showMessageBox(
                    "Ha ocurrido un error", "Ocurrió un error inesperado durante la consulta de productos, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
                print("Error saving product records:", e)
            finally:
                if not cursor is None:
                    cursor.close()
                    connection.close()
        self.loading_dialog = LoadingDialog(loadingPrompt)
        self.worker = Worker(insertMany, self, strSQL, params)
        self.loading_dialog.start(self.worker)

    def getMysqlFormattedDate(self, strDate):
        dateObj = datetime.strptime(strDate, "%d/%m/%Y")
        return {"str": dateObj.strftime("%Y-%m-%d"), "dateObj": dateObj}

    def get_user_input(self, title, text, default_value=""):
        dialog = QInputDialog(self.mainWindow)
        dialog.setWindowIcon(self.icon)
        dialog.setWindowTitle(title)
        dialog.setLabelText(text)
        dialog.setTextValue(default_value)
        dialog.setTextEchoMode(QLineEdit.Normal)

        if dialog.exec_() == QInputDialog.Accepted:
            return dialog.textValue()
        else:
            return ""
