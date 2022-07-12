#!/usr/bin/python3
# rtsp://admin:Mandarin53$@192.168.1.220:554//h264Preview_01_main
# rtsp://admin:123456$@192.168.1.243:554//h264Preview_01_main

from cmath import rect
import sys
import os
import cv2
import numpy as np
import imutils
import time
from threading import Thread
import serial
import time
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
from PyQt5.QtWidgets import (
    QWidget, 
    QApplication, 
    QLabel, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QTableWidget,
    QPushButton,
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QCheckBox
)

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'SmartHub'
        self.left = 0
        self.top = 0
        self.stream_on = False
        self.display_width = 1024 # Todo: change this?
        self.display_height = 600 # Todo: change this ?
        self.fps = 0.05 # Todo: change this ?
        self.initUI()
        self.rtsp_url = ""
        self.display_rtsp_form()
        self.recording = (VideoRecording)
        self.live = (VideoStream)
        self.type_of_stream = "home"
        self.list_widget
        self.disable_recording_value = False
 
    def initUI(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.display_width, self.display_height)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.createTable()
 
        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QStackedLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
 
        self.initialize_rtsp_stream_layout()
 
        # Show widget
        self.show()
 
    def createTable(self):
        # Create first widget for table (left column)
        self.rtsp_form = QWidget()
        self.rtsp_form_layout = QFormLayout() # Layout to place the RTSP credential form
        self.rtsp_form_layout.setAlignment(Qt.AlignVCenter)
        self.user_input_username = QLineEdit("")
        self.user_input_password = QLineEdit("")
        self.user_input_password.setEchoMode(QLineEdit.Password)
        self.user_input_ip = QLineEdit("")
        self.submit_btn = QPushButton("Submit")
        font = self.font()
        font.setPointSize(16)
        self.rtsp_username = QLabel("Enter Username:")
        self.rtsp_username.setFont(font)
        self.rtsp_password = QLabel("Enter Password:")
        self.rtsp_password.setFont(font)
        self.submit_btn.clicked.connect(lambda:self.submit_btn_clicked())
        self.disable_recording = QCheckBox("Disable Recording", self)
        self.disable_recording.setIconSize(QtCore.QSize(32, 32))
        self.disable_recording.setStyleSheet("QCheckBox{ font-size: 20px; border: 1px solid black } QCheckBox::indicator{ width: 40px; height: 40px; }")
        self.disable_recording.clicked.connect(self.disable_recording_clicked)
        self.rtsp_form_layout.addRow(self.rtsp_username)
        self.rtsp_form_layout.addRow(self.user_input_username)
        self.rtsp_form_layout.addRow(self.rtsp_password)
        self.rtsp_form_layout.addRow(self.user_input_password)
        self.rtsp_form_layout.addRow(self.submit_btn)
        self.rtsp_form_layout.addRow(self.disable_recording)
        self.rtsp_form_layout.setFormAlignment(Qt.AlignTop)
        self.rtsp_form.setLayout(self.rtsp_form_layout)
        
        # Create second widget for table (middle column)
        self.im = QPixmap("./dst/image.png")
#         self.im = QPixmap(".//dst//image.png")
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setPixmap(self.im)
 
        # Create third widget for table (right column)
        self.list_widget = QListWidget()
        arr = os.listdir('/home/seniordesign/Desktop/smarthub/videos')
        # arr = os.listdir('C:\\Users\\matth\\Desktop\\videos')
