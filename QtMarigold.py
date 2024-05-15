import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QCheckBox, QSpinBox, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtGui import QPixmap
from PIL import Image
from utils_Qt import addFormRow, upload_image, save_image
from diffusers import DiffusionPipeline
from PIL.ImageQt import ImageQt
from utils_image import calculate_normal_map, load_image, display_image, numpy_to_PIL
import numpy as np
import torch


class MarigoldWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Diffusion Pipeline Controller")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.image_label.setGeometry(50, 50, 300, 300)
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumSize(300, 300)
        
        self.height_image_label = QLabel(self)
        self.height_image_label.setGeometry(50, 50, 300, 300)
        self.height_image_label.setScaledContents(True)
        self.height_image_label.setMaximumSize(300, 300)

        self.normal_image_label = QLabel(self)
        self.normal_image_label.setGeometry(50, 50, 300, 300)
        self.normal_image_label.setScaledContents(True)
        self.normal_image_label.setMaximumSize(300, 300)

        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.setGeometry(50, 400, 150, 30)
        self.upload_button.clicked.connect(self.upload_image)

        self.match_input_resolution_checkbox = QCheckBox("Match Input Resolution", self)
        self.match_input_resolution_checkbox.setGeometry(50, 450, 200, 30)
        self.match_input_resolution_checkbox.setChecked(True)



        self.denoising_steps_spinbox = QSpinBox(self)
        self.denoising_steps_spinbox.setGeometry(250, 450, 100, 30)
        self.denoising_steps_spinbox.setMinimum(1)
        self.denoising_steps_spinbox.setMaximum(20)
        self.denoising_steps_spinbox.setValue(4)

        self.ensemble_steps_spinbox = QSpinBox(self)
        self.ensemble_steps_spinbox.setGeometry(250, 500, 100, 30)
        self.ensemble_steps_spinbox.setMinimum(1)
        self.ensemble_steps_spinbox.setMaximum(20)
        self.ensemble_steps_spinbox.setValue(5)

        self.generate_normal_button = QPushButton("Generate Normal Map", self)
        self.generate_normal_button.clicked.connect(self.generate_normal_map)

        self.process_button = QPushButton("Process", self)
        self.process_button.setGeometry(50, 550, 100, 30)
        self.process_button.clicked.connect(self.process_image)

        self.save_height_button = QPushButton("Save Height Map", self)
        self.save_height_button.setGeometry(200, 550, 100, 30)
        self.save_height_button.clicked.connect(self.save_height)

        self.save_normal_button = QPushButton("Save Normal Map", self)
        self.save_normal_button.setGeometry(200, 550, 100, 30)
        self.save_normal_button.clicked.connect(self.save_normal)


        #-------------------------------------------------------FORMATTING------------------------------------------------------------
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        image_layout = QHBoxLayout()

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.height_image_label)
        image_layout.addWidget(self.normal_image_label)
        layout.addLayout(image_layout)
        layout.addWidget(self.upload_button)
        addFormRow(layout, "Denoising Steps:", self.denoising_steps_spinbox)
        addFormRow(layout, "Ensemble Steps:", self.ensemble_steps_spinbox)
        layout.addWidget(self.match_input_resolution_checkbox)
        layout.addWidget(self.process_button)
        layout.addWidget(self.generate_normal_button)
        layout.addWidget(self.save_height_button)
        layout.addWidget(self.save_normal_button)


        self.pipeline = None
        self.image_path = None

    def upload_image(self):
        file_path = upload_image(self)
        load_image(file_path, self.image_label)
        self.image_path = file_path
    
    def process_image(self):
        if self.image_path:
            # Load the image
            image = Image.open(self.image_path)

            # Prepare pipeline
            if not self.pipeline:
                self.pipeline = DiffusionPipeline.from_pretrained(
                    "prs-eth/marigold-lcm-v1-0",
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
                match_input_res=self.match_input_resolution_checkbox.isChecked(),
            )


            self.depthImage: np.ndarray = pipeline_output.depth_np                    # Predicted depth map
            # Display processed image (depth map)
            
            # load depth map label
            display_image(self.depthImage, self.height_image_label)
    
    def generate_normal_map(self):
        self.normalMap = calculate_normal_map(self.depthImage)
        display_image(self.normalMap, self.normal_image_label)

    def save_normal(self):
        save_image(numpy_to_PIL(self.depthImage), self)

    def save_height(self): 
        save_image(numpy_to_PIL(self.normalMap), self)   
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarigoldWindow()
    window.show()
    sys.exit(app.exec())
