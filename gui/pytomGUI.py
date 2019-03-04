#!/cm/shared/apps/python3/3.7/bin/python3.7
import sys
import os
import pickle, json
import numpy as np

global pytompath
pytompath = os.path.dirname(os.popen('dirname `which pytom`').read()[:-1])
print(pytompath)

if not pytompath:
    print('Pytom package is not available. Please load, or install Pytom.')
    sys.exit()

def update_env_vars(pytompath):
    '''Make sure all pytom functionality can be imported from within the script. '''
    if 0:
        from pytom_volume import read
    else:
        update_vars = False
        for search in ('LD_LIBRARY_PATH','PATH','PYTHONPATH'):
            # Check if env vars include all paths set in paths.csh
            query_string = "cat {}/bin/paths.csh | grep 'setenv {}' | grep -v '${}'".format(pytompath, search,search)
            string = os.popen(query_string).read()[:-1].split()[-1]
            for new_lib in (string.split(':')):
                new_lib = new_lib.replace("'","")

                if not new_lib in os.environ[search].split(':'):
                    os.environ[search] += ':'+new_lib
                    update_vars = True
        #If any of the env vars are updated reopen this script.
        if update_vars:
            if len(sys.argv) < 2:
                python3 = os.popen('which python3').read()[-1]
                sys.argv = [python3] + sys.argv
            os.execv(sys.argv[0],sys.argv)
            #os.execv('/cm/shared/apps/python3/3.7/bin/python3.7', sys.argv)
update_env_vars(pytompath)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

from pytom.gui.guiStyleSheets import *
from pytom.gui.frameDataTransfer import *#CollectPreprocess, TomographReconstruct, CommonFunctions
from pytom.gui.frameTomographicReconstruction import TomographReconstruct
from pytom.gui.frameParticlePicking import ParticlePick
from pytom.gui.frameSubtomogramAnalysis import SubtomoAnalysis

class NewProject(QMainWindow, CommonFunctions):
    '''This class creates a new windows for browsing'''
    def __init__(self,parent,label):
        super(NewProject, self).__init__(parent)
        self.setGeometry(50, 50, 300, 100)
        self.cwidget = QWidget()
        self.gridLayout = QGridLayout()
        self.setWindowModality(Qt.ApplicationModal)



        #self.gridLayout.setContentrsMargins(10, 10, 10, 10)
        self.label = label
        self.setStyleSheet('background: #{};'.format(self.parent().middlec) )
        self.cwidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.cwidget)
        self.fill()


    def fill(self):
        columns, rows = 5, 5

        self.items, self.widgets = [['', ] * columns, ] * rows, {}
        parent = self.gridLayout

        self.row, self.column = 0, 1
        self.insert_label(parent, text='Project name', rstep=1, alignment=QtCore.Qt.AlignHCenter,
                          tooltip='Provide the foldername of a new project. The foldername must not exist.')
        self.insert_lineedit(parent, 'projectname', cstep=1)
        self.insert_pushbutton(parent, cstep=self.column * -1+1, rstep=1, text='Browse',
                               action=self.browse, params=['folder', self.items[self.row][self.column - 1], ''])
        self.insert_pushbutton(parent, cstep=self.column * -1+1, rstep=1, text='Create',
                               action=self.return_value)

    def return_value(self,params):
        path = self.widgets['projectname'].text()

        if os.path.exists(path):
            QMessageBox().warning(self, "Folder exists",
                                   "Please provide a non existing folder name.", QMessageBox.Ok)
        else:

            self.label.setText(path)
            self.close()




