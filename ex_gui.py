#!/usr/bin/python3
# -*- coding:utf-8 -*-

__author__ = "Tobias Wiesner"
__license__ = "GPL 3.0"
__maintainer__ = "Tobias Wiesner"
__email__ = "tobias@tawiesn.de"

import sys
import os
from random import randint
from bitstring import BitArray

from PyQt5.QtCore import *

from PyQt5.QtWidgets import *

#####################################################################
  
class HardwareLayerA:
  """ Hardware interface layer A """
  my_data = [
      ["reg 1", BitArray(int = 1, length=16), 
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 7]
        ],
        BitArray('0b00000000')
      ],
      ["reg 2", BitArray(int = 2, length=16),
        [
        ["slider",0,8]
        ],
        BitArray('0b00000000')
      ],
      ["reg 3", BitArray(int = 3, length=16),
        [
        ["bit 0",0,1],
        ["bit 1-3",1,3],
        ["bit 4-8",4,4]    
        ],
        BitArray('0b00000000')
      ],
      ]
      
  def loadData(self):
    return self.my_data

  def storeData(self, data):
    self.my_data = data
    print("Store data through Hardware Layer A")
    print(data)

#####################################################################

class HardwareLayerB:  
  """ Hardware interface layer B """
  my_data = [
      ["reg 1", BitArray(int = 1, length=16), 
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 7]
        ],
        BitArray('0b00000000')
      ],
      ["reg 2", BitArray(int = 2, length=16),
        [
        ["slider",0,8]
        ],
        BitArray('0b00000000')
      ],
      ]
  
  def loadData(self):
    return self.my_data
    
  def storeData(self, data):
    self.my_data = data
    print("Store data through Hardware Layer B")
    print(data)
  
  
#####################################################################  
  
class MyRegisterModel(QAbstractTableModel):
  """ Model class storing data """
  
  __devicedata = []
  
  def __init__(self, hardwarelayer = 'HardwareLayerA', parent=None, *args):
    """ Constructor with factory-like selection of hardware layer """
    QAbstractTableModel.__init__(self, parent, *args)

    self.hw = None    
    if hardwarelayer == "HardwareLayerA":
      self.hw = HardwareLayerA()
      self.__devicedata = self.hw.loadData()
    elif hardwarelayer == "HardwareLayerB":
      self.hw = HardwareLayerB()
      self.__devicedata = self.hw.loadData()
    else:
      self.hw = hardwarelayer
      self.__devicedata = self.hw.loadData()
    
  def __del__(self):
    """ destructor: write data to hardware layer """
    print("Send data to hardware layer")
    self.hw.storeData(self.__devicedata)
    print("Close connection")

  def rowCount(self, parent):
    """ Needed for QAbstractTableModel """
    return len(self.__devicedata)
  
  def columnCount(self, parent):
    """ Needed for QAbstractTableModel """  
    return 4
    
  def getRegisterName(self, i):
    """Get function """  
    return self.data(self.createIndex(i,0),Qt.DisplayRole)

  def getRegisterAddress(self, i):
    """Get function """    
    return self.data(self.createIndex(i,1),Qt.DisplayRole)
    
  def getRegisterValue(self,i):
    """Get function """    
    """ returns the 8bit value in a BitString object """
    dat = self.data(self.createIndex(i,3),Qt.DisplayRole)
    if isinstance(dat, BitArray) == False:
      raise RuntimeError("Error: data is not a BitArray")
    if len(dat) != 8:
      raise RuntimeError("Error: data is not a BitArray of length 8")
    return self.data(self.createIndex(i,3),Qt.DisplayRole)

  def getRegisterSubValue(self,i,pos,width):
    """Get function """    
    # get full value stored in model as a BitString
    dataValue = self.getRegisterValue(i)
    subValue = dataValue[pos:pos+width].uint
    return subValue
    
  def getBitfields(self, i):
    """Get function """    
    return self.data(self.createIndex(i,2),Qt.DisplayRole)

  def getNumberOfBitfields(self, i):
    """Get function """  
    return len(self.getBitfields(i))  

  def setRegisterValue(self, i, val):
    """ accepts an integer and stores it as 8bit BitArray object """
    bVal = BitArray(uint = val, length = 8)
    return self.setData(self.createIndex(i,3),bVal)
    
  def setRegisterSubValue(self, i, pos, width, val):
    """ accepts an integer and stores it as subset of 8bit BitArray object """  
    # get full value stored in model as a BitString
    dataValue = self.getRegisterValue(i)
    
    if val < 0 or val > pow(2,width)-1:
      raise RuntimeError("ERROR: val = {0} conflicts with bit width {1}".format(val,width))
    
    subValue = BitArray(uint=val, length=width)
    dataValue[pos:pos+width] = subValue
    self.setRegisterValue(i,dataValue.uint)
            
  def data(self, index, role):
    """ Data access routine in QAbstractTableModel class """
    if not index.isValid():
      return QVariant()
    elif role != Qt.DisplayRole:
      return QVariant()
    
    # default (e.g., for TableView)
    return self.__devicedata[index.row()][index.column()]

  def setData(self, index, value):
    """ Data access routine in QAbstractTableModel class """  
    if index.column() == 0:
      if isinstance(value, string) == False:
        raise RuntimeError("ERROR: Register name must be of type string")
    if index.column() == 1:
      if isinstance(value, int) == False:
        raise RuntimeError("ERROR: Register address must be of type int")
    if index.column() == 3:
      if isinstance(value, BitArray) == False:
        raise RuntimeError("ERROR: Register value must be of type BitArray")

    self.__devicedata[index.row()][index.column()] = value
    return True
  
  def flags(self, index):
    return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

