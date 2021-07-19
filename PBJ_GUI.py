#!/usr/bin/env python3

import sys
import random
from typing import Pattern
from PySide6 import QtCore, QtWidgets

class Button(QtWidgets.QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        # self.setGeometry(0, 0, 100, 100)
        # self.setFixedHeight(100)
        # self.setFixedWidth(100)

class InfoBox(QtWidgets.QGroupBox):
    def __init__(self, title):
        super().__init__()
        self.setTitle(title)

        # TODO: find better widget for these labels
        self.version_label = QtWidgets.QLabel()
        self.com_label = QtWidgets.QLabel()

        self.layout = QtWidgets.QFormLayout()
        self.layout.addRow("PBJ Version:", self.version_label)
        self.layout.addRow("COM port:", self.com_label)
        self.setLayout(self.layout)

class PatternBox(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Pattern")
        self.layout = QtWidgets.QGridLayout()

        # Array representing the status (checked or unchecked) of each checkbox as booleans
        # (1 = checked)
        self.checkbox_status = [0]*24

        # Array of checkbox widgets
        # index 0 is LSB, index 23 is MSB
        self.checkboxes = []
        for i in range(24):
            self.checkboxes.append(QtWidgets.QCheckBox())

        # Use 23-i so that checkboxes are displayed from MSB to LSB, left to right
        for i in range(24):
            self.layout.addWidget(self.checkboxes[i], 1, 23-i) 
            self.layout.addWidget(QtWidgets.QLabel(str(i)), 0, 23-i)
        # TODO: figure out formatting here so that labels aren't so far away


        self.setLayout(self.layout)

    def update_checkbox_status(self):
        for i in range(24):
            self.checkbox_status[i] = self.checkboxes[i].isChecked()


# Use QTableWidget? Not sure yet
class InstructionArrayBox(QtWidgets.QTableWidget):
    pass

# Maybe doesn't need to be a GroupBox
# Use QComboBox for the dropdown
# Can use this class with for the instruction input and delay input, with constructor that determines which side has the dropdown
class InputBox(QtWidgets.QGroupBox):
    pass

class PBJ_GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = Button("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.info_box = InfoBox("Information")
        self.pattern_box = PatternBox()

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.info_box)
        self.layout.addWidget(self.pattern_box)
        self.setLayout(self.layout)


        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

def main():
    app = QtWidgets.QApplication([])
    gui = PBJ_GUI()
    gui.resize(400,300)
    gui.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()