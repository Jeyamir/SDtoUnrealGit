from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget, QMainWindow
import time

class Task:
    """A class that performs a specific task."""
    def __init__(self, update_callback):
        self.update_callback = update_callback

    def run(self):
        """Long-running task."""
        for i in range(5):
            time.sleep(1)
            self.update_callback(i + 1)

class TaskThread(QThread):
    """A QThread subclass to manage the task execution."""
    finished = Signal()
    progress = Signal(int)

    def __init__(self, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task

    def run(self):
        # Define a callback to update progress
        def progress_callback(step):
            self.progress.emit(step)
        
        # Set the callback and run the task
        self.task.update_callback = progress_callback
        self.task.run()
        
        # Emit finished signal after task completion
        self.finished.emit()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Task Manager")

        # Create layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Create a button to start the task
        self.task_button = QPushButton("Start Task")
        self.task_button.clicked.connect(self.start_task)
        layout.addWidget(self.task_button)

        # Create a label to show progress
        self.progress_label = QLabel("Progress: 0")
        layout.addWidget(self.progress_label)

    def start_task(self):
        # Step 2: Create a Task instance
        task = Task(self.update_progress)

        # Step 3: Create a TaskThread instance
        self.worker = TaskThread(task)

        # Connect signals and slots
        self.worker.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(lambda: self.task_button.setEnabled(True))
        self.worker.finished.connect(lambda: self.progress_label.setText("Progress: 0"))

        # Step 6: Start the thread
        self.worker.start()

        # Disable button while task is running
        self.task_button.setEnabled(False)

    def update_progress(self, step):
        """Updates the progress label."""
        self.progress_label.setText(f"Progress: {step}")

if __name__ == "__main__":
    app = QApplication([])

    window = Window()
    window.show()

    app.exec_()
