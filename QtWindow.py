import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget,  QPushButton, QLineEdit, QVBoxLayout,QHBoxLayout, QWidget, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget, QFileDialog, QComboBox, QSpinBox, QSlider, QCheckBox, QDoubleSpinBox
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QSettings, Qt, Slot, QThread
from random import randint
from PipelineSDXL import SDXLPipeline
# from QtAdapters import AdapterWindow
from QtDeepBump import ImageProcessor
from utils_Qt import addFormRow
from QtThread import WorkerThread
from QtMarigold import MarigoldWindow
from convertimagerange import PixelRangeConversionApp
from QtThread import WorkerThread

class MainWindow(QMainWindow):
    def __init__(self, model = None):
        super().__init__()
        self.resize(500, 500)
        self.setWindowTitle("Stable Diffusion Material Generator for Unreal")


        # QT Window Tab Widget
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        # Create instances of the menus
        self.firstMenu = SetupMenu()
        self.secondMenu = StableDiffusionMenu()
        # self.thirdMenu = AdapterWindow()
        self.fourthMenu = ImageProcessor()
        self.fifthMenu = MarigoldWindow()
        self.sixthMenu = PixelRangeConversionApp()

        # Add tab names
        self.tabWidget.addTab(self.firstMenu, "Setup")
        self.tabWidget.addTab(self.secondMenu, "SDXL")
        # self.tabWidget.addTab(self.thirdMenu, "Adapters")
        self.tabWidget.addTab(self.fourthMenu, "DeepBump")
        self.tabWidget.addTab(self.fifthMenu, "Marigold")
        self.tabWidget.addTab(self.sixthMenu, "Pixel Range Conversion")
          

class SetupMenu(QWidget):
    def __init__(self):
        super().__init__()
        buttonstyle = """
        QPushButton {
            background-color: #007bff;
            color: white;
            font-weight: bold;
            padding: 16px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
    """
        # Central widget and layout
        layout = QVBoxLayout(self)
        #save location info label
        self.savelocationlabel = QLabel("Save Location")
        #save location explicit label
        self.Esavelocationlabel = QLabel("/")
        #save location button
        self.savelocationbutton = QPushButton("Select Save Location")
        self.savelocationbutton.clicked.connect(self.select_file)
        self.savelocationbutton.setStyleSheet(buttonstyle)

        layout.addWidget(self.savelocationlabel)
        layout.addWidget(self.Esavelocationlabel)
        layout.addWidget(self.savelocationbutton)
        layout.addStretch()
        self.load_settings()

    def load_settings(self):
        self.settings = QSettings("Ashill", "SDtoUnreal")
        last_used_file = self.settings.value("savelocation", "")
        if isinstance(last_used_file, str):
            self.Esavelocationlabel.setText(last_used_file)

    def save_settings(self, file_path):
        self.settings.setValue("lastUsedFile", file_path)

    @Slot()
    def select_file(self):
        options = QFileDialog.Options()
        folderName = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)
        if folderName:
            self.save_settings(folderName)
            self.Esavelocationlabel.setText(folderName)



