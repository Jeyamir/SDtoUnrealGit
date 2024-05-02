from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

def addFormRow(layout, labelText, widget, optionalWidget=None, enabled=True):
        rowLayout = QHBoxLayout()
        rowLayout.addWidget(QLabel(labelText))
        rowLayout.addWidget(widget)
        if optionalWidget:
            widget.setEnabled(enabled)
            rowLayout.addWidget(optionalWidget)
        layout.addLayout(rowLayout)