#         arr = os.listdir('/Users/koreylombardi/Desktop/videos')
        for file in arr:
            list_item = QListWidgetItem(file, self.list_widget)
            font = self.font()
            font.setPointSize(16)
            list_item.setFont(font)
        self.list_widget.clicked.connect(self.list_item_clicked)
 
        # Creating the table of widgets
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setCellWidget(0, 0, self.rtsp_form)
        self.tableWidget.setCellWidget(0, 1, self.label)
        self.tableWidget.setCellWidget(0, 2, self.list_widget)
        self.tableWidget.setColumnWidth(0, 340)
        self.tableWidget.setRowHeight(0, 600)
        self.tableWidget.setColumnWidth(1, 342)
        self.tableWidget.setRowHeight(1, 600)
        self.tableWidget.setColumnWidth(2, 340)
        self.tableWidget.setRowHeight(2, 600)
 
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
 
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
 
    def initialize_rtsp_stream_layout(self):
        self.type_of_stream = "home"
        self.footage = QWidget()
 
        self.back_button = QPushButton(self)
        self.back_button.setVisible(False)
        self.back_button.setGeometry(200, 150, 200, 40)
        self.back_button.clicked.connect(self.back_button_clicked)
        self.back_button.setIcon(QtGui.QIcon(".//dst//back.png"))
        self.back_button.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("QPushButton::hover{background-color : gray; border: 1px solid black;}")
 
        self.pause_button = QPushButton(self)
        self.pause_button.setVisible(False)
        self.pause_button.clicked.connect(self.pause_button_clicked)
        self.pause_button.setIcon(QtGui.QIcon(".//dst//pause.png"))
        self.pause_button.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("QPushButton::hover{background-color : gray; border: 1px solid black;}")
 
        self.play_button = QPushButton(self)
        self.play_button.setVisible(False)
        self.play_button.clicked.connect(self.play_button_clicked)
        self.play_button.setIcon(QtGui.QIcon(".//dst//play.png"))
        self.play_button.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("QPushButton::hover{background-color : gray; border: 1px solid black;}")
 
        self.fast_forward = QPushButton(self)
        self.fast_forward.setVisible(False)
        self.fast_forward.clicked.connect(self.fast_forward_button_clicked)
        self.fast_forward.setIcon(QtGui.QIcon(".//dst//fast-forward.png"))
        self.fast_forward.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("QPushButton::hover{background-color : gray; border: 1px solid black;}")
 
        self.rewind_button = QPushButton(self)
        self.rewind_button.setVisible(False)
        self.rewind_button.clicked.connect(self.rewind_button_clicked)
        self.rewind_button.setIcon(QtGui.QIcon(".//dst//rewind.png"))
        self.rewind_button.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("QPushButton::hover{background-color : gray; border: 1px solid black;}")

        self.disable_ai = QCheckBox("Disable Detection", self)
        self.disable_ai.setIconSize(QtCore.QSize(32, 32))
        self.disable_ai.setStyleSheet("QCheckBox{ font-size: 20px; } QCheckBox::indicator{ width: 40px; height: 40px; }")
        self.disable_ai.clicked.connect(self.disable_ai_clicked)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.rewind_button)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.fast_forward)
        self.button_layout.addWidget(self.disable_ai)

        self.image_label = QLabel(self) # Label used to hold the image
        self.image_label.resize(self.display_width, self.display_height)
        self.footage_layout = QVBoxLayout() # Layout to place RTSP stream footage
        self.footage_layout.setContentsMargins(0, 0, 0, 0)
        self.footage_layout.addWidget(self.image_label)
        self.footage_layout.setAlignment(Qt.AlignCenter)
        self.footage_layout.addLayout(self.button_layout)
        self.footage.setLayout(self.footage_layout)
        self.layout.addWidget(self.footage)
        self.play_button.setVisible(True)
        self.pause_button.setVisible(True)
        self.fast_forward.setVisible(True)
        self.back_button.setVisible(True)
        self.rewind_button.setVisible(True)
 
    def display_rtsp_form(self):
        self.layout.setCurrentIndex(0)
 
    def display_rtsp_stream(self):
        self.layout.setCurrentIndex(1) # Makes this layout visible
        self.play_button.setVisible(False)
        self.pause_button.setVisible(False)
        self.fast_forward.setVisible(False)
        self.rewind_button.setVisible(False)
        self.disable_ai.setVisible(True)
        self.live = self.thread = VideoStream(self.rtsp_url, self.image_label, self.disable_recording_value)
        self.thread.change_pixels_obj.connect(self.thread.update_image)
        self.thread.start()
 
    def display_rtsp_recording(self):
        self.layout.setCurrentIndex(1) # Makes this layout visible
        self.play_button.setVisible(True)
        self.pause_button.setVisible(True)
        self.fast_forward.setVisible(True)
        self.back_button.setVisible(True)
        self.rewind_button.setVisible(True)
        self.disable_ai.setVisible(False)
        self.recording = self.thread = VideoRecording(self.rtsp_url, self.image_label, self.display_width, self.display_height, self.fps) # Starts the RTSP stream
        self.thread.change_pixels_obj.connect(self.thread.update_image)
        self.thread.start()
 
    def submit_btn_clicked(self):
        self.user_input = "rtsp://" + self.user_input_username.text() + ":" + self.user_input_password.text() + "@192.168.1.220:554//h264Preview_01_main"
