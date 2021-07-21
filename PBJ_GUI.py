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
        self.setTitle("Output State")
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

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
    def __init__(self):
        super().__init__()
        # self.setRowCount(12)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Address", "Delay", "Output State", "Instruction", "Argument(s)"])
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setMaximumWidth(525)

# Maybe doesn't need to be a GroupBox
# Use QComboBox for the dropdown
# Can use this class with for the instruction input and delay input, with constructor that determines which side has the dropdown
class DelayInputBox(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.setTitle("Delay")

        self.input_delay = QtWidgets.QLineEdit()
        self.input_delay.setFixedWidth(75)
        self.label_delay = QtWidgets.QLabel("ns")
        self.layout.addWidget(self.input_delay)
        self.layout.addWidget(self.label_delay)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.layout)

class FlowInputBox(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.setTitle("Flow Control")

        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.addItems(["CONTINUE", "START_LOOP", "END_LOOP", "CALL_SUB", "RET_SUB", "JUMP_IF", "WAIT_FOR"])

        self.arg_list = QtWidgets.QLineEdit()
        self.arg_list.setFixedWidth(75)

        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.arg_list)


        self.setLayout(self.layout)

        

class InstructionInputBox(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout()
        self.setTitle("Instruction")
        self.flow_input = FlowInputBox()
        self.delay_input = DelayInputBox()
        self.pattern_box = PatternBox()
        self.setLayout(self.layout)

        self.layout.addWidget(self.delay_input, 0, 0)
        self.layout.addWidget(self.pattern_box, 0, 1)
        self.layout.addWidget(self.flow_input, 0, 2)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

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
        # self.layout.addWidget(self.pattern_box)
        self.layout.addWidget(InstructionInputBox())
        self.layout.addWidget(InstructionArrayBox())
        self.setLayout(self.layout)


        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

def main():
    app = QtWidgets.QApplication([])
    gui = PBJ_GUI()
    gui.resize(525,600)
    gui.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()