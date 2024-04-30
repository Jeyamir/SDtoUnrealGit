from PipelineSDXL import SDXLPipeline
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget, QMainWindow


class WorkerThread(QThread):
    """A custom QThread class for performing a background task."""
    finished = Signal()
    returnpath = Signal(str, int)  # Define a new signal to emit the result

    def __init__(self, SDXL, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SDXL = SDXL
        self.index = index
        self._is_running = True
    def run(self):
        for i in range(self.index):
            imagepath = self.SDXL.generate_image(i)
            self.returnpath.emit(imagepath, i)
        
        self.finished.emit()
    def stop(self):
        self.exit()