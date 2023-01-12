import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.utils import pp


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name_company = "None"
        self.name_product = 'KOS codegen'

        self.initUI()



    def initUI(self):

        self.createActions()
        self.createMenus()

        self.nodeeditor = NodeEditorWidget(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        #set window properties
        self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()

    def createStatusBar(self):
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)


    def createActions(self):
        self.actNew = QAction("&New",self, shortcut="Ctrl+N", statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction("&Open",self, shortcut="Ctrl+O", statusTip="Open File", triggered=self.onFileOpen)
        self.actSave = QAction("&Save",self, shortcut="Ctrl+S", statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction("Save &As",self, shortcut="Ctrl+Shift+S", statusTip="Save file as", triggered=self.onFileSaveAs)
        self.actExit = QAction("E&xit",self, shortcut="Ctrl+Q", statusTip="Create new graph", triggered=self.close)
        self.actUndo = QAction('&Undo',self, shortcut='Ctrl+Z', statusTip='Undo last operation', triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo',self, shortcut='Ctrl+Shift+Z', statusTip='Redo last operation', triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t',self, shortcut='Ctrl+X', statusTip='Cut to clipboard', triggered=self.onEditCut)
        self.actCopy = QAction('&Copy',self, shortcut='Ctrl+C', statusTip='Copy to clipboard', triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste',self, shortcut='Ctrl+V', statusTip='Paste to clipboard', triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete',self, shortcut='Del', statusTip='Delete selected items', triggered=self.onEditDelete)

    def createMenus(self):
        menuBar = self.menuBar()
        # init mune
        self.filemenu = menuBar.addMenu('&File')

        self.filemenu.addAction(self.actNew)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.actOpen)
        self.filemenu.addAction(self.actSave)
        self.filemenu.addAction(self.actSaveAs)
        self.filemenu.addAction(self.actExit)
        self.filemenu.addSeparator()

        self.editMenu = menuBar.addMenu("&Edit")
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)


    def setTitle(self):
        title = "Node Editor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.isModified()


    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()

    def maybeSave(self):
        if not self.isModified():
            return True
        res = QMessageBox.warning(self, 'Don`t forget to save',
                                  "The document has been modified.\n Do you want to save it?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False
        elif res == QMessageBox.Discard:
            return True
        return True

    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [{}, {}]".format(x, y))


    def onFileNew(self):
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()


    def onFileOpen(self):
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileload(fname)
                self.setTitle()

    def onFileSave(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None and current_nodeeditor.filename is not None:
            current_nodeeditor.filesave()
            self.statusBar().showMessage('Successfully saved {}'.format(current_nodeeditor.filename), 5000)

            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True
        else:
            return self.onFileSaveAs()


    def onFileSaveAs(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')

            if fname == '':
                return False
            current_nodeeditor.filesave(fname)
            self.statusBar().showMessage('Successfully saved as {}'.format(current_nodeeditor.filename), 5000)

            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True

    def onEditUndo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            #print(str_data)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()
            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print('Pasting of not valid json data. EXC:{}'.format(e))
                return
            # check json data are correct
            if 'nodes' not in data:
                print("JSON not contain nodes")
                return
            self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)


    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
