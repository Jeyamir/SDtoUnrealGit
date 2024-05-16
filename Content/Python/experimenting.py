import sys
import threading
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication

class MainWindow(QMainWindow):
    windowClosed = Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setGeometry(100, 100, 600, 400)

    def closeEvent(self, event):
        self.windowClosed.emit()
        print("Closing window...")
        super().closeEvent(event)

class AppThread(QObject):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.thread = None

    def run(self):
        print("Running application...")

        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.window.windowClosed.connect(self.cleanup)
        self.window.show()
        self.app.exec()

    @Slot()
    def cleanup(self):
        print("Cleaning up application...")
        # self.closed.emit()
        # QCoreApplication.quit()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print("Starting thread...")

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()
            print("Stopping thread...")

def run_gui_app():
    global app_thread
    app_thread = AppThread()
    app_thread.closed.connect(start_new_gui_thread)
    app_thread.start()
    print("Running GUI application...")

def start_new_gui_thread():
    global app_thread
    if app_thread:
        app_thread.stop()
    run_gui_app()
    print("Starting new GUI thread...")

if __name__ == "__main__":
    app_thread = None
    start_new_gui_thread()



# from PySide6.QtCore import Slot, Signal
# from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QDialog

# class ChildWnd(QDialog):
#     closed = Signal()
#     def __int__(self):
#         QDialog.__init__(self)

#     @Slot()
#     def closeEvent(self, event):
#         self.closed.emit()
#         super().closeEvent(event)

# class MainWnd(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.centralwidget = QWidget()
#         self.layout = QVBoxLayout()
#         self.button = QPushButton("Show window")
#         self.button.pressed.connect(self.on_button)
#         self.layout.addWidget(self.button)
#         self.label = QLabel()
#         self.layout.addWidget(self.label)
#         self.centralwidget.setLayout(self.layout)
#         self.setCentralWidget(self.centralwidget)
#         self.child_wnd = None

#     @Slot()
#     def on_button(self):
#         self.child_wnd = ChildWnd(self)
#         self.child_wnd.closed.connect(self.on_child_closed)
#         self.label.setText("")
#         self.child_wnd.show()

#     @Slot()
#     def on_child_closed(self):
#         self.label.setText("Window closed")

# def main():
#     app = QApplication()
#     mainwindow = MainWnd()
#     mainwindow.show()
#     app.exec()

# if __name__ == '__main__':
#     main()
