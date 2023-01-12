import traceback
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint



def dumpException(e):
    print("EXCEPTION: {}".format(e))
    traceback.print_tb(e.__traceback__)


def loadStyleSheet( filename):
    #print('Style loading: {}'.format(filename))
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))


