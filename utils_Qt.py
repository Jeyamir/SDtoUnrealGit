from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QFileDialog, QLayout
from PIL import Image
def addFormRow(layout, labelText, widget, optionalWidget=None, enabled=True):
        rowLayout = QHBoxLayout()
        label = QLabel(labelText)
        rowLayout.addWidget(label)
        rowLayout.addWidget(widget)
        if optionalWidget:
            widget.setEnabled(enabled)
            rowLayout.addWidget(optionalWidget)
        layout.addLayout(rowLayout)
        return rowLayout

def upload_image(parent=None):
    """
    Opens a file dialog to select an image file and returns the selected file path.
    :param parent: QWidget that will act as the parent of this file dialog. Can be None.
    :return: The path of the selected file as a string, or None if no file is selected.
    """
    file_dialog = QFileDialog(parent)
    file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
    file_dialog.setViewMode(QFileDialog.Detail)
    file_dialog.setFileMode(QFileDialog.ExistingFile)

    if file_dialog.exec():
        file_path = file_dialog.selectedFiles()[0]
        return file_path
    return None

def save_image(image, parent=None):
    """
    Opens a file dialog to save an image. 
    :param image: QImage or similar image object that has a save method.
    :param parent: QWidget that will act as the parent of this file dialog. Can be None.
    :return: None
    """
    if image:
        file_path, _ = QFileDialog.getSaveFileName(parent, "Save Image", ".", "Images (*.png *.jpg *.bmp)")
        if file_path:
            image.save(file_path)


def hide_widgets_in_layout(layout):
    """Recursively hide all widgets in a given layout."""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget():  # Check if the item is a widget
            item.widget().hide()
        elif item.layout():  # Check if the item is a sub-layout
            hide_widgets_in_layout(item.layout()) 

def show_widgets_in_layout(layout):
    """Recursively hide all widgets in a given layout."""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget():  # Check if the item is a widget
            item.widget().show()
        elif item.layout():  # Check if the item is a sub-layout
            hide_widgets_in_layout(item.layout()) 