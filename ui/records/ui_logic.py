from ui.mainUi import Ui_MainWindow
from ui.utils.ui_logic import UtilsUILogic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableView
from datetime import datetime
from utils.PandasTableModel import SingleCheckboxDelegate
from utils.LoadingDialog import Worker, LoadingDialog
import pandas as pd
import traceback
import os


class RecordsUILogic:
    def __init__(self, mainWindow: Ui_MainWindow, utils: UtilsUILogic):
        self.mainWindow = mainWindow
        self.utils = utils
        self.recordData = pd.DataFrame()
        self.selectedId = None
        self.recordCreatedBy = None
        self.sellAllQuery = """SELECT
                        id,
                        fechaIngreso,
                        fechaEgreso,
                        tipo,
                        numero,
                        titulo,
                        observacion,
                        folio,
                        destinatario,
                        createdBy
                    FROM
                        sistema_registros
                    ORDER BY
                        id DESC
                    """
        self.connectSignals()
        self.getPageContents()

    def connectSignals(self):
        self.mainWindow.btnGetRecordStartDate.clicked.connect(
            self.getRecordStartDate)
        self.mainWindow.btnGetRecordEndDate.clicked.connect(
            self.getRecordEndDate)
        self.mainWindow.btnRecordInsert.clicked.connect(self.onSaveRecordClick)
        self.mainWindow.btnRecordUpdate.clicked.connect(
            self.onUpdateRecordClick)
        self.mainWindow.btnRecordDelete.clicked.connect(
            self.onDeleteRecordClick)
        self.mainWindow.btnSearchRecords.clicked.connect(
            self.onSearchRecordsClick)
        self.mainWindow.btnGetSearchEndDate.clicked.connect(
            self.getRecordSearchEndDate)
        self.mainWindow.btnGetSearchStartDate.clicked.connect(
            self.getRecordSearchStartDate)
        self.mainWindow.btnClearSearchRecords.clicked.connect(
            self.clearSearchControls)
        self.mainWindow.btnRecordExport.clicked.connect(self.onExportClick)

    def getPageContents(self):
        recordTypes = ["Seleccione", "Expediente", "Resolución",
                       "Dispocisión", "Acta", "Otro"]
        self.mainWindow.cmbRecordType.clear()
        self.mainWindow.cmbSearchRecordType.clear()
        self.mainWindow.cmbRecordType.addItems(recordTypes)
        self.mainWindow.cmbSearchRecordType.addItems(recordTypes)
        self.mainWindow.lblSystemUsername.setText(
            self.utils.loginInfo["username"])
        self.populateRecordsTable(self.sellAllQuery)

    def onSaveRecordClick(self):
        try:

            startDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtRecordStartDate.text())
            endDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtRecordEndDate.text())
            recordStartDate = startDate["str"]
            recordEndDate = endDate["str"]
            recordType = self.mainWindow.cmbRecordType.currentText()
            recordNumber = self.mainWindow.txtRecordNumber.text()
            recordTitle = self.mainWindow.txtRecordTitle.text()
            recordObs = self.mainWindow.txtRecordObservation.toPlainText()
            recordFolium = self.mainWindow.txtRecordFolium.text()
            recordDestiny = self.mainWindow.txtRecordDestination.text()
            createdBy = self.mainWindow.lblSystemUsername.text()

            if "" in [recordStartDate, recordEndDate, recordType, recordNumber, recordTitle, recordObs, recordFolium, recordDestiny, createdBy] or self.mainWindow.cmbRecordType.currentIndex() == 0:
                self.utils.showMessageBox(
                    "Error de validación", "No ha completado todos los campos requeridos", QMessageBox.Critical, QMessageBox.Ok)
                return

            recordData = (recordStartDate, recordEndDate, recordType, recordNumber,
                          recordTitle, recordObs, recordFolium, recordDestiny, createdBy)
            strSQL = "INSERT INTO sistema_registros (fechaIngreso, fechaEgreso, tipo, numero, titulo, observacion, folio, destinatario, createdBy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.utils.executeSQLInsertOrUpdate(
                strSQL, recordData, "Guardando registro...")
            self.populateRecordsTable(self.sellAllQuery)
            self.utils.showMessageBox(
                "Registro Guardado", "Registrado correctamente", QMessageBox.Information, QMessageBox.Ok)
            self.clearControls()
        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante el proceso, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error saving records:", e)

    def onUpdateRecordClick(self):
        try:
            recordId = int(self.selectedId)
            recordCreatedBy = self.recordCreatedBy
            recordUpdatedBy = self.utils.loginInfo["username"]
            response = self.utils.showMessageBox(
                "Se necesita confirmación", "¿Está seguro que desea actualizar este registro?", QMessageBox.Warning, QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                return
            if (not recordId or not recordCreatedBy):
                return

            if recordUpdatedBy != recordCreatedBy and self.utils.loginInfo["userRole"] != 1:
                return self.utils.showMessageBox("Operación no permitida", "Su usuario no puede editar este registro", QMessageBox.Critical, QMessageBox.Ok)

            startDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtRecordStartDate.text())
            endDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtRecordEndDate.text())
            recordStartDate = startDate["str"]
            recordEndDate = endDate["str"]
            recordType = self.mainWindow.cmbRecordType.currentText()
            recordNumber = self.mainWindow.txtRecordNumber.text()
            recordTitle = self.mainWindow.txtRecordTitle.text()
            recordObs = self.mainWindow.txtRecordObservation.toPlainText()
            recordFolium = self.mainWindow.txtRecordFolium.text()
            recordDestiny = self.mainWindow.txtRecordDestination.text()

            if "" in [recordStartDate, recordEndDate, recordType, recordNumber, recordTitle, recordObs, recordFolium, recordDestiny, recordUpdatedBy] or self.mainWindow.cmbRecordType.currentIndex() == 0:
                self.utils.showMessageBox(
                    "Error de validación", "No ha completado todos los campos requeridos", QMessageBox.Critical, QMessageBox.Ok)
                return
            recordData = (recordStartDate, recordEndDate, recordType, recordNumber,
                          recordTitle, recordObs, recordFolium, recordDestiny, recordUpdatedBy, recordId)
            strSQL = "UPDATE sistema_registros  SET fechaIngreso = %s, fechaEgreso = %s, tipo = %s, numero = %s, titulo = %s, observacion = %s, folio = %s, destinatario = %s, updatedBy = %s, updatedAt = NOW() WHERE id = %s"
            self.utils.executeSQLInsertOrUpdate(
                strSQL, recordData, "Actualizando registro...")
            self.populateRecordsTable(self.sellAllQuery)
            self.utils.showMessageBox(
                "Registro actualizado", "Registrado actualizado correctamente", QMessageBox.Information, QMessageBox.Ok)
            self.clearControls()
        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante el proceso, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error saving records:", e)

    def onDeleteRecordClick(self):
        try:
            recordId = int(self.selectedId)
            recordCreatedBy = self.recordCreatedBy
            recordUpdatedBy = self.utils.loginInfo["username"]
            response = self.utils.showMessageBox(
                "Se necesita confirmación", "¿Está seguro que desea eliminar este registro?", QMessageBox.Warning, QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                return
            if (not recordId or not recordCreatedBy):
                return

            if recordUpdatedBy != recordCreatedBy and self.utils.loginInfo["userRole"] != 1:
                return self.utils.showMessageBox("Operación no permitida", "Su usuario no puede eliminar este registro", QMessageBox.Critical, QMessageBox.Ok)

            recordData = list((recordId, ))
            strSQL = "DELETE FROM sistema_registros WHERE id = %s"
            self.utils.executeSQLInsertOrUpdate(
                strSQL, recordData, "Eliminando registro...")
            self.populateRecordsTable(self.sellAllQuery)
            self.utils.showMessageBox(
                "Registro eliminado", "Registrado eliminado correctamente", QMessageBox.Information, QMessageBox.Ok)
            self.clearControls()
        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante el proceso, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error saving records:", e)

    def onSearchRecordsClick(self):
        try:

            strStartDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtSearchRecordStartDate.text())["str"]
            strEndDate = self.utils.getMysqlFormattedDate(
                self.mainWindow.txtSearchRecordEndDate.text())["str"]

            if self.mainWindow.cmbSearchRecordType.currentIndex() == 0:
                strRecordType = ""
            else:
                strRecordType = self.mainWindow.cmbSearchRecordType.currentText()
            searchCriteria = {
                "fechaIngreso": strStartDate,
                "fechaEgreso": strEndDate,
                "tipo": strRecordType,
                "numero": self.mainWindow.txtSearchRecordNumber.text()
            }

            filters = []
            params = {}
            for key, value in searchCriteria.items():
                if value is not None:
                    if isinstance(value, str):
                        filters.append(f"{key} LIKE %({key})s")
                        params[key] = f"%{value}%"
                    else:
                        filters.append(f"{key} = %({key})s")
                        params[key] = value

            # Construcción de la consulta SQL
            strSQL = """SELECT
                        id,
                        fechaIngreso,
                        fechaEgreso,
                        tipo,
                        numero,
                        titulo,
                        observacion,
                        folio,
                        destinatario,
                        createdBy
                    FROM
                        sistema_registros                    
                    """
            if filters:
                strSQL += " WHERE " + " AND ".join(filters)

            strSQL = strSQL + " ORDER BY id DESC "
            self.populateRecordsTable(strSQL, params)
        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante la consulta a la base de datos, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error getting records:", e)

    def onExportClick(self):
        if self.recordData.empty:
            return
        try:
            filename = str(
                QFileDialog.getExistingDirectory(
                    None, "Seleccione el directorio donde se guardará el resumen"
                )
            )
            if filename == "":
                return
            timestamp = datetime.today().strftime("%Y-%m-%d_%H%M%S")
            default_name = "Registros_{}".format(timestamp)
            inputName = self.utils.get_user_input(
                "Nombre del archivo", "Ingrese el nombre del reporte:", default_name
            )
            if inputName == "":
                return

            filename = os.path.join(filename, "{}.csv".format(inputName))

            def exportData():
                self.recordData.to_csv(filename, encoding='utf-8-sig')

            self.loading_dialog = LoadingDialog("Exportando")
            self.worker = Worker(exportData)
            self.loading_dialog.start(self.worker)
            self.utils.showMessageBox(
                "Reporte generado",
                "El reporte ha sido generado exitosamente",
                QMessageBox.Information,
                QMessageBox.Ok,
            )
        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante la generación del reporte de stock, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error getting outcome records:", e)

    def clearControls(self):
        self.mainWindow.txtRecordStartDate.setText("")
        self.mainWindow.txtRecordEndDate.setText("")
        self.mainWindow.cmbRecordType.setCurrentIndex(0)
        self.mainWindow.txtRecordNumber.setText("")
        self.mainWindow.txtRecordTitle.setText("")
        self.mainWindow.txtRecordObservation.setText("")
        self.mainWindow.txtRecordFolium.setText("")
        self.mainWindow.txtRecordDestination.setText("")

    def clearSearchControls(self):
        self.mainWindow.txtSearchRecordEndDate.setText("")
        self.mainWindow.txtSearchRecordStartDate.setText("")
        self.mainWindow.cmbSearchRecordType.setCurrentIndex(0)
        self.mainWindow.txtSearchRecordNumber.setText("")

    def populateRecordsTable(self, strSQL, params=None):
        try:
            results = self.utils.executeSQL(
                strSQL, "Obteniendo registros...", params)
            # Convertir los resultados a un DataFrame de pandas
            self.recordData = pd.DataFrame(results, columns=[
                'ID', 'Fecha Ingreso', 'Fecha Egreso', 'Tipo', 'Número', 'Título', 'Observación', 'Folio', 'Destinatario', 'Creado por'])

            # AÑADIR COLUMNA DE CHECKBOX
            self.recordTableViewData = self.recordData.copy()
            checkbox_values = self.recordData['ID'] == 0
            select_column = pd.Series(checkbox_values, name='')
            # Insertar la nueva columna al principio del DataFrame
            self.recordTableViewData.insert(
                loc=0, column='Seleccionar', value=select_column)
            self.utils.populateTableViewFromDataFrame(
                self.mainWindow.tableViewRecords, self.recordTableViewData, checkbox_columns=[0])

            # self.utils.adjustCheckboxColumnTableColumnsWidths(
            #    self.mainWindow.tableViewRecords)
            # Aplicar el delegado a la primera columna de la tabla
            delegate = SingleCheckboxDelegate(
                self.mainWindow)
            self.mainWindow.tableViewRecords.setItemDelegateForColumn(
                0, delegate)
            delegate.checkboxToggled.connect(
                self.onRecordCheckboxSelection)

        except Exception as e:
            traceback.print_exc()
            self.utils.showMessageBox(
                "Ha ocurrido un error", "Ocurrió un error inesperado durante la consulta de registros, obtenga más información en los logs de la aplicación", QMessageBox.Critical, QMessageBox.Ok)
            print("Error getting records:", e)

    def onRecordCheckboxSelection(self, row, state):
        if state:
            self.populateControlsFromSelection(row)
        else:
            self.clearControls()

    def populateControlsFromSelection(self, selectedRow):
        data = self.recordData.copy()
        startDate = data.iloc[selectedRow,
                              data.columns.get_loc('Fecha Ingreso')]
        strStartDate = startDate.strftime("%d/%m/%Y")
        endDate = data.iloc[selectedRow, data.columns.get_loc('Fecha Egreso')]
        strEndDate = endDate.strftime("%d/%m/%Y")
        self.selectedId = data.iloc[selectedRow, data.columns.get_loc(
            'ID')]
        self.mainWindow.txtRecordStartDate.setText(strStartDate)
        self.mainWindow.txtRecordEndDate.setText(strEndDate)
        self.mainWindow.cmbRecordType.setCurrentText(
            data.iloc[selectedRow, data.columns.get_loc('Tipo')])
        self.mainWindow.txtRecordNumber.setText(
            data.iloc[selectedRow, data.columns.get_loc('Número')])
        self.mainWindow.txtRecordTitle.setText(
            data.iloc[selectedRow, data.columns.get_loc('Título')])
        self.mainWindow.txtRecordObservation.setText(
            data.iloc[selectedRow, data.columns.get_loc('Observación')])
        self.mainWindow.txtRecordFolium.setText(
            data.iloc[selectedRow, data.columns.get_loc('Folio')])
        self.mainWindow.txtRecordDestination.setText(
            data.iloc[selectedRow, data.columns.get_loc('Destinatario')])
        self.recordCreatedBy = data.iloc[selectedRow,
                                         data.columns.get_loc('Creado por')]

    def getRecordStartDate(self):
        strStartDate = self.utils.show_calendar()
        if not strStartDate:
            return
        self.mainWindow.txtRecordStartDate.setText(strStartDate)

    def getRecordEndDate(self):
        strStartDate = self.utils.show_calendar()
        if not strStartDate:
            return
        self.mainWindow.txtRecordEndDate.setText(strStartDate)

    def getRecordSearchStartDate(self):
        strStartDate = self.utils.show_calendar()
        if not strStartDate:
            return
        self.mainWindow.txtSearchRecordStartDate.setText(strStartDate)

    def getRecordSearchEndDate(self):
        strStartDate = self.utils.show_calendar()
        if not strStartDate:
            return
        self.mainWindow.txtSearchRecordEndDate.setText(strStartDate)
