#!/home/pi/.pyenv/shims/python3
# -*- coding: utf-8 -*-

import rospy
import time
import Adafruit_PCA9685
from std_msgs.msg import String


class PCA9685:
    def __init__(self,频率=50):
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x41)
        self.pwm.set_pwm_freq(频率)

    def 调整占空比(self,通道,占空比):
        脉冲总长 = 1000000    # 1,000,000 us 每秒
        脉冲总长 /= 50       # 50 Hz
        脉冲总长 /= 4096     # 12 bits 分辨率
        
        占空比 *= 1000
        占空比 /= 脉冲总长
        self.pwm.set_pwm(通道, 0, int(占空比))

    def 舵机控制(self,指令):
        rospy.loginfo(f"接收指令:{指令.data}")
        if 指令.data == "上":
            self.调整占空比(2,0.5)
            time.sleep(0.05)
            self.调整占空比(2,1.5) 
        elif 指令.data == "下":
            self.调整占空比(2,2.6)
            time.sleep(0.05)
            self.调整占空比(2,1.5)
        elif 指令.data == "左":
            self.调整占空比(1,2.6)
            time.sleep(0.05)
            self.调整占空比(1,1.5)  
        elif 指令.data == "右":
            self.调整占空比(1,0.5)
            time.sleep(0.05)
            self.调整占空比(1,1.5)

def 订阅控制信息():

    舵机 = PCA9685()

    rospy.init_node('duoji', anonymous=True)

    rospy.Subscriber("/舵机控制/指令", String, 舵机.舵机控制)

    rospy.spin()

if __name__ =='__main__':
    订阅控制信息()