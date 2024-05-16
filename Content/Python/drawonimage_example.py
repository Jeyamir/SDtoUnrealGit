import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMainWindow, QHBoxLayout)
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PySide6.QtCore import Qt, QPoint
import os
from Inpainting import circle_mask
from PIL import Image
from PIL.ImageQt import ImageQt

class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Set the widget background to white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        self.imageLabel = QLabel('Upload an Image')
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)

        self.uploadButton = QPushButton('Upload Image')
        self.uploadButton.clicked.connect(self.uploadImage)
        self.layout.addWidget(self.uploadButton)

        self.saveButton = QPushButton('Save Mask')
        self.saveButton.clicked.connect(self.saveMask)
        self.layout.addWidget(self.saveButton)

        self.image = QImage()
        self.drawing = False
        self.lastPoint = QPoint()

        self.setMinimumSize(400,400)

    def uploadImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if filePath:
            pil_img = Image.open(filePath)
            pil_img, mask = circle_mask(pil_img)
            self.image = self.PIL_to_qimage(pil_img)
            self.imageLabel.clear()
            self.update()
            

            # pil_img = Image.open(filePath)
            # self.image, mask = circle_mask(pil_img)
            # # self.image = QImage(filePath)
            # self.image = QImage.fromImage(ImageQt(self.image))
            # self.imageLabel.clear()
            # self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.image.isNull():
            scale, offset = self.getImageScaleAndOffset()
            # Adjusting the event position with the scale and offset
            self.lastPoint = QPoint((event.position().x() - offset.x()) / scale,
                                    (event.position().y() - offset.y()) / scale)
            self.drawing = True

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            scale, offset = self.getImageScaleAndOffset()
            # Adjusting the event position with the scale and offset
            currentPoint = QPoint((event.position().x() - offset.x()) / scale,
                                (event.position().y() - offset.y()) / scale)
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.black, 40, Qt.SolidLine))

            painter.drawLine(self.lastPoint, currentPoint)
            self.lastPoint = currentPoint
            painter.end()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.image.isNull():
            # Calculate the scaling factor to maintain aspect ratio
            scaledImage = self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Create a QPainter for drawing
            painter = QPainter(self)
            # Calculate the top left point to center the image
            topLeftX = (self.width() - scaledImage.width()) / 2
            topLeftY = (self.height() - scaledImage.height()) / 2
            # Draw the image centered in the widget
            painter.drawImage(QPoint(topLeftX, topLeftY), scaledImage)

    def create_mask(self):
        mask = QImage(self.image.size(), QImage.Format_Grayscale8)
        mask.fill(Qt.black)  # Start with a completely black image

        for x in range(self.image.width()):
            for y in range(self.image.height()):
                if self.image.pixelColor(x, y) == QColor(Qt.black):
                    mask.setPixelColor(x, y, QColor(Qt.white))  # Set painted areas to white

        return mask

    def saveMask(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Mask", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        if filePath:
            self.mask = self.create_mask()  # Corrected line: call create_mask directly on self
            self.mask.save(filePath)


    def getImageScaleAndOffset(self):
        if self.image.isNull():
            return 1, QPoint(0, 0)  # Default values when no image is loaded

        # The scale factor for the image
        scaleWidth = self.width() / self.image.width()
        scaleHeight = self.height() / self.image.height()
        scale = min(scaleWidth, scaleHeight)

        # Calculating the offset to center the image
        offsetX = (self.width() - (self.image.width() * scale)) / 2
        offsetY = (self.height() - (self.image.height() * scale)) / 2

        return scale, QPoint(offsetX, offsetY)
    
    def PIL_to_qimage(self, pil_img):
        temp = pil_img.convert('RGBA')
        return QImage(
            temp.tobytes('raw', "RGBA"),
            temp.size[0],
            temp.size[1],
            QImage.Format.Format_RGBA8888
        )
class MaskWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Set the widget background to white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        self.maskLabel = QLabel('Upload Mask')
        self.maskLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.maskLabel)

         # Adding a Reload button to reload the mask
        self.reloadButton = QPushButton('Reload Mask')
        self.reloadButton.clicked.connect(self.reloadMask)
        self.layout.addWidget(self.reloadButton)

        self.uploadButton = QPushButton('Upload Mask')
        self.uploadButton.clicked.connect(self.uploadMask)
        self.layout.addWidget(self.uploadButton)
        
        # Adjust the overall size of this widget and enable drag-and-drop
        self.setMinimumSize(400,400)

    def loadMask(self, maskPath):
        mask = QPixmap(maskPath)
        self.maskLabel.setPixmap(mask.scaled(self.maskLabel.size(), Qt.KeepAspectRatio))
        self.update()

    def uploadMask(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Upload Mask", "", "Image Files (*.png *.jpg *.jpeg)")
        if filePath:
            self.loadMask(filePath)
    def reloadMask(self):
            # Path to the mask file
            maskPath = 'mask.png'
            # Check if the mask file exists and load it
            if os.path.exists(maskPath):
                self.loadMask(maskPath)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image and Mask Editor")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)



        layout = QHBoxLayout(centralWidget)

        self.imageWidget = ImageWidget(self)
        self.maskWidget = MaskWidget(self)

        layout.addWidget(self.imageWidget)
        layout.addWidget(self.maskWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
