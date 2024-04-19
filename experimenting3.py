from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PIL import Image, ImageQt
import numpy as np
import sys


class PixelRangeConversionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Range Conversion")
        self.setGeometry(100, 100, 600, 400)

        # Widgets
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumSize(400, 400)
        self.input_min_slider = QSlider(Qt.Horizontal)
        self.input_min_slider.setMinimum(0)
        self.input_min_slider.setMaximum(255)
        self.input_min_slider.setValue(0)
        self.input_min_slider.valueChanged.connect(self.update_image)

        self.input_max_slider = QSlider(Qt.Horizontal)
        self.input_max_slider.setMinimum(0)
        self.input_max_slider.setMaximum(255)
        self.input_max_slider.setValue(255)
        self.input_max_slider.valueChanged.connect(self.update_image)

        self.output_min_slider = QSlider(Qt.Horizontal)
        self.output_min_slider.setMinimum(0)
        self.output_min_slider.setMaximum(255)
        self.output_min_slider.setValue(0)
        self.output_min_slider.valueChanged.connect(self.update_image)

        self.output_max_slider = QSlider(Qt.Horizontal)
        self.output_max_slider.setMinimum(0)
        self.output_max_slider.setMaximum(255)
        self.output_max_slider.setValue(255)
        self.output_max_slider.valueChanged.connect(self.update_image)

        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.upload_image)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Input Range"))
        layout.addWidget(self.input_min_slider)
        layout.addWidget(self.input_max_slider)
        layout.addWidget(QLabel("Output Range"))
        layout.addWidget(self.output_min_slider)
        layout.addWidget(self.output_max_slider)
        layout.addWidget(self.upload_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.image = None

    def update_image(self):
        if self.image:
            self.input_min = self.input_min_slider.value()
            self.input_max = self.input_max_slider.value()
            self.output_min = self.output_min_slider.value()
            self.output_max = self.output_max_slider.value()
            converted_image = self.image.point(self.convert_pixel_range)
            self.display_image(converted_image)

    def convert_pixel_range(self, pixel_value):
        # Get the dimensions of the image
        # width, height = image.size
        
        # # Create a new empty image with the same size and mode
        # converted_image = Image.new(image.mode, (width, height))
        
        # # Iterate over each pixel
        # for y in range(height):
        #     for x in range(width):
        #         # Get the pixel value at (x, y)
        #         pixel = image.getpixel((x, y))
                
        #         # Check if the pixel value is within the input range
        #         if input_min <= pixel <= input_max:
        #             # Perform the conversion for pixels in the input range
        #             input_range = input_max - input_min
        #             output_range = output_max - output_min
        #             scaled_pixel = int((pixel - input_min) * (output_range / input_range) + output_min)
        #             # Set the converted pixel value in the new image
        #             converted_image.putpixel((x, y), scaled_pixel)
        #         else:
        #             # For pixels outside the input range, keep the original value
        #             converted_image.putpixel((x, y), pixel)
        
        # return converted_image
        if self.input_min <= pixel_value <= self.input_max:
            # Perform the conversion for pixels in the input range
            input_range = self.input_max - self.input_min
            output_range = self.output_max - self.output_min
            scaled_pixel = int((pixel_value - self.input_min) * (output_range / input_range) + self.output_min)
            return scaled_pixel
        else:
            return pixel_value

    def display_image(self, image):
        q_image = ImageQt.ImageQt(image)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.load_image(file_path)

    def load_image(self, file_path):
        self.image = Image.open(file_path)
        if self.image.mode != 'L':
            self.image = self.image.convert('L')
        self.display_image(self.image)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixelRangeConversionApp()
    window.show()
    sys.exit(app.exec())
