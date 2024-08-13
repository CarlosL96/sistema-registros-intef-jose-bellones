from PyQt5 import QtWidgets, QtCore, QtGui

class LoadingDialog(QtWidgets.QDialog):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("background-color:white;")
        self.setWindowTitle(title)
        self.setFixedSize(300, 200)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        self.label = QtWidgets.QLabel("Ejecutando proceso...")
        self.label.setStyleSheet("color: #827E7E; font-family:'candara'; font-size:20pt;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)        
        self.gif_label = QtWidgets.QLabel()               
        #self.gif_label.setStyleSheet("background-color: red")
        self.gif_label.setAlignment(QtCore.Qt.AlignCenter)
        self.movie = QtGui.QMovie("icons/loading.gif")        
        self.gif_label.setMovie(self.movie)
        layout.addWidget(self.gif_label)        
        self.movie.start()

    def start(self, worker):
        self.worker = worker
        self.worker.finished.connect(self.accept)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        self.exec_()
    
    
    def show_error(self, error_message):
        QtWidgets.QMessageBox.critical(self, "Error", error_message)
        self.reject()
        
        

class Worker(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)  # Señal de error que lleva un mensaje de error

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.error.emit(str(e))  # Emitir la señal de error con el mensaje de la excepción
        else:
            self.finished.emit()