import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QGridLayout, QLineEdit, QWidget, QComboBox, QPushButton, QSpacerItem, QHBoxLayout, QButtonGroup, QRadioButton, QSizePolicy, QCheckBox, QDoubleSpinBox, QSpinBox
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QImage, QResizeEvent
from controlnet import ControlNetPipeline

class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.controlNet = ControlNetPipeline()

        # Set the widget background to white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        self.imageLabel = QLabel('Drag an Image Here or Open Using the Button')
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)

        self.openButton = QPushButton('Open Image')
        self.layout.addWidget(self.openButton, alignment=Qt.AlignCenter)

        # Adjust the overall size of this widget and enable drag-and-drop
        self.setFixedHeight(400)
        self.setAcceptDrops(True)

    def loadImage(self, imagePath):
        image = QImage(imagePath)
        if image.isNull():
            return
        scaledImage = image.scaledToHeight(360, Qt.SmoothTransformation)  # Scale the image
        self.imageLabel.setPixmap(QPixmap.fromImage(scaledImage))

class ControlNetWindow(QWidget):
    def __init__(self):
        super().__init__()
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
        self.imageWidget = ImageWidget()
        self.imageWidget.openButton.clicked.connect(self.openImageDialog)

        # prompt
        self.promptInput = QLineEdit()
        self.promptInput.textChanged.connect(self.onPromptChanged)
 

        # height
        self.heightInput = QSpinBox()
        self.heightInput.valueChanged.connect(self.onHeightChanged)
        

        # width
        self.widthInput = QSpinBox()
        self.widthInput.valueChanged.connect(self.onWidthChanged)
        

        # numInferenceSteps
        self.numInferenceStepsInput = QSpinBox()
        self.numInferenceStepsInput.valueChanged.connect(self.onNumInferenceStepsChanged)
        

        # negativePrompt (optional)
        self.negativePromptInput = QLineEdit()
        self.negativePromptInput.textChanged.connect(self.onNegativePromptChanged)
        self.negativePromptCheckbox = QCheckBox("Enable Negative Prompt")
        self.negativePromptCheckbox.stateChanged.connect(self.onNegativePromptCheckboxChanged)
        

        # numImagesPerPrompt (defaults to 1)
        self.numImagesPerPromptInput = QSpinBox()
        self.numImagesPerPromptInput.setValue(1)
        self.numImagesPerPromptInput.valueChanged.connect(self.onNumImagesPerPromptChanged)
        

        # controlNetConditioningScale
        self.controlNetConditioningScaleInput = QDoubleSpinBox()
        self.controlNetConditioningScaleInput.valueChanged.connect(self.onControlNetConditioningScaleChanged)
        

        # guessMode (bool)
        self.guessModeInput = QCheckBox("Guess Mode")
        self.guessModeInput.stateChanged.connect(self.onGuessModeChanged)
        

        # controlGuidanceStart (defaults to 0.0)
        self.controlGuidanceStartInput = QDoubleSpinBox()
        self.controlGuidanceStartInput.setValue(0.0)
        self.controlGuidanceStartInput.valueChanged.connect(self.onControlGuidanceStartChanged)
        

        # controlGuidanceEnd (defaults to 1.0)
        self.controlGuidanceEndInput = QDoubleSpinBox()
        self.controlGuidanceEndInput.setValue(1.0)
        self.controlGuidanceEndInput.valueChanged.connect(self.onControlGuidanceEndChanged)    


        self.layout.addWidget(self.modelSelectionComboBox)
        self.layout.addWidget(self.imageWidget)

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
        self.addFormRow("Height:", self.heightInput)
        self.addFormRow("Width:", self.widthInput)
        self.addFormRow("Number of Inference Steps:", self.numInferenceStepsInput)
        self.addFormRow("Negative Prompt:", self.negativePromptInput, self.negativePromptCheckbox)
        self.addFormRow("Number of Images per Prompt:", self.numImagesPerPromptInput)
        self.addFormRow("ControlNet Conditioning Scale:", self.controlNetConditioningScaleInput)
        self.layout.addWidget(self.guessModeInput)
        self.addFormRow("Control Guidance Start:", self.controlGuidanceStartInput)
        self.addFormRow("Control Guidance End:", self.controlGuidanceEndInput)

        # Add a spacer item at the bottom to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(spacer)
    

        
    def openImageDialog(self):
        imagePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if imagePath:
            self.imageWidget.loadImage(imagePath)

    def setupRadioButtons(self):
        self.controlTypes = [
            "All", "Canny", "Depth", "NormalMap", "OpenPose", "MLSD", "Lineart",
            "SoftEdge", "Scribble/Sketch", "Segmentation", "Shuffle", "Tile/Blur",
            "Inpaint", "InstructP2P", "Reference", "Recolor", "Revision", "T2I-Adapter",
            "IP-Adapter", "Instant_ID", "SparseCtrl"
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
        print(f"{radioButton.text()} selected")

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
    def onPromptChanged(self, text):
        print("Prompt changed:", text)

    @Slot()
    def onHeightChanged(self, value):
        print("Height changed:", value)

    @Slot()
    def onWidthChanged(self, value):
        print("Width changed:", value)

    @Slot()
    def onNumInferenceStepsChanged(self, value):
        print("Number of Inference Steps changed:", value)

    @Slot()
    def onNegativePromptChanged(self, text):
        print("Negative Prompt changed:", text)

    @Slot()
    def onNegativePromptCheckboxChanged(self, state):
        self.negativePromptInput.setEnabled(self.negativePromptCheckbox.isChecked())

    @Slot()
    def onNumImagesPerPromptChanged(self, value):
        print("Number of Images per Prompt changed:", value)

    @Slot()
    def onControlNetConditioningScaleChanged(self, value):
        print("ControlNet Conditioning Scale changed:", value)

    @Slot()
    def onGuessModeChanged(self, state):
        print("Guess Mode changed:", state)

    @Slot()
    def onControlGuidanceStartChanged(self, value):
        print("Control Guidance Start changed:", value)

    @Slot()
    def onControlGuidanceEndChanged(self, value):
        print("Control Guidance End changed:", value)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.setupRadioButtons()

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlNetWindow()
    window.show()
    sys.exit(app.exec())