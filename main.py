import typing
from PyQt5.QtWidgets import QApplication
#from controler.mainWind import myWin

from controler.mainWind_withThread import myWin
import sys

import sys
# sys.coinit_flags=2
# import pythoncom

app=QApplication(sys.argv)
mw=myWin()
mw.show()
sys.exit(app.exec_())

