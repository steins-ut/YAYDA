from PyQt5 import QtWidgets, QtCore, QtGui
from YAYDA_MainWindow_Design2 import Ui_MainWindow
import youtube_dl as ydl

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.btnAdd.clicked.connect(self.checkURL)
        self.btnRemove.clicked.connect(self.removeURL)
        self.btnConvert.clicked.connect(self.convertURL)
        self.treeLink.setHeaderLabels(["URL", "Format", "Percentage", "ETA"])
        self.comboBox.addItems(["Video", "Audio"])

        self.urlList = []

    def btnSetEnabled(self):

        newState = not self.btnAdd.isEnabled()

        self.btnAdd.setEnabled(newState)
        self.btnRemove.setEnabled(newState)
        self.btnConvert.setEnabled(newState)
        self.btnSettings.setEnabled(newState)

    def checkURL(self):
        self.btnSetEnabled()
        val = self.plainTextLinks.toPlainText()
        valSplit = val.split("\n")
        for url in valSplit:
            self.ydlThread = YDLThread(url, {}, False)
            self.ydlThread.seturl(url)
            self.ydlThread.start()

    def removeURL(self):
        selectedItems = self.treeLink.selectedItems()
        if selectedItems:
            for item in selectedItems:
                self.treeLink.invisibleRootItem().removeChild(item)
                self.urlList.remove(item)
        else:
            QtWidgets.QMessageBox.critical(self.window(), "Error", "No item is selected.")

    def convertURL(self):
        self.ydlThread = YDLThread("", {}, True)
        self.ydlThread.start()


class YDLLogger(object):
    def debug(self, msg):
        window.textLog.setTextColor(QtGui.QColor(0, 0, 255))
        window.textLog.append(msg)

    def warning(self, msg):
        window.textLog.setTextColor(QtGui.QColor(255, 255, 0))
        window.textLog.append(msg)

    def error(self, msg):
        window.textLog.setTextColor(QtGui.QColor(255, 0, 0))
        window.textLog.append(msg)

class YDLThread(QtCore.QThread):

    addSignal = QtCore.pyqtSignal(str)

    def __init__(self, url = "", ydl_opts = {}, download = False):
        QtCore.QThread.__init__(self)
        self.logger = YDLLogger()
        self.url = url
        self.ydl_opts = ydl_opts
        self.ydl_opts['logger'] = self.logger
        self.download = download

    def seturl(self, url):
        self.url = url

    def setydl_opts(self, ydl_opts):
        self.ydl_opts = ydl_opts

    def setdownload(self, download):
        self.download = download

    def __del__(self):
        self.wait()

    def run(self):
        treeIndex = 0
        with ydl.YoutubeDL(self.ydl_opts) as ydler:
            try:
                if self.download == False:
                    info_dict = ydler.extract_info(self.url, self.download)
                    self.logger.debug('[YAYDA] Added URL: "' + self.url + '"')
                    window.btnSetEnabled()
                    window.urlList.append(QtWidgets.QTreeWidgetItem(window.treeLink, [self.url, window.comboBox.currentText()]))
                else:
                    root = window.treeLink.invisibleRootItem()
                    if root.childCount() != 0:
                        errorCount = 0
                        for i in range(root.childCount()):
                            treeIndex = i;
                            self.url = root.child(i).text(0)
                            ydl_opts = {
                                'outtmpl': "%(title)s.%(ext)s",
                                'postprocessors': [
                                    {'key': 'FFmpegMetadata'},
                                ],
                                'logger': YDLLogger(),
                            }
                            if (root.child(i).text(1) == "Video"):
                                ydl_opts["format"] = "best/bestvideo+bestaudio"
                            else:
                                ydl_opts["format"] = "bestaudio"
                                ydl_opts["postprocessors"] = [
                                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
                                     'preferredquality': '192',
                                     },
                                    {'key': 'FFmpegMetadata'},
                                ]

                            try:
                                info_dict = ydler.extract_info(self.url, self.download)

                            except Exception as ex:
                                root.child(i).addChild(QtWidgets.QTreeWidgetItem(root.child(i), [ex.__str__()]))
                                errorCount += 1

                        QtWidgets.QMessageBox.information(window, "Operations finished",
                                                          "All operations are done with " + str(
                                                              errorCount) + " errors!")
                    else:
                        QtWidgets.QMessageBox.critical(window, "Error", "There are no videos to convert!")
            except:
                window.btnSetEnabled()
                pass



    def hookHandler(self, hookDictionary):
        if (hookDictionary['status']) == "finished":
            print("")
            #self.treeLink.invisibleRootItem().child(self.treeIndex).setText(2, "100%")
            #self.treeLink.invisibleRootItem().child(self.treeIndex).setText(3, "Finished!")
        elif (hookDictionary['status']) == "downloading":
            print("")
            #self.treeLink.invisibleRootItem().child(self.treeIndex).setText(2, str(
            #int(hookDictionary['downloaded_bytes'] / hookDictionary['total_bytes'] * 100)) + "%")
            #self.treeLink.invisibleRootItem().child(self.treeIndex).setText(3, "Downloading...")

if __name__ == "__main__":
    import sys

    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())