#         self.user_input = "rtsp://" + self.user_input_username.text() + ":" + self.user_input_password.text() + "@192.168.1.243:554//h264Preview_01_main"
        self.type_of_stream = "live"
        self.store_user_input()
        self.display_rtsp_stream()
 
    def list_item_clicked(self):
        self.type_of_stream = "recording"
        self.item = self.list_widget.currentItem().text()
        self.store_item_input()
        self.display_rtsp_recording()
        
    def disable_ai_clicked(self):
        self.live.disable_ai = not self.live.disable_ai

    def disable_recording_clicked(self):
        self.disable_recording_value = not self.disable_recording_value

    def pause_button_clicked(self):
        self.recording.pause = True
 
    def play_button_clicked(self):
        self.recording.play = True
 
    def back_button_clicked(self):
        self.layout.setCurrentIndex(0)
        if(self.type_of_stream == "recording"):
            self.recording.close_stream()
        if(self.type_of_stream == "live"):
            self.live.close_stream()
 
    def rewind_button_clicked(self):
        if(self.recording.fps == 0.05):
            self.recording.fps = 0.025
        if(self.recording.fps == 0.025):
            self.recording.fps = 0.0125
        if(self.recording.fps == 0.0125):
            self.recording.fps = 0.05
        self.recording.rewind = True
 
    def fast_forward_button_clicked(self):
        if(self.recording.fps == 0.05):
            self.recording.fps = 0.025
        if(self.recording.fps == 0.025):
            self.recording.fps = 0.0125
        if(self.recording.fps == 0.0125):
            self.recording.fps = 0.05
 
    def store_item_input(self):
        self.rtsp_url =('/home/seniordesign/Desktop/smarthub/videos/' + self.item)
        # self.rtsp_url = ('C:\\Users\\matth\Desktop\\videos\\' + self.item)
#         self.rtsp_url = ("/Users/koreylombardi/Desktop/videos/" + self.item)
 
    def store_user_input(self):
        self.rtsp_url = self.user_input
 
 
class VideoStream(QThread, object):
    # When placed inside init, the code code does not work
    change_pixels_obj = pyqtSignal(np.ndarray) # Object for updating frames
     
    def __init__(self, rtsp_str, image_label, disable_recording_value):
        super().__init__()
        self.rtsp_str = rtsp_str
        self.image_label = image_label
        self.display_width = 640
        self.display_height = 480
        self.detection_timer = 0
        self.disable_ai = False
        self.disable_recording = disable_recording_value
        size = (self.display_width, self.display_height)
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')    
        self.out = cv2.VideoWriter('/home/seniordesign/Desktop/smarthub/videos/' + time.strftime("%m%d%Y-%H%M%S") + '.avi', fourcc, 20.0, size)
 
        # Capture RTSP stream
        while(True):
            self.cap = cv2.VideoCapture(self.rtsp_str)
            if(self.cap.isOpened()):
                break
 
    # Function gets called every time VideoStream is instantiated
    def run(self):
        # Initializing the HOG person detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
 
        frame_width = 640
        frame_height = 480
        size = (frame_width, frame_height)
 
        ret, frame = self.cap.read()
 
        # Video codec and output destination - filename formatted: MonthDayYear - HourMinuteSecond
        # out = cv2.VideoWriter('C://Users//matth//Desktop//videos//' + time.strftime("%m%d%Y-%H%M%S") + '.avi', fourcc, 20.0, size)
#         out = cv2.VideoWriter('/Users/koreylombardi/Desktop/videos/' + time.strftime("%m%d%Y-%H%M%S") + '.avi', fourcc, 20.0, size)
        
        ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            write_timeout=10,
            timeout=0
        )
        
        def uart_write(status):
            ser.write(b'%d' %(status))
