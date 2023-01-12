from PyQt5.QtGui import *
from kos_sub_window import KOSSubWindow
from nodeeditor.node_editor_window import NodeEditorWindow
from kos_drag_listbox import QDMDragListBox
from kos_conf_nodes import *
from kos_code_generator import *
SubWindowView = 0
TabbedView = 1

DEBUG = False

class KOSWindow(NodeEditorWindow):
    def initUI(self):
        self.name_company = "None"
        self.name_product = 'KOS codegen'

        self.empty_icon = QIcon(".")
        if DEBUG:
            print('Register node')
            pp(KOS_NODES)
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.mdiArea.setViewMode(TabbedView)
        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createNodesDock()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()
        self.readSettings()

        self.setWindowTitle("KOS Codegen")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()


    def createNodesDock(self):
        self.nodeListWidget = QDMDragListBox()
        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodeListWidget)
        self.nodesDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)


    def about(self):
        QMessageBox.about(self, "About KOS Codegen",
                          "The <b>KOS Codegen</b> is software to generate security policies for KasperskyOS.<br> "
                          "Based on Python & PyQt5"
                          "Control Keys:"
                          "Wheel down - move scene"
                          "Left click - select item/items"
                          "Right click on widget name - rename it")

    def createActions(self):
        super().createActions()
        self.actClose = QAction("Cl&ose", self,statusTip="Close the active window",triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self,statusTip="Close all the windows",triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows",triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows",triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,statusTip="Move the focus to the next window",triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self,shortcut=QKeySequence.PreviousChild,statusTip="Move the focus to the previous window",triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)
        self.exportAct = QAction("&Export", self,statusTip="Generate KOS files", triggered=self.exportMenu)
        self.aboutAct = QAction("&About", self,statusTip="Show the application's About box", triggered=self.about)

    def createMenus(self):
        super().createMenus()

        self.export = self.menuBar().addMenu("&Export")
        self.export.addAction(self.exportAct)
        self.export.aboutToShow.connect(self.updateMenus)
        self.menuBar().addSeparator()
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def exportMenu(self):
        if self.maybeSave():
            if ExportKosCode(self.getCurrentNodeEditorWidget()):
                QMessageBox.information(self,'Export result',
                                          "Export successful", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Export result',
                                        "Export failed. Check fail.txt", QMessageBox.Ok)
        else:
            if self.getCurrentNodeEditorWidget().filename is not None:
                if ExportKosCode(self.getCurrentNodeEditorWidget()):
                    QMessageBox.information(self, 'Export result',
                                            "Export successful", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, 'Export result',
                                        "Export failed. Check fail.txt", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Can`t export',
                                    "Export failed. Please save graph as file", QMessageBox.Ok)
    def updateMenus(self):
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)
        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actPaste.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)
        self.export.setEnabled(hasMdiChild)
        self.updateEditMenu()

    def updateEditMenu(self):
        try:
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)
            self.actPaste.setEnabled(hasMdiChild)


            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e: dumpException(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()


    def getCurrentNodeEditorWidget(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def createToolBars(self):
        pass

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else KOSSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        #nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        #nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def onFileNew(self):
        subwnd = self.createMdiChild()
        subwnd.widget().fileNew()
        subwnd.show()

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file')
        try:
            for fname in fnames:
                existing = self.findMdiChild(fname)
                if existing:
                    self.mdiArea.setActiveSubWindow(existing)
                else:
                    nodeeditor = KOSSubWindow()
                    if nodeeditor.fileload(fname):
                        self.statusBar().showMessage('File {} loaded'.format(fname), 5000)
                        nodeeditor.setTitle()
                        subwnd = self.createMdiChild(nodeeditor)
                        subwnd.show()
                    else:
                        nodeeditor.close()
        except Exception as e: dumpException(e)


