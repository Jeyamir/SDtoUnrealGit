import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from image_utils import load_image, save_image, calculate_occlusion
from utils_Qt import upload_image, save_image

class OcclusionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Height Map to Occlusion Conversion")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumSize(800, 600)

        self.upload_button = QPushButton("Upload Height Map")
        self.upload_button.clicked.connect(self.upload_image)

        self.save_button = QPushButton("Save Occlusion Map")
        self.save_button.clicked.connect(self.save_occlusion_image)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.height_map = None
        self.occlusion_map = None

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Height Map", ".", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.height_map = load_image(file_path, is_uint16=False)
            self.image_label.setPixmap(QPixmap.fromImage(self.height_map))
            self.occlusion_map = calculate_occlusion(self.height_map, radius=5, invert=False)
            self.display_image(self.occlusion_map)


    def display_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def save_occlusion_image(self):
        if self.occlusion_map:
            save_image(self.occlusion_map, self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OcclusionApp()
    window.show()
    sys.exit(app.exec())
