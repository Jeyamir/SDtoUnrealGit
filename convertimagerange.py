from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PIL import Image, ImageQt, ImageOps

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

        self.invert_checkbox = QCheckBox("Invert Image")
        self.invert_checkbox.stateChanged.connect(self.invert_image)
        self.uint_checkbox = QCheckBox("Load from UInt16")

        self.input_min_slider = QSlider(Qt.Horizontal)
        self.input_min_slider.setMinimum(0)
        self.input_min_slider.setMaximum(255)
        self.input_min_slider.setValue(0)
        self.input_min_slider.valueChanged.connect(self.transform_image)

        self.input_max_slider = QSlider(Qt.Horizontal)
        self.input_max_slider.setMinimum(0)
        self.input_max_slider.setMaximum(255)
        self.input_max_slider.setValue(255)
        self.input_max_slider.valueChanged.connect(self.transform_image)

        self.output_min_slider = QSlider(Qt.Horizontal)
        self.output_min_slider.setMinimum(0)
        self.output_min_slider.setMaximum(255)
        self.output_min_slider.setValue(0)
        self.output_min_slider.valueChanged.connect(self.transform_image)

        self.output_max_slider = QSlider(Qt.Horizontal)
        self.output_max_slider.setMinimum(0)
        self.output_max_slider.setMaximum(255)
        self.output_max_slider.setValue(255)
        self.output_max_slider.valueChanged.connect(self.transform_image)

        self.shift_range_min_slider = QSlider(Qt.Horizontal)
        self.shift_range_min_slider.setMinimum(0)
        self.shift_range_min_slider.setMaximum(255)
        self.shift_range_min_slider.setValue(0)
        self.shift_range_min_slider.valueChanged.connect(self.shift_image)

        self.shift_range_max_slider = QSlider(Qt.Horizontal)
        self.shift_range_max_slider.setMinimum(0)
        self.shift_range_max_slider.setMaximum(255)
        self.shift_range_max_slider.setValue(255)
        self.shift_range_max_slider.valueChanged.connect(self.shift_image)

        self.shift_value_slider = QSlider(Qt.Horizontal)
        self.shift_value_slider.setMinimum(-255)
        self.shift_value_slider.setMaximum(255)
        self.shift_value_slider.setValue(0)
        self.shift_value_slider.valueChanged.connect(self.shift_image)

        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.upload_image)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)


        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.invert_checkbox)
        layout.addWidget(self.uint_checkbox)
        layout.addWidget(QLabel("Input Range"))
        layout.addWidget(self.input_min_slider)
        layout.addWidget(self.input_max_slider)
        layout.addWidget(QLabel("Output Range"))
        layout.addWidget(self.output_min_slider)
        layout.addWidget(self.output_max_slider)
        layout.addWidget(QLabel("Shift Range"))
        layout.addWidget(self.shift_range_min_slider)
        layout.addWidget(self.shift_range_max_slider)
        layout.addWidget(QLabel("Shift Value"))
        layout.addWidget(self.shift_value_slider)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.image = None

    def transform_image(self):
        if self.image:
            self.input_min = self.input_min_slider.value()
            self.input_max = self.input_max_slider.value()
            self.output_min = self.output_min_slider.value()
            self.output_max = self.output_max_slider.value()
            self.converted_image = self.image.point(self.convert_pixel_range)
            self.display_image(self.converted_image)

    def shift_image(self):
        if self.image:
            self.shift_range_max = self.shift_range_max_slider.value()
            self.shift_range_min = self.shift_range_min_slider.value()
            self.shift_value = self.shift_value_slider.value()
            self.converted_image = self.image.point(self.shift_pixel_range)
            self.display_image(self.converted_image)


    def convert_pixel_range(self, pixel_value):
        if self.input_min <= pixel_value <= self.input_max:
            # Perform the conversion for pixels in the input range
            input_range = self.input_max - self.input_min
            output_range = self.output_max - self.output_min
            scaled_pixel = int((pixel_value - self.input_min) * (output_range / input_range) + self.output_min)
            return scaled_pixel
        else:
            return pixel_value
        
    def shift_pixel_range(self, pixel_value):
        if self.shift_range_min <= pixel_value <= self.shift_range_max:
            return pixel_value + self.shift_value
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
        if self.uint_checkbox.isChecked():
            # Scale down the pixel values from uint16 to uint8
            self.image = self.image.convert('I').point(lambda x: x * (1.0 / 256)).convert('L')

        if self.image.mode != 'L':
            self.image = self.image.convert('L')
        self.display_image(self.image)
    
    def invert_image(self):
        if self.image:
            self.image = ImageOps.invert(self.image)
            self.display_image(self.image)

    def save_image(self):
        if self.image:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", ".", "Images (*.png *.jpg *.bmp)")
            if file_path:
                self.converted_image.save(file_path)


        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixelRangeConversionApp()
    window.show()
    sys.exit(app.exec())