#             time.sleep(1)
#             ser.close()
        
        def detect_human(self, detection_frame):
            # Detecting all the regions in the Image that has a pedestrians inside it
            # For speedup, increase scale in range (1.0 - 1.5), increase winStride 
            (regions, _) = hog.detectMultiScale(detection_frame, winStride=(4, 4), padding=(6, 6), scale=1.3)
            if (len(regions) == 1 and (self.detection_timer == 0 or has_timer_expired())): # len == 0 when no detection found
                print("Human Detected!  Results: " + str(regions))
                uart_write(3)
                set_detection_timer(10)
 
        def set_detection_timer(timer_sec):
            self.detection_timer = time.time() + timer_sec
 
        def has_timer_expired():
            if self.detection_timer < time.time():
                return True
            else:
                return False
 
        counter = 0 
        while True:
            ret, frame = self.cap.read()
            if ret: 
                # Resize image for better detection
                if counter == 6 and self.disable_ai == False:
                    detection_frame = imutils.resize(frame, width=400)
                    detection_thread = Thread(target=detect_human, args=(self, detection_frame))
                    detection_thread.start()
                    counter = 0
                counter = counter + 1
                self.change_pixels_obj.emit(frame)
                frame = cv2.resize(frame, (frame_width, frame_height))
                if(self.disable_recording == False):
                    self.out.write(frame)
 
    # Function gets called for each new frame
    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        qt_img = self.convert_image_to_qt_image(img)
        self.image_label.setPixmap(qt_img)
 
    def convert_image_to_qt_image(self, img):
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converts opencv image to QPixmap image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio))
 
    # Function gets called when user exits app
    def close_stream(self):
        self.cap.release()
#         cv2.destroyAllWindows() # breaks code on pi
        print("RTSP stream closed")
 
class VideoRecording(QThread, object):
    # When placed inside init, the code code does not work
    change_pixels_obj = pyqtSignal(np.ndarray) # Object for updating frames
 
    def __init__(self, rtsp_str, image_label, display_width, display_height, fps):
        super().__init__()
        self.rtsp_str = rtsp_str
        self.image_label = image_label
        self.display_width = 640
        self.display_height = 480
        self.fps = fps
        self.frame_list = []
        self.counter = 0
        self.pause = False
        self.play = False
        self.rewind = False
        self.total_frames = 0
        self.chopped_frames = len(self.frame_list) - 1
        self.chopped_frames_temp = len(self.frame_list) - 1
        self.recap_frames = 0
        self.recap = False
 
        # Capture RTSP stream
        while(True):
            self.cap = cv2.VideoCapture(self.rtsp_str)
            if(self.cap.isOpened()):
                break
 
    # Function gets called every time VideoStream is instantiated
    def run(self):
        # Initializing the HOG person detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
 
        while True:
            ret, frame = self.cap.read()
            self.chopped_frames_temp = len(self.frame_list) - 1
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            while self.rewind:
                imutils.resize(self.frame_list[self.chopped_frames_temp], width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(self.frame_list[self.chopped_frames_temp])
                if(self.fps):
                    time.sleep(self.fps)
                if(self.chopped_frames_temp >= 2):
                    self.chopped_frames_temp = self.chopped_frames_temp - 1
                if(self.chopped_frames_temp == 1):
                    self.chopped_frames = self.chopped_frames_temp
                    self.recap_frames = self.chopped_frames
                    self.rewind = False
                    self.pause = True
                    self.play = False
                    self.recap = True
                    break
                if(self.play == True):
                    self.chopped_frames = self.chopped_frames_temp
                    self.recap_frames = self.chopped_frames
                    self.rewind = False
                    self.play = False
                    self.recap = True
                    break
 
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            while self.recap:
                # print('here3')
                print("self.total_frames", self.total_frames)
                print("self.recap_frames", self.recap_frames)
                imutils.resize(self.frame_list[self.recap_frames], width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(self.frame_list[self.recap_frames])

                if(self.fps):
                    time.sleep(self.fps)
                self.recap_frames += 1
                if(self.recap_frames + 1 == self.total_frames):
                    self.recap = False
                    break
 
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            if ret and (self.recap == False):
                # Resize image for better detection
                imutils.resize(frame, width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(frame)
                # breaks code on pi
                if(self.fps):
                    time.sleep(self.fps)
                self.frame_list.append(frame)
                self.total_frames += 1
 
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
    # Function gets called for each new frame
    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        qt_img = self.convert_image_to_qt_image(img)
        self.image_label.setPixmap(qt_img)
 
    def convert_image_to_qt_image(self, img):
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converts opencv image to QPixmap image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio))
 
    # Function gets called when user exits app
    def close_stream(self):
        if self.cap.isOpened():
            self.cap.release()
#         cv2.destroyAllWindows() # breaks code on pi
        print("RTSP stream closed")
 
def exit_app(q_app, app):
    q_app.exec_() # Function's execution pauses here until user exits app 
    app.thread.close_stream() # Closes RTSP stream 
    sys.exit() # Exits app
 
def main():
    q_app = QApplication(sys.argv)
    app = App()
    app.show() 
    exit_app(q_app, app)
    
if __name__=="__main__":
    main()
