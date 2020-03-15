#!/home/ros/.pyenv/shims/python3
# -*- coding: utf-8 -*-

import rospy
import cv2

from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image


class 图像处理:

    def __init__(self):
        
        self.帧转换器 = CvBridge()
        # 创建一个Subscriber，订阅名为/usb_cam/image_raw的话题，注册回调函数poseCallback
        self.图像接收 = rospy.Subscriber("/usb_cam/image_raw", Image, self.帧处理)
        # 创建一个发布者，发布图像处理结果和选定录制的帧
        self.帧处理结果 = rospy.Publisher("/catch_mouse_processed/image_raw",Image,queue_size=10)
        self.帧录制 = rospy.Publisher("/catch_mouse_result/image_raw",Image,queue_size=10)
        
        self.bs=cv2.createBackgroundSubtractorKNN(detectShadows=True)

    def 帧处理(self,ros帧):
        try:
            cv帧 = self.帧转换器.imgmsg_to_cv2(ros帧,"bgr8")
        except CvBridgeError as e:
            print(e)

        fgmask=self.bs.apply(cv帧)
        th=cv2.threshold(fgmask.copy(),244,255,cv2.THRESH_BINARY)[1]
        th=cv2.erode(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=2)
        dilated=cv2.dilate(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=2)
        contours,_=cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        是否录制 = False
        for c in contours:
            if cv2.contourArea(c)>300:
                (x,y,w,h)=cv2.boundingRect(c)
                cv2.rectangle(cv帧,(x,y),(x+w,y+h),(255,255,0),2)
                是否录制 = True

        if len(contours) > 0 and 是否录制 == True:
            try:
                self.帧录制.publish(self.帧转换器.cv2_to_imgmsg(cv帧, "bgr8"))
            except CvBridgeError as e:
                print(e)

        try:
            self.帧处理结果.publish(self.帧转换器.cv2_to_imgmsg(cv帧, "bgr8"))
        except CvBridgeError as e:
            print(e)

def 图像处理节点():
	# ROS节点初始化
    rospy.loginfo("开始处理图像")
    处理实例 = 图像处理()
    rospy.init_node('cv', anonymous=True)

    try:
        # 循环等待回调函数
        rospy.spin()
    except KeyboardInterrupt:
        print("图像处理节点进程结束")

if __name__ == '__main__':
    图像处理节点()
