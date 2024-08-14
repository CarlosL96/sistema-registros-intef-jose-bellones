import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.loginUi import Ui_login as LoginUI
from ui.mainUi import Ui_MainWindow
from ui.utils.ui_logic import UtilsUILogic
from ui.login.ui_logic import LoginUILogic
from ui.records.ui_logic import RecordsUILogic


class LoginApp(QMainWindow, LoginUI):
    def __init__(self):
        super(LoginApp, self).__init__()
        self.setupUi(self)
        self.icon = self.windowIcon()
        self.utils = UtilsUILogic(self, self.icon)
        self.loginLogic = LoginUILogic(self, self.utils)


class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self, utils):
        super(MainApp, self).__init__()
        self.setupUi(self)
        self.utils = utils        
        self.utils.updateUI(self)
        self.close_requested_by_ui = False
        self.icon = self.windowIcon()
        self.reportsLogic = RecordsUILogic(self, self.utils)

    def closeEvent(self, event):
        event.accept()
        return
        if self.close_requested_by_ui:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    # Mostrar la ventana de login primero
    login_window = LoginApp()
    login_window.show()
    # Ejecutar el evento de la aplicación para manejar el login
    app.exec_()
    # Si el login fue exitoso, mostrar la ventana principal
    loginInfo = login_window.loginLogic.login_successful()
    if loginInfo["success"]:
        login_window.utils.loginInfo = loginInfo
        window = MainApp(login_window.utils)
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
