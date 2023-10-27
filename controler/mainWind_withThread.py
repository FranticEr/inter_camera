
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

# import pyrealsense2 as rs


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
    
    def __init__(self,recordFolder_root ,parent: QObject | None = None) -> None:
        super().__init__(parent)

        #存储路径
        self.recordFolder_root=recordFolder_root
        print(self.recordFolder_root)
        self.recoding=False
        self.queue=[]
        self.start_recording()

    def start_recording(self):
        self.mp4  = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps=30
        self.w=1280
        self.h=720
        self.recordFolder=os.path.join(self.recordFolder_root,str(int(time())))
        os.mkdir(self.recordFolder)
        print(self.recordFolder)
        self.video_path=os.path.join(self.recordFolder,"rgb.mp4")
        self.depth_path=os.path.join(self.recordFolder,"depthcolor.mp4")
        self.depth16_path=os.path.join(self.recordFolder,"depth16.h5")
        self.wr = cv2.VideoWriter(self.video_path, self.mp4, self.fps, (self.w, self.h), isColor=True)
        self.wr_colordepth = cv2.VideoWriter(self.depth_path, self.mp4, self.fps, (self.w, self.h), isColor=True)
        self.wr_depth = h5py.File(self.depth16_path, 'w')
        self.recording=True
        print(self.recording)
        pass
    def add_frame(self,color_image, depth_image, colorizer_depth):
        self.queue.append(color_image)
        pass

    def stop_recording(self):
        cv2.destroyAllWindows()
        

        self.recroding=False
        self.wr.release()
        self.wr_colordepth.release()

        # wr_left.release()
        # wr_right.release()
        self.wr_depth.close()
        print("release")


    
    def run(self):
         print(self.recording)
         while self.recording:
            if self.recording and len(self.queue) > 0:
                #frames的顺序是[color_image, depth_image, colorizer_depth]
                frame = self.queue.pop(0)
                self.wr.write(frame) 
                
            else:
                # 任务不占用主界面时间，可以进行其他操作
                pass






class myWin(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        #connect_signal_slot
        self.Record_Button.clicked.connect(self.record)
        self.Start_Button.clicked.connect(self.start)
        self.Stop_Button.clicked.connect(self.stop)
        self.pauseButton.clicked.connect(self.pause)
        self.RecordFolderButton.clicked.connect(self.folderChose)
        # self.getCameralist_Button.clicked.connect(self.getCameralist)

        
        self.workthread=None
        self.recordFolder_root="D:\inter_re"

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

        #创建录制子线程
        
        self.record_thread=recordThread(recordFolder_root=self.recordFolder_root)
        self.workthread.update_data.connect(self.record_thread.add_frame)
        #启动
        self.record_thread.start()
        pass

    def folderChose(self):
        self.recordFolder_root=QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹",r"C:/")
        pass

    def start(self):
        #按钮状态设置
        self.Start_Button.setEnabled(False)
        self.Stop_Button.setEnabled(True)

        #开始监视
        if self.workthread==None:
            print("isNone")
            #启动相机
            self.workthread=WorkThread()
            self.workthread.update_data.connect(self.handleDisplay)
            
            self.workthread.start()
        #暂停启动
        if self.workthread.ispause==True:
            self.workthread.continueT()
        pass
    
    #显示
    def handleDisplay(self,color_image, depth_image, colorizer_depth):
        rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # 将BGR格式转换为RGB格式
        # 创建 QImage 对象
        image = QImage(rgb_frame.data,
                    rgb_frame.shape[1],
                    rgb_frame.shape[0],
                    QImage.Format_RGB888)        
        # 创建 QPixmap 对象
        qpixmap = QPixmap.fromImage(image)  # 将RGB格式的图像转换为QPixmap对象
        self.label.setPixmap(qpixmap)
        pass

    #暂停
    def pause(self):
        #设置按钮状态
        self.workthread.pause()
        self.Record_Button.setEnabled(True)
        self.Start_Button.setEnabled(True)
        
    def stop(self):
        #设置按钮状态
        self.Record_Button.setEnabled(True)
        self.Start_Button.setEnabled(True)
        self.Stop_Button.setEnabled(False)

        #停止相机线程
        self.workthread.stop()
        #清空句柄
        self.workthread=None
        # self.camera.stop()
        # self.camera = None
        pass
    #关闭应用时回收相机线程
    def closeEvent(self, event) -> None:
        if self.workthread!=None:
            self.workthread.stop()
            self.record_thread.stop_recording()
        print('byby')