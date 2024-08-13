import sys
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLineEdit, QCalendarWidget, QDialog, QVBoxLayout
from PyQt5.QtCore import QLocale, QDate
from PyQt5 import QtCore, QtGui, QtWidgets

class CalendarDialog(QDialog):
    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Fecha")
        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale(QLocale.Spanish, QLocale.Spain))
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setStyleSheet("font-family: 'candara'")
        self.calendar.setWindowIcon(icon)        
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        self.setLayout(layout)

    def on_date_selected(self, date):
        self.selected_date = date
        self.accept()