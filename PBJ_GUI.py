#!/usr/bin/env python3

import sys
import random
from PySide6 import QtCore, QtWidgets

class Button(QtWidgets.QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setGeometry(0, 0, 100, 100)
        # self.setFixedHeight(100)
        # self.setFixedWidth(100)

# use QVBoxLayout
class InfoBox(QtWidgets.QGroupBox):
    pass

# use QHBoxLayout
# potentially with a QVBoxLayout with a QHBoxLayout inside of it? so that I can display the hex underneath
# or don't need to display the hex, it's kind of redundant
class PatternBox(QtWidgets.QGroupBox):
    pass

# Use QTableWidget? Not sure yet
class InstructionArrayBox(QtWidgets.QTableWidget):
    pass

# Maybe doesn't need to be a GroupBox
# Use QComboBox for the dropdown
# Can use this class with for the instruction input and delay input, with constructor that determines which side has the dropdown
class InputBox(QtWidgets.QGroupBox):
    pass

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = Button("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

def main():
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(400,300)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()