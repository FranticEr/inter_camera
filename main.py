import typing
from view.Ui_base_0 import Ui_MainWindow

from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget,QMainWindow,QMessageBox
import sys
from PyQt5.QtCore import QStringListModel
from PyQt5.QtMultimedia import (QCameraInfo,QCameraImageCapture,
      QImageEncoderSettings,QMultimedia,QVideoFrame,QSound,QCamera)
from PyQt5.QtGui import QPixmap 
from PyQt5.QtGui import QImage
from model.intercamera import Camera
import cv2
class myWin(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.Record_Button.clicked.connect(self.record)
        self.Start_Button.clicked.connect(self.start)
        self.Stop_Button.clicked.connect(self.stop)
        self.getCameralist_Button.clicked.connect(self.getCameralist)
        self.inter_camer=Camera()

    def getCameralist(self):
        self.listModel=QStringListModel()
        self.camera_list = QCameraInfo.availableCameras()
        list=[]
        for camera in self.camera_list:
            list.append(camera.description()) 
        self.listModel.setStringList(list)
        self.listView.setModel(self.listModel)
        pass
    def record(self):
        self.Record_Button.setEnabled(False)
        self.Start_Button.setEnabled(False)
        self.Stop_Button.setEnabled(True)
        pass
    # def start(self):
    #     camera_devices = QCameraInfo.availableCameras()
    #     camera_info = camera_devices[1]
    #     self.camera = QCamera(camera_info)
    #     self.camera.setCaptureMode(QCamera.CaptureMode.CaptureStillImage)
    #     self.camera.setViewfinder(self.widget)
    #     self.capture=QCameraImageCapture(self.camera)
    #     self.camera.start()
    # def start(self):
    #     self.showcamera=True
    #     while self.showcamera:  
    #         color_image, depth_image, colorizer_depth = self.inter_camer.get_frame() # 读取一帧图像  
            
    #         rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # 将BGR格式转换为RGB格式  
    #         qpixmap = QPixmap.fromImage(rgb_frame)  # 将RGB格式的图像转换为QPixmap对象  
    #         self.label.setPixmap(qpixmap)  # 将QPixmap对象显示在标签上
    #     pass
    def start(self):
        self.showcamera = True
        while self.showcamera:
            color_image, depth_image, colorizer_depth = self.inter_camer.get_frame()  # 读取一帧图像

            rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # 将BGR格式转换为RGB格式

            # 创建 QImage 对象
            image = QImage(rgb_frame.data,
                        rgb_frame.shape[1],
                        rgb_frame.shape[0],
                        QImage.Format_RGB888)

            # 创建 QPixmap 对象
            qpixmap = QPixmap.fromImage(image)  # 将RGB格式的图像转换为QPixmap对象

            # 将QPixmap对象显示在标签上
            self.label.setPixmap(qpixmap)
            self.Record_Button.setEnabled(False)
            self.Start_Button.setEnabled(False)
            self.Stop_Button.setEnabled(True)

            QApplication.processEvents()
        pass
    def stop(self):
        self.showcamera=False
        self.Record_Button.setEnabled(True)
        self.Start_Button.setEnabled(True)
        self.Stop_Button.setEnabled(False)
        # self.camera.stop()
        # self.camera = None
        pass




app=QApplication(sys.argv)
mywin=myWin()
mywin.show()
sys.exit(app.exec_())
