# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 02:40:07 2019

@author: pi
"""

from __future__ import division
import time
import Adafruit_PCA9685
import threading
import queue
import os
from getch import _Getch
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).


#范围0.5-2.6ms，中间停顿值1.5，左右通道1，上下通道2
class Attitude_control(threading.Thread):

    def __init__(self,qe,freq=50):
        super().__init__()
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x41)
        self.pwm.set_pwm_freq(freq)
        self.qe = qe

    def run(self):
        print("舵机控制线程启动")
        while True:
            sign = self.qe.get(block = True,timeout = None)
            if sign == "up":
                self.set_servo_pulse(2,2.6)
                time.sleep(0.1)
                self.set_servo_pulse(2,1.5)
            elif sign == "down":
                self.set_servo_pulse(2,0.5)
                time.sleep(0.1)
                self.set_servo_pulse(2,1.5)      
            elif sign == "left":
                self.set_servo_pulse(1,2.6)
                time.sleep(0.1)
                self.set_servo_pulse(1,1.5)  
            elif sign == "right":
                self.set_servo_pulse(1,0.5)
                time.sleep(0.1)
                self.set_servo_pulse(1,1.5)

    def set_servo_pulse(self,channel, pulse):
        pulse_length = 1000000    # 1,000,000 us per second
        pulse_length /= 50       # 50 Hz
        #print('{0}us per period'.format(pulse_length))
        pulse_length /= 4096     # 12 bits 分辨率
        #print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse /= pulse_length
        self.pwm.set_pwm(channel, 0, int(pulse))

def start_push_video():
    print("打开视频端口")
    os.system("raspivid -t 0 -w 640 -h 480 -fps 25 -o - | nc -l 8090")


def main():
    print("鹰眼...启动")
    print("方向键控制画面移动，q键退出，r键重启画面推送")

    qe = queue.Queue(1)

    thread_1 = Attitude_control(qe)
    thread_1.name = '舵机控制线程'
    thread_1.daemon = True
    thread_1.start()

    thread_2 = threading.Thread(target=start_push_video)
    thread_2.name = '视频端口准备线程'
    thread_2.daemon = True
    thread_2.start()

    getch = _Getch()
    while True:
        ch = getch()
        if ch == 'q':
            break
        elif ch == '[':
            Next = getch()
            try:
                if Next == 'A':
                    qe.put_nowait("up")
                elif Next == 'B':
                    qe.put_nowait("down")
                elif Next == 'D':
                    qe.put_nowait("left")
                elif Next == 'C':
                    qe.put_nowait("right")
            except queue.Full:
                pass

        elif ch == bytes('r','ascii'):
            if thread_2.isAlive() == True:
                print("视频端口已开启，无需重置")
            else:
                print("尝试重启视频端口")
                thread_2 = threading.Thread(target=start_push_video)
                thread_2.name = '视频端口准备线程'
                thread_2.daemon = True
                thread_2.start()
                if thread_2.isAlive() == True:
                    print("视频端口重启成功，请查看")

    print("主线程结束")
if __name__ == "__main__":
    main()
