import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.clahe = cv2.createCLAHE(clipLimit=0.1, tileGridSize=(8, 8))  # Decreased clipLimit for reduced contrast
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("CLAHE Image Processor")
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.upload_image)
        
        self.clip_limit_slider = QSlider(Qt.Horizontal)
        self.clip_limit_slider.setMinimum(1)
        self.clip_limit_slider.setMaximum(100)
        self.clip_limit_slider.setValue(10)  # Decreased initial value for clipLimit
        self.clip_limit_slider.valueChanged.connect(self.update_image)
        
        self.tile_grid_size_slider = QSlider(Qt.Horizontal)
        self.tile_grid_size_slider.setMinimum(2)
        self.tile_grid_size_slider.setMaximum(20)
        self.tile_grid_size_slider.setValue(8)
        self.tile_grid_size_slider.valueChanged.connect(self.update_image)
        
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Clip Limit"))
        layout.addWidget(self.clip_limit_slider)
        layout.addWidget(QLabel("Tile Grid Size"))
        layout.addWidget(self.tile_grid_size_slider)
        
        self.setLayout(layout)
        
    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                image_path = file_paths[0]
                self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if self.image is not None:
                    self.update_image()
                else:
                    print("Failed to load the image.")
        
    def update_image(self):
        if self.image is None:
            return
        
        clip_limit = self.clip_limit_slider.value() / 10.0  # Scale clipLimit to be between 0 and 1
        tile_grid_size = (self.tile_grid_size_slider.value(), self.tile_grid_size_slider.value())
        
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        equalized_image = self.clahe.apply(self.image)
        if equalized_image is None:
            print("CLAHE operation failed.")
            return
        
        height, width = equalized_image.shape
        bytes_per_line = width
        
        q_image = QImage(equalized_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
