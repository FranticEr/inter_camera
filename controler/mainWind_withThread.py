
import typing
from PyQt5 import QtGui,QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel,QThreadPool,QThread,pyqtSignal,QObject, QRunnable
from PyQt5.QtWidgets import  QMainWindow
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtGui import QImage,QPixmap 



import os
import sys
from time import time

import h5py
import cv2

from model.intercamera import Camera
from view.layout.Ui_base_0 import Ui_MainWindow




# class mywidget(QMainWindow,Ui_MainWindow):
#     def __init__(self, parent=None) -> None:
#         super().__init__(parent)
#         self.setupUi(self)
#         self.RecordFolderButton.clicked.connect(self.folder)
        
#     def folder(self):
#         print("ssss")
#         m = QtWidgets.QFileDialog.getExistingDirectory(self,"选取文件夹","C:/")  # 起始路径


class WorkThread(QThread):
    update_data=pyqtSignal(object,object,object)
    def __init__(self,fps=30, w= 1280, h = 720, parent: QObject | None = None) -> None:
        super().__init__(parent)

        #控制线程的标志位
        self.run_flag=True
        self.ispause=False


        self.fps=fps
        self.w=w
        self.h=h
    def run(self):
        self.camera=Camera(fps=self.fps,width=self.w,height=self.h)
        while self.run_flag:
            if not self.ispause:
                color_image, depth_image, colorizer_depth=self.camera.get_frame()
                self.update_data.emit(color_image, depth_image, colorizer_depth)
            pass
        pass

    #停止
    def stop(self):
        self.run_flag=False
        self.camera.release()
        pass
    #暂停
    def pause(self):
        self.ispause=True
        pass
    #继续
    def continueT(self):
        self.ispause=False
        pass

    #设置录像文件地址
    def setRecordPath(self,recordPath):
        pass

    #录像
    def recordFrames(self):
        pass


class recordThread(QThread):
    
    def __init__(self,recordFolder ,parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.recordFolder=os.mkdir(os.path.join(recordFolder,int(time())))

        #存储路径
        self.video_path=os.path.join(self.recordFolder,"rgb.mp4")
        self.depth_path=os.path.join(self.recordFolder,"depthcolor.mp4")
        self.depth16_path=os.path.join(self.recordFolder,"depth16.h5")

        self.recoding=False
        self.queue=[]
    def start_recording(self):
        self.recording=True
        pass
    def add_frame(self,frame):
        self.queue.append(frame)
        pass
    def stop_recording(self):
        self.recoding=False
    def run(self):
         while True:
            if self.recording and len(self.queue) > 0:
                frame = self.queue.pop(0) 
            else:
                # 任务不占用主界面时间，可以进行其他操作
                pass





class myWin(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)


        self.Record_Button.clicked.connect(self.record)
        self.Start_Button.clicked.connect(self.start)
        self.Stop_Button.clicked.connect(self.stop)
        self.pauseButton.clicked.connect(self.pause)

        # self.RecordFolderButton.clicked.connect(self.folderChose)
        # self.getCameralist_Button.clicked.connect(self.getCameralist)

        self.inter_camer=Camera()
        
        self.workthread=None
        self.recordFolder="D:\inter_re"

        self.isrecord=False

        self.mp4 = cv2.VideoWriter_fourcc(*'mp4v')   # 视频格式

    # def getCameralist(self):
    #     self.listModel=QStringListModel()
    #     self.camera_list = QCameraInfo.availableCameras()
    #     list=[]
    #     for camera in self.camera_list:
    #         list.append(camera.description()) 
    #     self.listModel.setStringList(list)
    #     self.listView.setModel(self.listModel)
        pass
    
    def record(self):

        #按钮状态
        self.Record_Button.setEnabled(False)
        self.Start_Button.setEnabled(False)
        self.Stop_Button.setEnabled(True)

        #启动子线程
        #record_thread=recordThread()
        self.fps=30
        self.w=1280
        self.h=720
        #存储路径
        self.video_path=os.path.join(self.recordFolder,"rgb.mp4")
        self.depth_path=os.path.join(self.recordFolder,"depthcolor.mp4")
        self.depth16_path=os.path.join(self.recordFolder,"depth16.h5")

        #录制器
        self.wr = cv2.VideoWriter(self.video_path, self.mp4, self.fps, (self.w, self.h), isColor=True)
        self.wr_colordepth = cv2.VideoWriter(self.depth_path, self.mp4, self.fps, (self.w, self.h), isColor=True)
        self.wr_depth = h5py.File(self.depth16_path, 'w')

        os.mkdir(os.path.join(self.recordFolder,str(int(time()))))
        

        self.id  = 0
        self.isrecord=True

        pass
    # def folderChose(self):
    #     print("record")
    #     m = QtWidgets.QFileDialog.getExistingDirectory(self,"选取文件夹","C:/")
    #     self.recordFolder=QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹",r"C:/")
        
        pass
    def start(self):
        if self.workthread==None:
            print("isNone")
            self.workthread=WorkThread()
            self.workthread.update_data.connect(self.handleDisplay)
            self.workthread.update_data.connect(self.recordFrames)
            self.workthread.start()
        if self.workthread.ispause==True:
            self.workthread.continueT()
        
        self.Start_Button.setEnabled(False)
        self.Stop_Button.setEnabled(True)
        pass
    def recordFrames(self,color_image, depth_image, colorizer_depth):

        pass

    def handleDisplay(self,color_image, depth_image, colorizer_depth):
        rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # 将BGR格式转换为RGB格式

        
        

        # 创建 QImage 对象
        image = QImage(rgb_frame.data,
                    rgb_frame.shape[1],
                    rgb_frame.shape[0],
                    QImage.Format_RGB888)
        

        if self.isrecord==True:
            print(self.id)
            self.wr.write(color_image)
            self.wr_colordepth.write(colorizer_depth)

            depth16_image = cv2.imencode('.png', depth_image)[1]
            depth_map_name = str(self.id).zfill(5) + '_depth.png'
            self.wr_depth[depth_map_name] = depth16_image
            self.id = self.id + 1
        # 创建 QPixmap 对象
        qpixmap = QPixmap.fromImage(image)  # 将RGB格式的图像转换为QPixmap对象
        self.label.setPixmap(qpixmap)
        pass
    def pause(self):
        self.workthread.pause()
        self.Record_Button.setEnabled(True)
        self.Start_Button.setEnabled(True)
        
    def stop(self):
       
        self.Record_Button.setEnabled(True)
        self.Start_Button.setEnabled(True)
        self.Stop_Button.setEnabled(False)
        self.workthread.stop()
        self.workthread=None
        # self.camera.stop()
        # self.camera = None
        pass
    def closeEvent(self, event) -> None:
        if self.workthread!=None:
            self.workthread.stop()
        print('byby')