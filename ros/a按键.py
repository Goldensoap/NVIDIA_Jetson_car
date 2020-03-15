#!/home/ros/.pyenv/shims/python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String
from getch import _Getch

def 发布指令():
    shell输入 = _Getch()
    rospy.init_node('keyboard', anonymous=True)

    指令发送 = rospy.Publisher('/舵机控制/指令', String, queue_size=10)

    循环频率 = rospy.Rate(50)
    while not rospy.is_shutdown():
        输入 = shell输入()
        数据 = String()

        if 输入 == 'w':
            数据.data = "上"
            指令发送.publish(数据)
            rospy.loginfo(f"发送指令:{数据.data}")
        elif 输入== 'a':
            数据.data = "左"
            指令发送.publish(数据)
            rospy.loginfo(f"发送指令:{数据.data}")
        elif 输入 == 's':
            数据.data = "下"
            指令发送.publish(数据)
            rospy.loginfo(f"发送指令:{数据.data}")
        elif 输入 == 'd':
            数据.data = "右"
            指令发送.publish(数据)
            rospy.loginfo(f"发送指令:{数据.data}")

        循环频率.sleep()

if __name__ == '__main__':

    发布指令()
