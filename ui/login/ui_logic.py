from ui.loginUi import Ui_login as LoginUIMainWindow
from ui.utils.ui_logic import UtilsUILogic
from PyQt5.QtWidgets import *


class LoginUILogic:
    def __init__(self, mainWindow: LoginUIMainWindow, utils: UtilsUILogic):
        self.mainWindow = mainWindow
        self.utils = utils
        self.connectSignals()

    def connectSignals(self):
        self.mainWindow.btnLogin.clicked.connect(self.check_credentials)

    def check_credentials(self):
        username = self.mainWindow.txtLoginUser.text()
        password = self.mainWindow.txtLoginPassword.text()
        if "" in [username, password]:
            return
        strSQL = "SELECT username FROM sistema_usuarios WHERE username = %s AND password = SHA1(%s) LIMIT 1"
        params = list((username, password))
        results = self.utils.executeSQL(
            strSQL, "Validando credenciales", params)
        if len(results) == 0:
            return self.utils.showMessageBox("Acceso denegado", "Las credenciales ingresadas no se encuentran registradas", QMessageBox.Critical, QMessageBox.Ok)

        self.accepted = True
        self.mainWindow.close()

    def login_successful(self):
        success = getattr(self, 'accepted', False)
        username = self.mainWindow.txtLoginUser.text()

        return {"success": success, "username": username}
