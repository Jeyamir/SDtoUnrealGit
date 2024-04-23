import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget,  QPushButton, QLineEdit, QVBoxLayout,QHBoxLayout, QWidget, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget, QFileDialog, QComboBox, QSpinBox, QSlider, QCheckBox, QDoubleSpinBox
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QSettings, Qt, Slot
from random import randint
from PipelineSDXL import SDXLPipeline
from QtAdapters import AdapterWindow
from QtDeepBump import ImageProcessor
from utils_Qt import addFormRow
from QtMarigold import MarigoldWindow
from convertimagerange import PixelRangeConversionApp

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
        self.thirdMenu = AdapterWindow()
        self.fourthMenu = ImageProcessor()
        self.fifthMenu = MarigoldWindow()
        self.sixthMenu = PixelRangeConversionApp()

        # Add tab names
        self.tabWidget.addTab(self.firstMenu, "Setup")
        self.tabWidget.addTab(self.secondMenu, "SDXL")
        self.tabWidget.addTab(self.thirdMenu, "Adapters")
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
        self.inferenceStepsSpinBox.valueChanged.connect(self.updateInferenceSteps)

        # Create the Denoising Fraction slider
        self.denoisingFractionSlider = QSlider(Qt.Horizontal)
        self.denoisingFractionSlider.setMinimum(1) 
        self.denoisingFractionSlider.setMaximum(100)  
        self.denoisingFractionSlider.setValue(80)    
        self.denoisingFractionSlider.valueChanged.connect(self.updateDenoisingFraction)
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
        self.guidanceScaleSpinBox.valueChanged.connect(self.updateGuidanceScale)

        # Random Seed Spin Box
        self.seedSpinBox = QSpinBox()
        self.seedSpinBox.setMinimum(1)  # Set minimum value
        self.seedSpinBox.setMaximum(999999)
        self.seedSpinBox.setValue(0)  
        self.seedSpinBox.setEnabled(False)
        self.seedSpinBox.valueChanged.connect(self.updateSeed)
        self.seedCheckBox = QCheckBox()
        self.seedCheckBox.stateChanged.connect(self.seedSpinBox.setEnabled)
        self.seedCheckBox.stateChanged.connect(self.randomizeSeed)


        # Create QLineEdit and QLabel for Prompt1
        self.prompt1Label = QLabel("Prompt1")
        self.prompt1LineEdit = QLineEdit()
        self.prompt1LineEdit.setText("set a prompt please")
        # Create QLineEdit and QLabel for Negative Prompt1
        self.negativePrompt1LineEdit = QLineEdit()



        # Create the height slider
        
        self.heightSlider = QSlider(Qt.Horizontal)
        self.heightSlider.setMinimum(64) 
        self.heightSlider.setMaximum(2048)  
        self.heightSlider.setValue(1024)    
        self.heightSlider.setSingleStep(8)
        self.heightSlider.valueChanged.connect(self.updateHeight)
        # Create the height Spin Box
        self.heightSpinBox = QSpinBox()
        self.heightSpinBox.setMinimumWidth(100)
        self.heightSpinBox.setMinimum(64)
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
        self.widthSlider.setMinimum(64) 
        self.widthSlider.setMaximum(2048)  
        self.widthSlider.setValue(1024)    
        self.widthSlider.setSingleStep(8)
        self.widthSlider.valueChanged.connect(self.updateWidth)
        # Create the width Spin Box
        self.widthSpinBox = QSpinBox()
        self.widthSpinBox.setMinimumWidth(100)
        self.widthSpinBox.setMinimum(64)
        self.widthSpinBox.setMaximum(2048)
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
        self.batchSpinBox.setMaximum(4)

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

        # FORMATTING----------------------------------------------------------------------------------------------------------------
        # self.layout.addWidget(self.negativePrompt1LineEdit)
        addFormRow(self.layout,"Prompt", self.prompt1LineEdit)
        addFormRow(self.layout,"Negative Prompt", self.negativePrompt1LineEdit)

        
        # scheduler
        # layout.addWidget(self.schedulerLabel)
        # self.layout.addWidget(self.schedulerComboBox)
        addFormRow(self.layout, "Scheduler", self.schedulerComboBox)

        # inference steps
        # layout.addWidget(self.inferenceStepsSpinBoxLabel)
        # self.layout.addWidget(self.inferenceStepsSpinBox)
        addFormRow(self.layout,"Inference Steps", self.inferenceStepsSpinBox)

        self.layout.addWidget(self.refinerCheckBox)
    
        # denoising fraction
        # layout.addWidget(self.FractionLabel)
        # self.layout.addWidget(self.denoisingFractionSlider)
        addFormRow(self.layout,"Refiner Starts at", self.denoisingFractionSlider)
        self.layout.addWidget(self.denoisingFractionLabel)

        # guidance scale
        # layout.addWidget(self.guidanceScaleSpinBoxLabel)
        # self.layout.addWidget(self.guidanceScaleSpinBox)
        addFormRow(self.layout,"Guidance Scale (CFG)", self.guidanceScaleSpinBox)

        # random seed
        # layout.addWidget(self.seedSpinBoxLabel)
        # self.layout.addLayout(self.seedLayout)
        addFormRow(self.layout,"Custom Seed", self.seedSpinBox, self.seedCheckBox)

        # prompts
        # layout.addWidget(self.prompt1Label)
        # self.layout.addWidget(self.prompt1LineEdit)


        # height slider
        self.layout.addWidget(self.heightLabel)
        self.layout.addLayout(self.heightLayout)
   
        

        # width slider
        self.layout.addWidget(self.widthLabel)
        self.layout.addLayout(self.widthLayout)


        # batch spin box
        # self.layout.addWidget(self.batchSpinBox)
        addFormRow(self.layout,"Number of Images", self.batchSpinBox)

        # generate button
        self.layout.addWidget(self.generateButton)


        # output images
        self.imagesLayout = QHBoxLayout()
        self.imagesLayout.addWidget(self.imageLabels[0])
        self.imagesLayout.addWidget(self.imageLabels[1])
        self.imagesLayout.addWidget(self.imageLabels[2])
        self.imagesLayout.addWidget(self.imageLabels[3])
        self.layout.addLayout(self.imagesLayout)



        self.layout.addStretch()
        self.load_settings()
        self.SDXL.set_scheduler("EulerDiscreteScheduler")

    # def addFormRow(self, labelText, widget, optionalWidget=None):
    #     rowLayout = QHBoxLayout()
    #     rowLayout.addWidget(QLabel(labelText))
    #     rowLayout.addWidget(widget)
    #     if optionalWidget:
    #         widget.setEnabled(False)
    #         rowLayout.addWidget(optionalWidget)
    #     self.layout.addLayout(rowLayout)
        
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
        prompt1 = self.prompt1LineEdit.text()
        negative_prompt1 = self.negativePrompt1LineEdit.text()

        self.SDXL.set_prompts(prompt1, negative_prompt1)
        # pixmaps = [None]*4  
        for i in range(self.batchSpinBox.value()):
            imagePath = self.SDXL.generate_image(i)
            self.imagesLayout = QHBoxLayout()
            if imagePath:
                pixmap = QPixmap(imagePath)
                # pixmap.scaled(self.imageLabel.width(), self.imageLabel.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imageLabels[i].setPixmap(pixmap)
                self.imageLabels[i].adjustSize()
                self.imageLabels[i].setScaledContents(True)


    @Slot()
    def setScheduler(self, index):
        self.SDXL.set_scheduler(self.schedulerComboBox.currentText())

    @Slot()
    def updateDenoisingFraction(self):
        # Divide by 100 to convert back to the desired floating point range
        value = self.denoisingFractionSlider.value() / 100
        self.denoisingFractionLabel.setText(f"{value:.1f}")
        self.SDXL.set_denoising_fraction(value)

    @Slot()
    def updateInferenceSteps(self, value):
        self.SDXL.set_inference_steps(value)

    @Slot()
    def updateGuidanceScale(self, value):
        self.SDXL.set_CFG(value)

    @Slot()
    def updateHeight(self):
        # Divide by 100 to convert back to the desired floating point range
        value = self.heightSlider.value()
        self.SDXL.set_height(value)
        
    @Slot()
    def updateWidth(self):
        # Divide by 100 to convert back to the desired floating point range
        value = self.widthSlider.value()
        self.SDXL.set_width(value)
        
    @Slot()
    def updateSeed(self, value):
        self.SDXL.set_seed(value)
        
    @Slot()
    def randomizeSeed(self, state):
        random_int = randint(1, 999999)
        self.SDXL.set_seed(random_int)
        self.seedSpinBox.setValue(random_int)

    @Slot()
    def setRefiner(self, state):
        if state:
            self.SDXL.set_refiner(True)
            self.denoisingFractionLabel.setText(".8")
            self.denoisingFractionSlider.setValue(80)
            self.SDXL.set_denoising_fraction(.8)
        else:
            self.SDXL.set_refiner(False)




def run_gui_app(image_path=None):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui_app()