#####################################################################

class BitfieldWidget(QWidget):
  """ WidgetHandler for Bitfields """
  
  __model = None # underlying model class
  __reg   = -1   # number of register (selected in combobox)
  __pos   = -1   # position in 8bit register
  __width = 0    # bitfield width
  __act   = None # GUI element for bitfield
  
  def __init__(self, *args):
    """ standard constructor """
    QWidget.__init__(self, *args)

  def setModel(self, model):
    """ set underlying model """
    self.__model = model
    
  def model(self):
    """ return underlying model """
    return self.__model

  def createWidget(self, register, pos, bitFieldWidth):
    """ create widget for selected bitfield entry """
    self.__reg   = register
    self.__pos   = pos
    self.__width = bitFieldWidth

    if self.__pos < 0 or self.__pos > 7:
      raise RuntimeError("Error: bitfield position must between 0 and 7")
    if self.__pos + self.__width > 8:
      raise RuntimeError("Error: inconsisten bitfield width and positiion")

    if bitFieldWidth == 1:
      self.__act = QPushButton(self)
      self.__act.setCheckable(True)
      self.__act.clicked.connect(self.slotBitfieldButtonChange)
    elif bitFieldWidth < 4:
      self.__act = QComboBox(self)
      for k in range(0,pow(2,bitFieldWidth)):
        self.__act.addItem(str(k))
      self.__act.currentIndexChanged.connect(self.slotBitfieldComboChange)
        
    elif bitFieldWidth < 9:
      self.__act = QSlider(self)
      self.__act.setRange(0,pow(2,bitFieldWidth)-1)
      self.__act.setTickInterval(1)    
      self.__act.setOrientation(Qt.Horizontal)  
      self.__act.setTickPosition(QSlider.TicksBelow)  
      self.__act.valueChanged.connect(self.slotBitfieldSliderChange)
    else:
      raise RuntimeError("Error: bitfield width cannot exceed size 8")
    return self.__act

  def slotBitfieldButtonChange(self):
    """ update model and GUI if button was pressed """
    val = 0
    if self.__act.isChecked() == True:
      val = 1
    self.__model.setRegisterSubValue(self.__reg, self.__pos, self.__width, val)
    self.parent().updateUI()

  def slotBitfieldComboChange(self,i):
    """ update model and GUI if combo box selection has changed """
    self.__model.setRegisterSubValue(self.__reg, self.__pos, self.__width, i)
    self.parent().updateUI()

  def slotBitfieldSliderChange(self):
    """ update model and GUI if slider value has changed """
    self.__model.setRegisterSubValue(self.__reg, self.__pos, self.__width, self.__act.value())
    self.parent().updateUI()
    
  def updateUI(self):
    """ update GUI elements for current bitfield with data from model """
    subValue = self.__model.getRegisterSubValue(self.__reg,self.__pos,self.__width)
    if self.__width == 1:
      if ((subValue == 1 and self.__act.isChecked() == False) or (subValue == 0 and self.__act.isChecked() == True)):
        self.__act.toggle()
      if self.__act.isChecked() == True:
        self.__act.setText("HIGH")
      else:
        self.__act.setText("LOW")
    elif self.__width < 4:
      self.__act.setCurrentIndex(subValue)
    elif self.__width < 9:
      self.__act.setValue(subValue)
    else:
      raise RuntimeError("Error: bitfield width cannot exceed size 8")
      
  def testMe(self):
    subValue = self.__model.getRegisterSubValue(self.__reg,self.__pos,self.__width)
    
    # check type of GUI element
    if (self.__width == 1) and (isinstance(self.__act,QPushButton) == False):
      raise RuntimeError("Error: bitfield width == 1 but GUI element is not a push button")
      return False
    if (self.__width > 1) and (self.__width < 4) and (isinstance(self.__act,QComboBox) == False):
      raise RuntimeError("Error: bitfield width between 2 and 3 but GUI element is not a combo box")
      return False
    if (self.__width > 3) and (self.__width < 9) and (isinstance(self.__act,QSlider) == False):
      raise RuntimeError("Error: bitfield width between 4 and 8 but GUI element is not a slider")
      return False
    if (self.__width < 1) or (self.__width > 8):
      raise RuntimeError("Error: invalid bitfield width: {0}".format(self.__width))
      return False
    if (isinstance(self.__act,QSlider) == False) and (isinstance(self.__act,QComboBox) == False) and (isinstance(self.__act,QPushButton) == False) :
      raise RuntimeError("Error: invalid GUI element")
      return False

    #check whether GUI element contains right data
    if isinstance(self.__act,QSlider) == True:
      if(subValue != self.__act.value()):
        raise RuntimeError("Error: slider value does not correspond to sub-value from model")
        return False
    elif isinstance(self.__act,QComboBox) == True:
      if(subValue != self.__act.currentIndex()):
        raise RuntimeError("Error: combo box value does not correspond to sub-value from model")
        return False      
    elif isinstance(self.__act,QPushButton) == True:
      if subValue == 1 and self.__act.isChecked() == False:
        raise RuntimeError("Error: button value does not correspond to sub-value from model")
        return False
      elif subValue == 0 and self.__act.isChecked() == True:
        raise RuntimeError("Error: button value does not correspond to sub-value from model")
        return False    

	# set GUI element to random number and modify value (checked in ExerciseWindow.testMe)
    rndnr = randint(0,pow(2,self.__width)-1)  # generate random number

	# set GUI element to random number        
    if isinstance(self.__act,QSlider) == True:
      self.__act.setValue(rndnr)
    elif isinstance(self.__act,QComboBox) == True:
      self.__act.setCurrentIndex(rndnr)
    elif isinstance(self.__act,QPushButton) == True:
      if rndnr == 0 and self.__act.isChecked() == True:
        self.__act.toggle()
      elif rndnr == 1 and self.__act.isChecked() == False:
        self.__act.toggle()
      self.slotBitfieldButtonChange()  
    
        
    subValueNew = self.__model.getRegisterSubValue(self.__reg,self.__pos,self.__width)        
    if rndnr != subValueNew:
      raise RuntimeError("Error: failed to store new subvalue")
      return False
                
