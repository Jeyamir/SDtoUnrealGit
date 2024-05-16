import sys
from PySide6 import QtWidgets, QtCore

class Window(QtWidgets.QMainWindow):
    """PySide6 app that closes successfully in Spyder."""
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 400, 300)
        self.initUI()

    def initUI(self):
        btn = QtWidgets.QPushButton('Quit', self)
        btn.setGeometry(150, 125, 100, 50)
        btn.clicked.connect(self.close)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', 'Are you sure you want to quit?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            QtWidgets.QApplication.quit()
        else:
            event.ignore()

def run_app():
    global app
    if QtWidgets.QApplication.instance() is None:
        app = QtWidgets.QApplication(sys.argv)
        app.aboutToQuit.connect(app.deleteLater)
    else:
        app = QtWidgets.QApplication.instance()
    
    win = Window()
    win.show()
    app.exec()

if __name__ == '__main__':
    run_app()
