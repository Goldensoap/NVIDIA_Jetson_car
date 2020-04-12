#!/home/ros/.pyenv/shims/python3
# -*- coding: utf-8 -*-

import rospy
import cv2
import time
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

class 图像记录:
    def __init__(self):
        now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())
        self.帧转换器 = CvBridge()
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output = cv2.VideoWriter('{}.avi'.format(now),fourcc,10,(640,480))
        rospy.loginfo('创建文件{}.avi'.format(now))
        self.图像接收 = rospy.Subscriber("/catch_mouse_result/image_raw", Image, self.录像)

    def 录像(self,ros帧):
        cv帧 = self.帧转换器.imgmsg_to_cv2(ros帧,"bgr8")
        self.output.write(cv帧)


def 录像节点():

    rospy.init_node('jilu', anonymous=True)
    # 设置保存名称和编码格式
    记录实例 = 图像记录()
    try:
        # 循环等待回调函数
        rospy.spin()
    except KeyboardInterrupt:
        #处理完毕，释放所有资源
        记录实例.output.release()
        rospy.loginfo('完成录像')

if __name__ == '__main__':
    录像节点()