#####################################################################

class ExerciseWindow(QWidget):
  """ Exercise MainWindow """
  __model = None
  
  def __init__(self, *args):
    """ standard constructor """
    QWidget.__init__(self, *args)
         
  def setModel(self, model):
    """ sets underlying model object and initializes GUI """
    self.__model = model
    
    self.__cmbSelectRegister = QComboBox()
    self.__cmbSelectRegister.setModel(self.__model)
    self.__cmbSelectRegister.currentIndexChanged.connect(self.changeRegisterSelection)
    
    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.__cmbSelectRegister)

    self.setMinimumWidth(300)
            
    self.setWindowTitle("Exercise")
    
    # initialize UI data
    self.changeRegisterSelection(0)

    # set main layoyt
    self.setLayout(self.layout)

  def model(self):
    """ returns underlying model object """
    return self.__model

  def changeRegisterSelection(self, i):
    """ slot function switching to new register """
    print("Switch to register with index " + str(i+1) + "/" + str(self.__cmbSelectRegister.count()))
    if self.layout.count() == 2:
      self.layout.itemAt(1).widget().deleteLater()
      
    layoutRegister = QVBoxLayout(self)
    
    self.__labelRegisterName = QLabel()
    self.__labelRegisterName.setText("Register: " + self.__model.getRegisterName(i))
    self.__labelRegisterName.setTextFormat(Qt.PlainText)
    layoutRegister.addWidget(self.__labelRegisterName)

    self.__labelRegisterAddress = QLabel()
    self.__labelRegisterAddress.setText("Address: 0x" + self.__model.getRegisterAddress(i).hex)
    self.__labelRegisterAddress.setTextFormat(Qt.PlainText)
    layoutRegister.addWidget(self.__labelRegisterAddress)

    layoutRegisterValue = QHBoxLayout(self)
    self.__labelRegisterValName = QLabel()
    self.__labelRegisterValName.setText("Value: ")
    self.__labelRegisterValName.setTextFormat(Qt.PlainText)
    layoutRegisterValue.addWidget(self.__labelRegisterValName)
    
    regVal = int(self.__model.getRegisterValue(i).uint)
    self.__labelRegisterValue = QSpinBox()
    self.__labelRegisterValue.setRange(0,255) # 8bit integer
    self.__labelRegisterValue.setValue(regVal)
    self.__labelRegisterValue.valueChanged.connect(self.slotRegisterValueChanged)
    layoutRegisterValue.addWidget(self.__labelRegisterValue)
    layoutRegister.addLayout(layoutRegisterValue)
    
    self.__actorBitfield = []
    cnt = 0
    sumBitfieldWidths = 0
    for bi in self.__model.getBitfields(i):
      labelBitfieldName = QLabel()
      labelBitfieldName.setText(bi[0])
      
      position       = bi[1]
      bitFieldWidth  = bi[2]      
      bitFieldWidget = BitfieldWidget(self)
      bitFieldWidget.setModel(self.__model)

      # add bitfield widgets
      layoutRegister.addWidget(labelBitfieldName)
      layoutRegister.addWidget(bitFieldWidget.createWidget(i,position,bitFieldWidth))

      # store bitfield widget in list
      self.__actorBitfield.append(bitFieldWidget)
       
      cnt = cnt + 1 # index for bitfield actor objects
      
      # plausibility check
      sumBitfieldWidths = sumBitfieldWidths + bitFieldWidth
      
    if sumBitfieldWidths != 8:
      raise RuntimeError("Error: sum of all bitfield widths should be 8 but is {0}".format(sumBitfieldWidths))  

    self.__groupRegister = QGroupBox(self.tr("Register"))    
    self.__groupRegister.setLayout(layoutRegister)
    self.layout.addWidget(self.__groupRegister)
    
    self.updateUI()
    

  def slotRegisterValueChanged(self):
    """ slot for value change through spin box """
    
    # store full value in underlying model
    self.__model.setRegisterValue( self.__cmbSelectRegister.currentIndex(), self.__labelRegisterValue.value())
    # update the other objects
    self.updateUI()
   
  def updateUI(self):
    """ 
    update UI elements in Exercise widget and all subwidgets 
    
    Reads the data from the Model and sets the values of the GUI elements
    """
    regVal = int(self.__model.getRegisterValue(self.__cmbSelectRegister.currentIndex()).uint)
    self.__labelRegisterValue.setValue(regVal)  
    for actor in self.__actorBitfield:
      actor.updateUI()

  def testMe(self):
    """ Given a set of bitfields test whether GUI represents all values correctly """
    
    if self.__model.rowCount(self) != self.__cmbSelectRegister.count():
      raise RuntimeError("Error: Number of registers in GUI does not match number of registers in model")
      return False
      
    # loop over all registers
    for r in range(0, self.__model.rowCount(self)):
      self.__cmbSelectRegister.setCurrentIndex(r)
      
      name = "Register: " + self.__model.getRegisterName(r)
      if name != self.__labelRegisterName.text():
        raise RuntimeError("Error: Incorrect register name in label")
        return False
        
      address = "Address: 0x" + self.__model.getRegisterAddress(r).hex
      if address != self.__labelRegisterAddress.text():
        raise RuntimeError("Error: Incorrect register address in label")
        return False
        
      if self.__model.getNumberOfBitfields(r) != len(self.__actorBitfield):
        raise RuntimeError("Error: Inconsistent number of bitfields")
        return False
    
      # loop through all values
      for v in range(0,256):
        
        # set new value
        self.__labelRegisterValue.setValue(v)
        
        # check whether value is correctly stored in model
        if self.__model.getRegisterValue(r).uint != v:
          raise RuntimeError("Error: could not set new register value")
          return False
        
        # check all bitfield GUI elements for correct values
        for b in range(0,self.__model.getNumberOfBitfields(r)):
          bSuccess = self.__actorBitfield[b].testMe()
          if bSuccess == False:        
            raise RuntimeError("Error: bitfield tests failed")
            return False
            
          # testMe of bitfield widget should have changed value
          if self.__model.getRegisterValue(r).uint != self.__labelRegisterValue.value():
            raise RuntimeError("Error: register value does not match model data value")
            return False

      print("Test register " + str(r) + ": OK")    

    # all tests for all registers passed
    return True

if __name__ == '__main__':
  app = QApplication(sys.argv)
  mm = MyRegisterModel('HardwareLayerA')
  ex = ExerciseWindow()
  ex.setModel(mm)
  ex.show()
  sys.exit(app.exec())
