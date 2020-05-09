#!/home/jetbot/.pyenv/shims/python3

import rospy
#import cv2
import time
#from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

帧计数 = 0
起点 = time.time()

def 回调(ros帧):
    #帧转换器 = CvBridge()
    #cv帧 = 帧转换器.imgmsg_to_cv2(ros帧,"bgr8")
    global 帧计数
    global 起点
    帧计数 += 1
    
    当前 = time.time()
    if int(当前 - 起点):
        rospy.loginfo(f"帧率:{帧计数}")
        起点 = 当前
        帧计数 = 0

def 图像接收测试():
	# ROS节点初始化
    rospy.init_node('cv_test', anonymous=True)
    rospy.loginfo("开始处理图像")
    
    图像接收 = rospy.Subscriber("/usb_cam/image_raw", Image, 回调)
    
    try:
        # 循环等待回调函数
        rospy.spin()
    except KeyboardInterrupt:
        print("图像处理节点进程结束")

if __name__ == '__main__':
    
    图像接收测试()
