import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QGridLayout, QLineEdit, QWidget, QComboBox, QPushButton, QSpacerItem, QHBoxLayout, QButtonGroup, QRadioButton, QSizePolicy, QCheckBox, QDoubleSpinBox, QSpinBox, QHBoxLayout
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QImage, QResizeEvent, QPixmap
from PipelineAdapters import AdapterPipeline
from drawonimage_example import MaskWidget
from PIL import Image, ImageQt
from random import randint

class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        

        # Set the widget background to white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        self.imageLabel = QLabel('Drag an Image Here or Open Using the Button')
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.imageLabel)

        self.buttonlayout = QHBoxLayout()
        self.openButton = QPushButton('Load Image')
        self.buttonlayout.addWidget(self.openButton, alignment=Qt.AlignCenter)
        self.conditionalButton = QPushButton('Load Canny Image')
        self.buttonlayout.addWidget(self.conditionalButton, alignment=Qt.AlignCenter)
        self.layout.addLayout(self.buttonlayout)

        # Adjust the overall size of this widget and enable drag-and-drop
        self.setFixedHeight(400)
        self.setAcceptDrops(True)

    
    def loadImage(self, image):
        if image:
            q_image = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(325, 325, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.imageLabel.setPixmap(scaled_pixmap)


class AdapterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.Adapters = AdapterPipeline()

        self.setWindowTitle('Image Input Example')
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout(self)

        # Model Selection Combo Box
        self.modelSelectionComboBox = QComboBox()
        self.modelSelectionComboBox.addItem("Select a model...")
        self.modelSelectionComboBox.addItem("Stable Diffusion XL")
        self.modelSelectionComboBox.addItem("Load Custom Model")
        
        # Custom Model Load Section (Initially Hidden)
        self.customModelLineEdit = QLineEdit()
        self.customModelLineEdit.setPlaceholderText("Enter model path...")
        self.loadModelButton = QPushButton("Load Model")

        # ImageWidget setup
        imagelayout = QHBoxLayout()
        self.imageWidget = ImageWidget()
        self.imageWidget.openButton.clicked.connect(lambda: self.openImageDialog(True))
        self.imageWidget.conditionalButton.clicked.connect(lambda: self.openImageDialog(False))

        self.outputImage = QLabel()

        imagelayout.addWidget(self.imageWidget)
        imagelayout.addWidget(self.outputImage)


        # prompt
        self.promptInput = QLineEdit()
        # negativePrompt (optional)
        self.negativePromptInput = QLineEdit()

        # numInferenceSteps
        self.numInferenceStepsInput = QSpinBox()

        # height
        self.heightInput = QSpinBox()
        self.heightInput.setMinimumWidth(100)
        self.heightInput.setMinimum(64)
        self.heightInput.setMaximum(2048)
        self.heightInput.setValue(1024)  
        
        # width
        self.widthInput = QSpinBox()
        self.widthInput.setMinimumWidth(100)
        self.widthInput.setMinimum(64)
        self.widthInput.setMaximum(2048)
        self.widthInput.setValue(1024)  

        # controlGuidanceEnd (defaults to 1.0)
        self.CFGInput = QDoubleSpinBox()
        self.CFGInput.setValue(1.0)
    

        # adapter conditioning scale (defaults to 0.8)
        self.adapterConditioningScaleInput = QDoubleSpinBox()
        self.adapterConditioningScaleInput.setValue(0.8)

        # adapter conditioning factor (defaults to 1)
        self.adapterConditioningFactorInput = QDoubleSpinBox()
        self.adapterConditioningFactorInput.setMinimum(0.0)
        self.adapterConditioningFactorInput.setMaximum(1.0)
        self.adapterConditioningFactorInput.setValue(1)

        # Random Seed Spin Box
        self.seedSpinBox = QSpinBox()
        self.seedSpinBox.setMinimum(1)
        self.seedSpinBox.setMaximum(999999)
        self.seedSpinBox.setValue(0)  
        self.seedSpinBox.setEnabled(False)
        self.seedSpinBox.valueChanged.connect(self.updateSeed)
        self.seedCheckBox = QCheckBox()
        self.seedCheckBox.stateChanged.connect(self.seedSpinBox.setEnabled)
        self.seedCheckBox.stateChanged.connect(self.randomizeSeed)


         # numImagesPerPrompt (defaults to 1)
        self.numImagesPerPromptInput = QSpinBox()
        self.numImagesPerPromptInput.setValue(1)
        
        self.generateButton = QPushButton("Generate Image")
        self.generateButton.clicked.connect(self.generateImage)

        #----------------------------------------------layout---------------------------------------------------
        self.layout.addWidget(self.modelSelectionComboBox)
        self.layout.addLayout(imagelayout)

        # Add LineEdit and Button to layout but hide them initially
        self.layout.addWidget(self.customModelLineEdit)
        self.layout.addWidget(self.loadModelButton)
        self.customModelLineEdit.hide()
        self.loadModelButton.hide()

        # Combo Box Selection Changed Connection
        self.modelSelectionComboBox.currentIndexChanged.connect(self.onModelSelectionChanged)

        # Setup radio buttons
        self.radioButtonsLayout = QGridLayout()
        self.radioButtonGroup = QButtonGroup(self)
        self.radioButtonGroup.setExclusive(True)
        self.setupRadioButtons()
        self.layout.addLayout(self.radioButtonsLayout)
        self.addFormRow("Prompt:", self.promptInput)
        self.addFormRow("Negative Prompt:", self.negativePromptInput)
        self.addFormRow("Number of Inference Steps:", self.numInferenceStepsInput)
        self.addFormRow("CFG Scale:", self.CFGInput)
        self.addFormRow("Height:", self.heightInput)
        self.addFormRow("Width:", self.widthInput)
        self.addFormRow("Adapter Conditioning Scale:", self.adapterConditioningScaleInput)
        self.addFormRow("Adapter Conditioning Factor:", self.adapterConditioningFactorInput)
        self.addFormRow("Custom Seed:", self.seedSpinBox, self.seedCheckBox)
        self.addFormRow("Number of Images per Prompt:", self.numImagesPerPromptInput)
        self.layout.addWidget(self.generateButton)
        # Add a spacer item at the bottom to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(spacer)
    

        
    def openImageDialog(self, to_canny):
        imagePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if imagePath:
            # self.imageWidget.loadImage(imagePath)
            self.imageWidget.loadImage(self.Adapters.set_image(imagePath, to_canny))

            
    def setupRadioButtons(self):
        self.controlTypes = [
            "Canny", "Depth", "OpenPose", "Scribble/Sketch",  "Lineart"
        ]

        for i in reversed(range(self.radioButtonsLayout.count())): 
            self.radioButtonsLayout.itemAt(i).widget().setParent(None)

        button_width = 100  # Assume each button is 100 pixels wide for this example
        n_columns = max(self.width() // button_width, 1)  # Ensure at least one column

        for i, controlType in enumerate(self.controlTypes):
            row = i // n_columns
            col = i % n_columns
            radioButton = QRadioButton(controlType)
            self.radioButtonGroup.addButton(radioButton)
            self.radioButtonsLayout.addWidget(radioButton, row, col)
            
        self.radioButtonGroup.idClicked.connect(self.radioButtonClicked)


    def radioButtonClicked(self, id):
        radioButton = self.radioButtonGroup.button(id)
        self.Adapters.set_adapter_type(radioButton.text())
            

    def onModelSelectionChanged(self, index):
        # Show or hide LineEdit and Load button based on selection
        if self.modelSelectionComboBox.currentText() == "Load Custom Model":
            self.customModelLineEdit.show()
            self.loadModelButton.show()
        else:
            self.customModelLineEdit.hide()
            self.loadModelButton.hide()
        
        # Here you can add additional actions based on the selected model
    def addFormRow(self, labelText, widget, optionalWidget=None):
        rowLayout = QHBoxLayout()
        rowLayout.addWidget(QLabel(labelText))
        rowLayout.addWidget(widget)
        if optionalWidget:
            widget.setEnabled(False)
            rowLayout.addWidget(optionalWidget)
        self.layout.addLayout(rowLayout)

    @Slot()
    def generateImage(self):
        if not self.seedCheckBox.isChecked():
            self.updateSeed(randint(1, 999999))
        adaptersSettingsDict = {
            "prompt": self.promptInput.text(),
            "negativePrompt": self.negativePromptInput.text(),
            "numInferenceSteps": self.numInferenceStepsInput.value(),
            "height": self.heightInput.value(),
            "width": self.widthInput.value(),
            "CFG": self.CFGInput.value(),
            "adapterConditioningScale": self.adapterConditioningScaleInput.value(),
            "adapterConditioningFactor": self.adapterConditioningFactorInput.value(),
            "numImagesPerPrompt": self.numImagesPerPromptInput.value()
        }
        self.Adapters.set_settings(adaptersSettingsDict)
        self.Adapters.generate_image()

    @Slot()
    def updateSeed(self, value):
        self.Adapters.set_seed(value)

    @Slot()
    def randomizeSeed(self, state):
        random_int = randint(1, 999999)
        self.SDXL.set_seed(random_int)
        self.seedSpinBox.setValue(random_int)


    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.setupRadioButtons()

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdapterWindow()
    window.show()
    sys.exit(app.exec())