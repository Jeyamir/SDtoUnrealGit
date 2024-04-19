from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

def addFormRow(layout, labelText, widget, optionalWidget=None):
        rowLayout = QHBoxLayout()
        rowLayout.addWidget(QLabel(labelText))
        rowLayout.addWidget(widget)
        if optionalWidget:
            widget.setEnabled(False)
            rowLayout.addWidget(optionalWidget)
        layout.addLayout(rowLayout)