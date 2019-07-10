import cv2
from copy import deepcopy
import multiprocessing as mp
import numpy
import time 

def object_detection():
    r"""
    """
    now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())

    #帧计数
    counter = 0


    background = None
    
    # 获取网络摄像头
    camera = cv2.VideoCapture('rtsp://admin:PSAXMJ@192.168.2.129:554/h264/ch1/main/av_stream')
    
    # 测试用,查看视频size,fps
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    if fps > 100:
        fps = 15

    print('成功连接摄像头 size:{},fps:{}'.format(str(size),str(fps)))

    # 设置保存名称和编码格式
    fourcc = cv2.VideoWriter_fourcc('X','2','6','4')
    output = cv2.VideoWriter('/media/pi/OTA128/{}.avi'.format(now),fourcc,fps,size)
    print('创建文件{}.avi'.format(now))

    # 创建掩模
    addimg = numpy.zeros([size[1],size[0]],dtype=numpy.uint8)
    mask = numpy.zeros([size[1],size[0]],dtype=numpy.uint8)
    mask[:,:]=255
    mask[0:100,0:100]=0

    start = time.time()
    # 判断视频是否打开
    while camera.isOpened():
        
        # 读取视频流
        ret, frame_lwpCV = camera.read()
        if ret != True:
            continue
        # 对帧进行预处理，先转灰度图，再进行高斯滤波。
        # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
        gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY)
        
        # 将第一帧设置为整个输入的背景
        if background is None:
            background = gray_lwpCV
            continue
        
        # 对于每个从背景之后读取的帧都会计算其与背景之间的差异，并得到一个差分图（different map）。
        # 还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
        diff = cv2.absdiff(background, gray_lwpCV)

        # 二值化阈值处理
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1] 

        # 显示矩形框
        # 该函数计算一幅图像中目标的轮廓
        
        image, contours, hierarchy = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        
        for c in contours:

            # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            if cv2.contourArea(c) < 50: 
                continue

            # 该函数计算矩形的边界框
            (x, y, w, h) = cv2.boundingRect(c) 
            cv2.rectangle(frame_lwpCV, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if len(contours) > 0:
            output.write(frame_lwpCV)

        # 更新背景
        counter +=1
        if counter % 150 ==0:
            background = gray_lwpCV

        if counter == 450:
            break

    # When everything done, release the capture
    stop = time.time()
    print('平均处理时间'+str((stop-start)/450))
    output.release()
    camera.release()

if __name__ == '__main__':
    print("目标检测启动,按q 结束程序")
    start = time.time()
    object_detection()
    stop = time.time()


    print('程序结束,总时间'+str(stop-start))