class menudemo(QMainWindow, CommonFunctions):
    resized=pyqtSignal()
    def __init__(self, parent=None):
        super(menudemo, self).__init__(parent)
        self.size_policies()
        self.setGeometry(0,0, 300, 100)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        print(pytompath)
        self.pytompath=pytompath

        y,b,g,w = 'f9ce00', '343434', 'cacaca','fcfaf1'
        ly = 'f4e8c1'
        green = 'a0c1b8'
        gr = '5c636e'
        bl='1989ac'
        lg = 'f6f6f6'
        r = '970747'
        gg = '00818a'
        lb = 'bbf1fd'
        yy = 'f4e033'
        tt = 'bbf1fd'
        self.bars = bl
        self.mainc = w
        self.middlec = lg
        #oImage = QImage("background11.jpg")
        #sImage = oImage.scaled(QSize(1920,1080))  # resize Image to widgets size
        #palette = QPalette()
        #palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        #self.setPalette(palette)

        self.setStyleSheet('background: #{};'.format(self.mainc))
        bar=self.menuBar()
        bar.setStyleSheet('selection-background-color: #1989ac;')
        tb = QToolBar()
        tb.setStyleSheet('background: #{};'.format(self.bars))
        self.addToolBar(tb)

        new=QAction(QIcon("{}/gui/Icons/new_project4.png".format(self.pytompath)),"Create New Project",self)
        tb.addAction(new)
        load=QAction(QIcon("{}/gui/Icons/open_project4.png".format(self.pytompath)),"Load Project",self)
        tb.addAction(load)

        save = QAction(QIcon("{}/gui/Icons/save_project4.png".format(self.pytompath)), "Save Project", self)
        tb.addAction(save)

        settings = QAction(QIcon("{}/gui/Icons/cogwheel.png".format(self.pytompath)), "Open Settings", self)
        tb.insertSeparator(settings)
        tb.addAction(settings)

        tb.actionTriggered[QAction].connect(self.processtrigger)

        self.logbook = {}
        dropdown = []

        self.targets =  ( (  'CollectPreprocess',  "Data Transfer" ),
                          ('TomographReconstruct', "Tomographic Reconstruction"),
                          ('ParticlePick',         "Particle Picking" ),
                          ('SubtomoAnalysis',      "Subtomogram Analysis"))

        self.drf = ("File",('New','Open','Save','Quit'))
        self.drs = ("Enable Stage",("Tomographic Reconstruction", "Particle Picking", "Subtomogram Analysis") )
        for name,actionlist in (self.drf,self.drs): 

            dropdown.append(bar.addMenu(name))
            for subname in actionlist:
                
                action=QAction(subname,self)

                dropdown[-1].addAction(action)

                dropdown[-1].triggered[QAction].connect(self.processtrigger)

        self.sbar = QStatusBar(self)
        self.sbar.setStyleSheet('background: #{}'.format(self.bars))
        # self.statusBar.setLayout(QHBoxLayout())
        self.setStatusBar(self.sbar)
        self.sbar.setSizeGripEnabled(False)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(menudemo, self).resizeEvent(event)

    def sizetest(self):
        w = self.splitter.frameGeometry().width()
        h  = self.splitter.frameGeometry().height()
        for frame in (self.CD, self.TR, self.PP, self.SA):
            for scrollarea in frame.scrollareas:
                scrollarea.resize(w-280,h-20)

    def init_size(self,w,h):
        self.resize(1200, 800)
        for frame in (self.CD, self.TR, self.PP, self.SA):
            for n, scrollarea in enumerate( frame.scrollareas):
                scrollarea.resize(w-280-frame.scrolloffset[n]/2,h-80-frame.scrolloffset[n])

    def save_logfile(self):

        with open(os.path.join(self.projectname, 'logfile.js'),'w') as f:
                json.dump(self.logbook, f, indent=4, sort_keys=True)
        #np.save('logfile.npy', self.logbook)

    def load_logfile(self,logfile):
        with open(logfile) as f:
            self.logbook = json.load(f)

    def is_pytomgui_project(self, projectname):
        if os.path.exists(os.path.join(projectname, 'logfile.js')):

            self.load_logfile(os.path.join(projectname, 'logfile.js'))
            return True
        if os.path.exists(os.path.join(projectname, 'logfile.pickle'))  :
            for t, text in self.targets:
                self.logbook['00_framebutton_{}'.format(t)] = (t == self.targets[0][0])
            return True

        return False

    def processtrigger(self,q):

        if q.text() == 'Create New Project': self.new_project()
        elif q.text() == 'Load Project':     self.open_project()
        elif q.text() == 'Quit':             sys.exit()
        elif q.text() == 'Open Settings':    self.open_settings()
        elif q.text() == 'Save Project':     self.save_logfile()
        else:
            for n, subname in enumerate(self.drs[1]):
                if q.text() == subname:
                    self.stage_buttons[n+1].setEnabled(True)
                    self.logbook['00_framebutton_{}'.format(self.targets[n+1][0])] = True

    def new_project(self):

        self.projectname = ''
        self.label = QLineEdit(self)
        self.label.textChanged.connect(lambda ignore: self.go_you())
        widget = NewProject(self,self.label)
        widget.show()

    def open_settings(self):
        self.generalSettings = GeneralSettings(self)
        self.generalSettings.show()

    def go_you(self):
        self.projectname = os.path.join(os.getcwd(), self.label.text())

        os.mkdir(self.projectname)
        self.setWindowTitle(basename(self.projectname))
        self.logbook = {}
        for t, text in self.targets:
            self.logbook['00_framebutton_{}'.format(t)] = (t == self.targets[0][0])

        guiFunctions.create_project_filestructure(projectdir=self.projectname)
        self.save_logfile()
        self.run_project()
        #dialog = QFileDialog(self, 'Create Project', './')
        #dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        
    def open_project(self):
        
        self.projectname = QFileDialog.getExistingDirectory(self, 'Open file', os.getcwd())

        if len(self.projectname) < 2:
            pass
        elif self.is_pytomgui_project(self.projectname) == False:

            QMessageBox().critical(self, "Invalid projectname",
                                "The selected folder does not contain a valid pytomGUI structure", QMessageBox.Ok)
            #error_dialog.showMessage('The folder you selected does not contain a valid pytomGUI folder structure.')

        elif self.projectname and self.is_pytomgui_project(self.projectname):
            #self.destroy(error_dialog)
            self.setWindowTitle(basename(self.projectname))
            self.run_project()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_N:
            self.new_project()
        if e.key() == Qt.Key_O:
            self.open_project()

    def run_project(self):

        self.rawnanographs_folder = os.path.join(self.projectname, '01_Raw_Nanographs')
        self.motioncor_folder = os.path.join(self.projectname, '02_Preprocessed_Nanographs/Motion_corrected')
        self.ctf_folder = os.path.join(self.projectname, '02_Preprocessed_Nanographs/CTF_corrected')
        self.tomogram_folder = os.path.join(self.projectname, '03_Tomographic_Reconstruction')
        self.particlepick_folder = os.path.join(self.projectname, '04_Particle_Picking')
        self.subtomo_folder = os.path.join(self.projectname, '05_Subtomogram_Analysis')

        topleft = QFrame()
        topleft.setSizePolicy(self.sizePolicyC)
        topleft.setFixedWidth(250)

        #topleft.setGeometry(20,20,0,0)
        self.topleft_layout = QVBoxLayout(topleft)

        self.topleft_layout.setContentsMargins(10,80,10,30)
        self.topleft_layout.setSpacing(30)

        self.stage_buttons = []
        self.topright = QStackedWidget(self)

        self.topright.setContentsMargins(10,10,10,10)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)

        #sizePolicy.setHeightForWidth(self.topright.sizePolicy().hasHeightForWidth())
        self.topright.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.CD = CollectPreprocess(self)
        self.TR = TomographReconstruct(self)
        self.PP = ParticlePick(self)
        self.SA = SubtomoAnalysis(self)
        self.topright.addWidget(self.CD)
        self.topright.addWidget(self.TR)
        self.topright.addWidget(self.PP)
        self.topright.addWidget(self.SA)
        #self.topright.setSizePolicy(self.sizePolicyB)
        self.topright.setCurrentIndex(2)
        self.CD.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.CD.scrollarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.CD.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(self.topright)

        #splitter1.addWidget(dummy)
        #splitter1.setSizes([100,1000])


                          #('Segmentation',         "Segmentation") )


        self.iconnames = [os.path.join(self.pytompath, 'gui/Icons/td.png'),
                          os.path.join(self.pytompath, 'gui/Icons/recon.png'),
                          os.path.join(self.pytompath, 'gui/Icons/sa3.png'),
                          os.path.join(self.pytompath, 'gui/Icons/pp.jpg')]

        for nn,(i,n) in enumerate(self.targets):
            widget = QPushButton(n)

            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
            widget.setSizePolicy(sizePolicy)
            #self.topleft_layout.addStretch(0)
            self.stage_buttons.append(widget)
            self.stage_buttons[-1].clicked.connect(lambda ignore, index=nn: self.showpage(index))
            self.topleft_layout.addWidget(self.stage_buttons[-1])
            if nn >0:
                try:
                    self.stage_buttons[-1].setEnabled(self.logbook['00_framebutton_{}'.format(i)])
                except:
                    self.logbook['00_framebutton_{}'.format(i)] = False
                    self.stage_buttons[-1].setEnabled(False)

            icon = QtGui.QIcon(self.iconnames[nn])
            widget.setIcon(icon)

        self.topleft_layout.addWidget(QLabel(''), Qt.AlignHCenter)

        self.image = QWidget(self)
        self.imagelayout = QVBoxLayout()
        self.transfer_data = QLabel()
        pixmap = QPixmap(self.iconnames[0])
        #pixmap = pixmap.scaledToWidth(225)  # scaled(300, 200, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.transfer_data.setPixmap(pixmap)
        self.imagelayout.addWidget(self.transfer_data)
        self.image.setLayout(self.imagelayout)
        centralFrame = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter1)
        centralFrame.setLayout(central_layout)
        self.topleft_layout.addWidget(self.image,alignment=Qt.AlignHCenter)
        self.splitter = splitter1
        self.resized.connect(self.sizetest)
        self.setCentralWidget(self.splitter)
        self.init_size(1200,800)

    def showpage(self, index):
        self.topright.setCurrentIndex(index)
        self.image.setParent(None)
        self.image = QWidget(self)
        self.imagelayout = QVBoxLayout()
        self.transfer_data = QLabel()
        pixmap = QPixmap(self.iconnames[index])
        self.transfer_data.setPixmap(pixmap)
        self.image.setSizePolicy(self.sizePolicyC)
        self.imagelayout.addWidget(self.transfer_data)
        self.image.setLayout(self.imagelayout)

        self.topleft_layout.addWidget(self.image,alignment=Qt.AlignHCenter)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon('/Users/gijs/Documents/PostDocUtrecht/GUI/pp.jpg'))
    ex = menudemo()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
