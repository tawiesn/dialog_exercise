#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = "Tobias Wiesner"
__license__ = "GPL 3.0"
__maintainer__ = "Tobias Wiesner"
__email__ = "tobias@tawiesn.de"

import sys
import unittest
import itertools
from bitstring import BitArray

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import QTest

from ex_gui import ExerciseWindow,MyRegisterModel
from ex_unittest import EightBitDemoDevice

if __name__ == "__main__":
  app = QApplication(sys.argv)
  demodevice = EightBitDemoDevice()
  model = MyRegisterModel(demodevice)
  form = ExerciseWindow()
  form.setModel(model)
  form.show()
  sys.exit(app.exec())