class StableDiffusionMenu(QWidget):
    def __init__(self):
        super().__init__()
        buttonstyle = """
        QPushButton {
            background-color: #007bff;
            color: white;
            font-weight: bold;
            padding: 16px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
    """        
        self.SDXL = SDXLPipeline()

        # Central widget and layout
        self.layout = QVBoxLayout(self)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.5)  # Set the opacity here (0.0 to 1.0)
        # Dropdown menu for Scheduler
        self.schedulerComboBox = QComboBox(self)
        self.schedulerComboBox.currentIndexChanged.connect(self.setScheduler)


        # Inference Steps Spin Box
        self.inferenceStepsSpinBox = QSpinBox()
        self.inferenceStepsSpinBox.setMinimum(1)  # Set minimum value
        self.inferenceStepsSpinBox.setSingleStep(1) # Set step size
        self.inferenceStepsSpinBox.setValue(30)  
        self.inferenceStepsSpinBoxLabel = QLabel("Inference Steps")

        # Create the Denoising Fraction slider
        self.denoisingFractionSlider = QSlider(Qt.Horizontal)
        self.denoisingFractionSlider.setMinimum(1) 
        self.denoisingFractionSlider.setMaximum(100)  
        self.denoisingFractionSlider.setValue(80)    
        self.denoisingFractionSlider.setEnabled(False)
        # Label for the denoising fraction
        self.FractionLabel = QLabel("Refiner Starts at:")
        self.denoisingFractionLabel = QLabel(".8")
        self.denoisingFractionLabel.setAlignment(Qt.AlignCenter)

        # CFG Spin Box
        self.guidanceScaleSpinBox = QDoubleSpinBox()
        self.guidanceScaleSpinBox.setMinimum(0)  # Set minimum value
        self.guidanceScaleSpinBoxLabel = QLabel("Guidance Scale (CFG)")
        self.guidanceScaleSpinBox.setValue(5.0)  

        # Random Seed Spin Box
        self.seedSpinBox = QSpinBox()
        self.seedSpinBox.setMinimum(1)  # Set minimum value
        self.seedSpinBox.setMaximum(999999)
        self.seedSpinBox.setValue(0)  
        self.seedSpinBox.setEnabled(False)
        self.seedCheckBox = QCheckBox()
        self.seedCheckBox.stateChanged.connect(self.seedSpinBox.setEnabled)


        # Create QLineEdit and QLabel for Prompt1
        self.prompt1Label = QLabel("Prompt1")
        self.prompt1LineEdit = QLineEdit()
        self.prompt1LineEdit.setText("texture, prompt, top down close-up")
        # Create QLineEdit and QLabel for Negative Prompt1
        self.negativePrompt1LineEdit = QLineEdit()
        self.negativePrompt1LineEdit.setText("ugly, deformed, noisy, blurry, unrealistic, shadows")



        # Create the height slider
        
        self.heightSlider = QSlider(Qt.Horizontal)
        self.heightSlider.setMinimum(768) 
        self.heightSlider.setMaximum(2048)  
        self.heightSlider.setValue(1024)    
        # Create the height Spin Box
        self.heightSpinBox = QSpinBox()
        self.heightSpinBox.setMinimumWidth(100)
        self.heightSpinBox.setMinimum(768)
        self.heightSpinBox.setMaximum(2048)
        self.heightSpinBox.setValue(1024)  
        self.heightSlider.valueChanged.connect(self.heightSpinBox.setValue)
        self.heightSpinBox.valueChanged.connect(self.heightSlider.setValue)
        self.heightLayout = QHBoxLayout()
        self.heightLayout.addWidget(self.heightSlider)
        self.heightLayout.addWidget(self.heightSpinBox)
        # Label for the height slider
        self.heightLabel = QLabel("Height")
        

        # Create the width slider
        self.widthSlider = QSlider(Qt.Horizontal)
        self.widthSlider.setMinimum(768) 
        self.widthSlider.setMaximum(2048)  
        self.widthSlider.setValue(1024)    
        # Create the width Spin Box
        self.widthSpinBox = QSpinBox()
        self.widthSpinBox.setMinimumWidth(100)
        self.widthSpinBox.setMinimum(768)
        self.widthSpinBox.setMaximum(2048)
        self.widthSpinBox.stepBy(16)
        self.widthSpinBox.setValue(1024)  
        self.widthSlider.valueChanged.connect(self.widthSpinBox.setValue)
        self.widthSpinBox.valueChanged.connect(self.widthSlider.setValue)
        self.widthLayout = QHBoxLayout()
        self.widthLayout.addWidget(self.widthSlider)
        self.widthLayout.addWidget(self.widthSpinBox)
        # Label for the width slider
        self.widthLabel = QLabel("Width")

        # number of images
        self.batchSpinBox = QSpinBox()
        self.batchSpinBox.setMinimum(1) 

        # Button to generate output
        self.generateButton = QPushButton("Generate", self)
        self.generateButton.clicked.connect(self.generateClicked)
        self.generateButton.setStyleSheet(buttonstyle)

        #checkbox for refiner
        self.refinerCheckBox = QCheckBox()
        self.refinerCheckBox.setText("Refiner")
        self.refinerCheckBox.stateChanged.connect(self.setRefiner)
        self.refinerCheckBox.setChecked(False)
        self.refinerCheckBox.stateChanged.connect(self.denoisingFractionSlider.setEnabled)

        # Labels for displaying the image
        self.imageLabels = [QLabel(self) for _ in range(4)]
        for label in self.imageLabels:
            label.setFixedSize(200, 200)

        # FORMATTING----------------------------------------------------------------------------------------------------------------
        addFormRow(self.layout,"Prompt", self.prompt1LineEdit)
        addFormRow(self.layout,"Negative Prompt", self.negativePrompt1LineEdit)
        addFormRow(self.layout, "Scheduler", self.schedulerComboBox)
        addFormRow(self.layout,"Inference Steps", self.inferenceStepsSpinBox)
        self.layout.addWidget(self.refinerCheckBox)
        addFormRow(self.layout,"Refiner Starts at", self.denoisingFractionSlider)
        self.layout.addWidget(self.denoisingFractionLabel)
        addFormRow(self.layout,"Guidance Scale (CFG)", self.guidanceScaleSpinBox)
        addFormRow(self.layout,"Custom Seed", self.seedSpinBox, self.seedCheckBox)
        self.layout.addWidget(self.heightLabel)
        self.layout.addLayout(self.heightLayout)
        self.layout.addWidget(self.widthLabel)
        self.layout.addLayout(self.widthLayout)
        addFormRow(self.layout,"Number of Images", self.batchSpinBox)
        self.layout.addWidget(self.generateButton)
        # output images
        self.imagesTopLayout = QHBoxLayout()
        self.imagesTopLayout.addWidget(self.imageLabels[0])
        self.imagesTopLayout.addWidget(self.imageLabels[1])
        self.imagesBottomLayout = QHBoxLayout()
        self.imagesBottomLayout.addWidget(self.imageLabels[2])
        self.imagesBottomLayout.addWidget(self.imageLabels[3])
        self.layout.addLayout(self.imagesTopLayout)
        self.layout.addLayout(self.imagesBottomLayout)

        self.layout.addStretch()
        self.load_settings()
        self.SDXL.set_scheduler("EulerDiscreteScheduler")


    def load_settings(self):
        # Read the setting as a list/convert to tuple
        self.settings = QSettings("Ashill", "SDtoUnreal")
        stored_list = self.settings.value("SchedulersList", [])
        if stored_list:
                self.schedulerlist = tuple(stored_list)
                for option in self.schedulerlist:
                    self.schedulerComboBox.addItem(option)
        self.schedulerComboBox.setCurrentText("EulerDiscreteScheduler")


    @Slot()
    def generateClicked(self):
        if not self.seedCheckBox.isChecked():
            self.updateSeed(randint(1, 999999))
        self.setSettings()

        self.worker = WorkerThread(self.SDXL, self.batchSpinBox.value())
        self.generateButton.setText("Generating...")
        # Connect signals and slots
        self.worker.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(lambda: self.generateButton.setEnabled(True))
        self.worker.finished.connect(lambda: self.generateButton.setText("Generate"))
        self.worker.returnpath.connect(self.handle_result)

        # Step 6: Start the thread
        self.worker.start()

        # Disable button while task is running
        self.generateButton.setEnabled(False)

    def handle_result(self, path, i):
            self.imageLabels[i%4].setPixmap(QPixmap(path))
            self.imageLabels[i%4].setScaledContents(True)
            self.imageLabels[i%4].setAlignment(Qt.AlignCenter)

    @Slot()
    def setScheduler(self, index):
        self.SDXL.set_scheduler(self.schedulerComboBox.currentText())\
        


    @Slot()
    def setRefiner(self, state):
        if state:
            self.SDXL.set_refiner(True)
            self.denoisingFractionLabel.setText(".8")
            self.denoisingFractionSlider.setValue(80)
        else:
            self.SDXL.set_refiner(False)

    def setSettings(self):
        settings = {
            "prompt": self.prompt1LineEdit.text(),
            "negativePrompt": self.negativePrompt1LineEdit.text(),
            "numInferenceSteps": self.inferenceStepsSpinBox.value(),
            "denoisingEnd": self.denoisingFractionSlider.value()/100.0,
            "CFG": self.guidanceScaleSpinBox.value(),
            "height": self.heightSpinBox.value(),
            "width": self.widthSpinBox.value(),
            "seed": self.seedSpinBox.value(),
            "numImagesPerPrompt": self.batchSpinBox.value()
        }
        print(settings)
        
        self.SDXL.set_settings(settings)

    def updateSeed(self, seed):
        self.seedSpinBox.setValue(seed)


# def handle_app_exit():
#     """Function to stop all worker threads before app exits."""
#     if hasattr(window.secondMenu, 'worker'):
#         window.secondMenu.worker.stop()
#         window.secondMenu.worker.wait()

def run_gui_app(image_path=None):
    app = QApplication(sys.argv)
    window = MainWindow()
    # app.aboutToQuit.connect(handle_app_exit)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui_app()
