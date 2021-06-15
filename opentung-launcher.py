#!/usr/bin/python
import requests,os,json,subprocess,sys
from bs4 import BeautifulSoup
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def getCommitHash(website):
	return website.find("span").get_text()
if os.name == 'nt':
    os.environ["HOME"] = str(Path.home())
    pathsep = "\\"
else:
    pathsep = "/"
basepath = os.environ["HOME"] + pathsep + ".opentung"
site = requests.get("https://opentung.ecconia.com")
site = BeautifulSoup(site.text, "lxml")
currentcommit=getCommitHash(site)
if not os.path.exists(basepath):
    os.makedirs(basepath)
if not os.path.exists(basepath + pathsep + "launcher.txt"):
    with open(basepath + pathsep + "launcher.txt", "w") as f:
        f.write('{"commitHash":"currentcommit"}'.replace("currentcommit", currentcommit))
config = json.load(open(basepath + pathsep + "launcher.txt"))


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('main.ui', self) # Load the .ui file
        #Load button objects and set event handlers
        self.launchButton = self.findChild(QtWidgets.QPushButton, 'launchButton')
        self.launchButton.clicked.connect(self.launch)
        self.updateButton = self.findChild(QtWidgets.QPushButton, 'updateButton')
        self.updateButton.clicked.connect(self.update)
        self.installButton = self.findChild(QtWidgets.QPushButton, 'installButton')
        self.installButton.clicked.connect(self.install)
        #Load status bar
        self.statusBar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
        #Load world list and set world list
        self.worldList = self.findChild(QtWidgets.QListWidget, "worldList")
        self.worldList.addItem("New")
        self.worldList.setCurrentItem(self.worldList.item(0))
        try:
            self.worldList.addItems(os.listdir(basepath + pathsep + "OpenTUNG" + pathsep + "boards"))
        except:
            pass
        self.show() # Show the GUI
    def setStatus(self, message):
        self.statusBar.showMessage(message)
        QtWidgets.QApplication.processEvents()
    def launch(self):
        btn = self.launchButton
        btn.setText('Running OpenTUNG')
        QtWidgets.QApplication.processEvents()
        print("Would be launching if, y'know, it worked")
        olddir = os.getcwd()
        os.chdir(basepath)
        try:
            world = self.worldList.selectedItems()[0].text()
            if world == "New":
                cmdline = "java -jar OpenTUNG.jar"
            else:
                cmdline = "java -jar OpenTUNG.jar " + basepath + pathsep +  "OpenTUNG" + pathsep + "boards" + pathsep + world
        except:
            self.setStatus("WARN: Could not find selected world, defaulting to New!")
            cmdline = "java -jar OpenTUNG.jar"
        subprocess.run(cmdline, shell=True)
        os.chdir(olddir)
        btn.setText('Launch OpenTUNG')
        QtWidgets.QApplication.processEvents()
    def update(self):
        olddir = os.getcwd()
        os.chdir(basepath)
        if currentcommit == config["commitHash"]:
            self.setStatus("There is nothing to be done!")
        else:
            self.setStatus("Version mismatch! Updating to " + currentcommit + "!")
            r = requests.get("https://opentung.ecconia.com/OpenTUNG.jar")
            with open('OpenTUNG.jar', 'wb') as f:
                f.write(r.content)
            config["commitHash"] = currentcommit
            self.setStatus("Finished updating!")
        os.chdir(olddir)
        json.dump(config, open(basepath + "/launcher.txt", "w"))
    def install(self):
        olddir = os.getcwd()
        os.chdir(basepath)
        self.setStatus("Downloading OpenTUNG...")
        r = requests.get("https://opentung.ecconia.com/OpenTUNG.jar")
        self.setStatus("Writing OpenTUNG...")
        with open('OpenTUNG.jar', 'wb') as f:
            f.write(r.content)
        self.setStatus("Installed OpenTUNG!")
        os.chdir(olddir)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
