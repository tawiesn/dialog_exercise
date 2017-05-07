# dialog_exercise

### Content:

The project contains the following files

* ex_gui.py: general classes for GUI.
* ex_unittest.py: unit tests for all possible combinations of bitfields
* ex_demo.py: demonstration program

### Prerequisites

To run the programs you need the following python modules:

* PyQt5
* bitstring
* unittest
* itertools

### Run the program

Use
>$ python3 ./ex_gui.py

to run the main GUI for two sample device definitions. Note, that in line 495 you can switch from 'HardwareLayerA' to 'HardwareLayerB'

The unit tests are executed with
>$ python3 ./ex_unittest.py

You can play around with the EightBitDemoDevice created for the unit test with the demo program:
>$ python3 ./ex_demo.py
