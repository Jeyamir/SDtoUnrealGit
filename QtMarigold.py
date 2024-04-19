import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QCheckBox, QSpinBox
from PySide6.QtGui import QPixmap
from PIL import Image
from diffusers import DiffusionPipeline
import numpy as np
import torch


class MarigoldWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Diffusion Pipeline Controller")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(50, 50, 300, 300)

        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.setGeometry(50, 400, 150, 30)
        self.upload_button.clicked.connect(self.upload_image)

        self.match_input_resolution_checkbox = QCheckBox("Match Input Resolution", self)
        self.match_input_resolution_checkbox.setGeometry(50, 450, 200, 30)

        self.seed_spinbox = QSpinBox(self)
        self.seed_spinbox.setGeometry(50, 500, 100, 30)
        self.seed_spinbox.setMinimum(0)
        self.seed_spinbox.setMaximum(9999)
        self.seed_spinbox.setValue(2024)

        self.denoising_steps_spinbox = QSpinBox(self)
        self.denoising_steps_spinbox.setGeometry(250, 450, 100, 30)
        self.denoising_steps_spinbox.setMinimum(1)
        self.denoising_steps_spinbox.setMaximum(20)
        self.denoising_steps_spinbox.setValue(10)

        self.ensemble_steps_spinbox = QSpinBox(self)
        self.ensemble_steps_spinbox.setGeometry(250, 500, 100, 30)
        self.ensemble_steps_spinbox.setMinimum(1)
        self.ensemble_steps_spinbox.setMaximum(20)
        self.ensemble_steps_spinbox.setValue(10)

        self.process_button = QPushButton("Process", self)
        self.process_button.setGeometry(50, 550, 100, 30)
        self.process_button.clicked.connect(self.process_image)

        self.pipeline = None
        self.image_path = None

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg)")
        if file_dialog.exec_():
            self.image_path = file_dialog.selectedFiles()[0]
            pixmap = QPixmap(self.image_path)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)

    def process_image(self):
        if self.image_path:
            # Load the image
            image = Image.open(self.image_path)

            # Prepare pipeline
            if not self.pipeline:
                self.pipeline = DiffusionPipeline.from_pretrained(
                    "prs-eth/marigold-v1-0",
                    custom_pipeline="marigold_depth_estimation",
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                self.pipeline.to("cuda")

            # Process image with pipeline
            pipeline_output = self.pipeline(
                image,
                denoising_steps=self.denoising_steps_spinbox.value(),
                ensemble_size=self.ensemble_steps_spinbox.value(),
                match_input_res=self.match_input_resolution_checkbox.isChecked()
            )


            depth: np.ndarray = pipeline_output.depth_np                    # Predicted depth map
            depth_colored: Image.Image = pipeline_output.depth_colored      # Colorized prediction
            # Display processed image (depth map)
            # Save as uint16 PNG
            depth_uint16 = (depth * 65535.0).astype(np.uint16)
            Image.fromarray(depth_uint16).save("./depth_map.png", mode="I;16")
            # Save colorized depth map
            depth_colored.save("./depth_colored.png")
            depth_colored.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarigoldWindow()
    window.show()
    sys.exit(app.exec())
