from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QSlider, QLineEdit, QApplication, QTabWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PIL import Image, ImageQt
from utils_PIL import adjust_contrast
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contrast Adjustment")
        self.setGeometry(100, 100, 400, 400)

        # Widgets
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)

        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.select_image)

        self.min_color_slider = QSlider(Qt.Horizontal)
        self.min_color_slider.setMinimum(0)
        self.min_color_slider.setMaximum(255)
        self.min_color_slider.setValue(0)

        self.max_color_slider = QSlider(Qt.Horizontal)
        self.max_color_slider.setMinimum(0)
        self.max_color_slider.setMaximum(255)
        self.max_color_slider.setValue(255)

        self.contrast_factor_edit = QLineEdit()
        self.contrast_factor_edit.setText("1.5")

        self.apply_button = QPushButton("Apply Contrast")
        self.apply_button.clicked.connect(self.apply_contrast)

        self.tab_widget = QTabWidget()
        self.local_contrast_tab = QWidget()
        self.contrast_stretch_tab = QWidget()

        # Layout for settings tab
        settings_layout = QVBoxLayout(self.local_contrast_tab)
        settings_layout.addWidget(QLabel("Min Color"))
        settings_layout.addWidget(self.min_color_slider)
        settings_layout.addWidget(QLabel("Max Color"))
        settings_layout.addWidget(self.max_color_slider)
        settings_layout.addWidget(QLabel("Contrast Factor"))
        settings_layout.addWidget(self.contrast_factor_edit)
        settings_layout.addWidget(self.apply_button)

        # Add tabs to tab widget
        self.tab_widget.addTab(self.local_contrast_tab, "Local Contrast")
        self.tab_widget.addTab(self.contrast_stretch_tab, "Contrast Stretching")

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.tab_widget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.image = None

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.image = Image.open(file_path)
            self.display_image()

    def display_image(self):
        q_image = ImageQt.ImageQt(self.image)
        self.image_label.setMaximumHeight(400)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def apply_contrast(self):
        if self.image:
            min_color = self.min_color_slider.value()
            max_color = self.max_color_slider.value()
            contrast_factor = float(self.contrast_factor_edit.text())

            adjusted_image = adjust_contrast(self.image, min_color, max_color, contrast_factor)
            q_image = ImageQt.ImageQt(adjusted_image)

            self.image_label.setPixmap(QPixmap.fromImage(q_image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
