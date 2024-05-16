import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
from PySide6.QtGui import QPixmap, QFont
from PIL.ImageQt import ImageQt
from module_color_to_normals import apply as apply_normals
from module_normals_to_height import apply as apply_height
from PIL import Image
import numpy as np
from utils_image import display_image, numpy_to_PIL


class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Processor")
        self.setGeometry(100, 100, 400, 200)

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)

        self.normal_label = QLabel(self)
        self.normal_label.setScaledContents(True)

        self.height_label = QLabel(self)
        self.height_label.setScaledContents(True)

        self.load_button = QPushButton("Load Image", self)
        self.load_button.clicked.connect(self.load_image)

        self.generate_normal_button = QPushButton("Generate Normal Map", self)
        self.generate_normal_button.clicked.connect(self.generate_normal_map)

        self.generate_height_button = QPushButton("Generate Height Map", self)
        self.generate_height_button.clicked.connect(self.generate_height_map)

        self.save_normal_button = QPushButton("Save Normal Map", self)
        self.save_normal_button.clicked.connect(self.save_normal)

        self.save_height_button = QPushButton("Save Height Map", self)
        self.save_height_button.clicked.connect(self.save_height)

        layout = QVBoxLayout()
        imagelayout = QHBoxLayout()
        imagelayout.addWidget(self.image_label)
        imagelayout.addWidget(self.normal_label)
        imagelayout.addWidget(self.height_label)
        layout.addLayout(imagelayout)
        layout.addWidget(self.load_button)
        layout.addWidget(self.generate_normal_button)
        layout.addWidget(self.generate_height_button)
        layout.addWidget(self.save_normal_button)
        layout.addWidget(self.save_height_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_np = None

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setDirectory('.')
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            image = self.load_image_as_numpy(file_path)
            self.numpy_img = image
            display_image(image, self.image_label)

    def generate_normal_map(self):
        if self.numpy_img is not None:
            self.numpy_normal = apply_normals(self.numpy_img, "SMALL", None)
            display_image(self.numpy_normal, self.normal_label)

    def generate_height_map(self):
        if self.numpy_normal is not None:
            self.numpy_height = apply_height(self.numpy_normal, "SMALL", None)
            display_image(self.numpy_height, self.height_label)

    def save_normal(self):
        if self.numpy_normal is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Normal Map", ".", "Images (*.png *.jpg *.bmp)")
            if file_path:
                output_image = numpy_to_PIL(self.numpy_normal)
                output_image.save(file_path)

    def save_height(self):
        if self.numpy_height is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Height Map", ".", "Images (*.png *.jpg *.bmp)")
            if file_path:
                output_image = numpy_to_PIL(self.numpy_height)
                output_image.save(file_path)
    
    def load_image_as_numpy(self, image_path):
        try:
            # Load the image
            image = Image.open(image_path)
            # Convert to RGB
            image = image.convert('RGB')
            # Convert to numpy array
            image_np = np.array(image)
            # Normalize the pixel values from [0, 255] to [0, 1]
            image_np = image_np.astype(np.float32) / 255.0
            # Rearrange the dimensions to C, H, W
            image_np = np.transpose(image_np, (2, 0, 1))
            return image_np
        except IOError:
            print(f"Error opening or reading image file {image_path}")
            return None

    # def RGBA_numpy_to_PIL(self, numpy_image):
    #     # Check if the numpy image is in the format C, H, W and if it is normalized between [0, 1]
    #     if numpy_image.ndim == 3 and numpy_image.shape[0] in [1, 3, 4]:  # Assuming grayscale or RGB/RGBA
    #         # Convert C, H, W to H, W, C
    #         numpy_image = np.transpose(numpy_image, (1, 2, 0))
    #     else:
    #         raise ValueError("Input array must have shape (C, H, W) and C should be 1, 3, or 4")

    #     # Check if the image data is already in the expected range [0, 1] and type is float
    #     if numpy_image.dtype != np.float32 and numpy_image.dtype != np.float64:
    #         raise TypeError("Image data type should be float32 or float64 for normalization.")

    #     # Scale from [0, 1] to [0, 255]
    #     numpy_image = (numpy_image * 255).clip(0, 255).astype(np.uint8)
        
    #     # Create and return the PIL Image
    #     image_pil = Image.fromarray(numpy_image)

    #     return image_pil
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())