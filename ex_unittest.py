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

app = QApplication(sys.argv)


class EightBitDemoDevice:  
  """ Hardware interface layer for 8bit demo device """
 
  def subset_sum(self, numbers, target, partial=[],result=[]):
    """ Recursive helper function to collect all possible summands """
    s = sum(partial)
    # check if the partial sum is equals to target
    if s == target: 
      result.append(partial)
    if s >= target:
      return  # if we reach the number why bother to continue

    for i in range(len(numbers)):
      n = numbers[i]
      remaining = numbers[i+1:]
      self.subset_sum(remaining, target, partial + [n],result) 

  def generate_bitfields(self):
    """ helper function which generates all possible lists of sums of 8
        with summands in increasing ordering. For each list of summands
        we generate all permutations and store them in one big list of
        lists
    """
    res = []
    # build all subset sums (with summands of increasing size)
    self.subset_sum([1,1,1,1,1,1,1,1,2,2,2,2,3,3,4,4,5,6,7,8],8,[],res)

    # permute all subset sums (to have all cases with random ordering of summands)
    final = []
    for r in res:
      perm = itertools.permutations(r)
      uniq_res = [list(t) for t in set(map(tuple, list(perm)))]
      for s in uniq_res:
        final.append(s)
    uniq_final = [list(t) for t in set(map(tuple, final))]    
    return uniq_final
 
 
  def generate_register(self, regAddress, bitfieldWidths):
    """ helper function generates a register entry for a given bitfield array """
    register = []
    register.append("reg {0}".format(regAddress))
    register.append(BitArray(int=regAddress, length=16))
    bitfields = []
    b = 0
    for i in bitfieldWidths:
      bf = []
      bf.append("bit {0}-{1}".format(b,b+i-1))
      bf.append(b)
      bf.append(i)
      b = b + i
      bitfields.append(bf)
    register.append(bitfields)
    register.append(BitArray(int=0, length=8))  
    
    return register
    
  def build_8bit_demo_device(self): 
    """ build demo device containing all combination of GUI elements for 8 bit data """

    # generate all bitfield combinations
    bitfieldcombinations = self.generate_bitfields()
    
    # determine number of registers (1 per bitfield variation)
    numRegisters = len(bitfieldcombinations)
    
    # collect all registers
    deviceregisters = []
    for i in range(0,numRegisters):
      reg = self.generate_register(i,bitfieldcombinations[i])
      deviceregisters.append(reg)
  
    self.my_data = deviceregisters
    
  def loadData(self):
    # generate demo device and return it
    self.build_8bit_demo_device()
    return self.my_data
    
  def storeData(self, data):
    self.my_data = data
    
    for i in range(0,len(self.my_data)):
      print("Register 0x{0: <4}: {1: <7} = 0b{2}".format(BitArray(int=i, length=16).hex,self.my_data[i][0],self.my_data[i][3].bin))
      
class DefectDeviceA:  
  def loadData(self):
    data = [[42, BitArray(int = 1, length=16), # integer as a name
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 7]
        ],
        BitArray('0b00000000')
      ]]
    return data 
  def storeData(self, data):
    print ("")
    
class DefectDeviceB:  
  def loadData(self):
    data = [["defect", 66666, # wrong address 
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 7]
        ],
        BitArray('0b00000000')
      ]]
    return data
    
  def storeData(self, data):
    print ("")    
    
class DefectDeviceC:  
  def loadData(self):
    data = [["defect", BitArray(int = 1, length=16), 
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 22] # wrong bitfield width
        ],
        BitArray('0b00000000')
      ]]
    return data
    
  def storeData(self, data):
    print ("")        
  
class DefectDeviceD:  
  def loadData(self):
    data = [["defect", BitArray(int = 1, length=16), 
        [
        ["bit 0", 0, 1],
        ["bits 1-7", 1, 7]
        ],
        "DEFECT"  # not a BitArray
      ]]
    return data
    
  def storeData(self, data):
    print ("")          
  
class ExerciseTest(unittest.TestCase):
  """ Unit test for Exercise GUI """
  def setUp(self):
    """ Create the GUI """
    self.form  = ExerciseWindow()
 
  def test_defaults(self):
    """ Test GUI """
    demodevice = EightBitDemoDevice()
    self.model = MyRegisterModel(demodevice)
    self.form.setModel(self.model)
    self.assertEqual(self.form.testMe(), True)

  def test_defectA(self):
    """ Test Defect devices """
    for demodevice in {DefectDeviceA(),DefectDeviceB(),DefectDeviceC(),DefectDeviceD()}:
      self.model = MyRegisterModel(demodevice)
      self.assertRaises(TypeError, self.form.testMe, self.model)
        
if __name__ == "__main__":
  unittest.main()
