import cv2
import multiprocessing as mp
from copy import deepcopy
import numpy
import time

def object_detection(e,d):
    r"""
    """
    now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())

    #帧计数
    counter = 0

    #es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
    background = None

    #阻塞等待视频流
    e.wait()

    # 设置保存名称和编码格式
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    output = cv2.VideoWriter('{}.avi'.format(now),fourcc,10,d['size'])
    print('创建文件{}.avi'.format(now))

    print('开始处理')
    start = time.time()

    while True:
        # 读取视频流
        if d['image'] is None:
            continue
        frame_lwpCV = deepcopy(d['image'])

        # 对帧进行预处理，先转灰度图，再进行高斯滤波。
        # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
        gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY)
        gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (7, 7), 0)

        # 将第一帧设置为整个输入的背景
        if background is None:
            background = deepcopy(gray_lwpCV)
            continue

        # 对于每个从背景之后读取的帧都会计算其与背景之间的差异，并得到一个差分图（different map）。
        # 还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
        diff = cv2.absdiff(background, gray_lwpCV)

        # 二值化阈值处理
        diff = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)[1] 

        # 形态学膨胀
        #diff = cv2.dilate(diff, es, iterations=2) 

        # 显示矩形框
        # 该函数计算一幅图像中目标的轮廓
        _,contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        Flag = False
        for c in contours:

            # 对于矩形区域，只显示给定阈值的轮廓，所以一些微小的变化和背景变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            if cv2.contourArea(c) < 500 or cv2.contourArea(c) > 200000: 
                continue

            # 该函数计算矩形的边界框
            Flag = True
            (x, y, w, h) = cv2.boundingRect(c) 
            cv2.rectangle(frame_lwpCV, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if len(contours) > 0 and Flag == True:
            output.write(frame_lwpCV)

        # 更新背景
        counter +=1
        if counter % 150 ==0:
            background = deepcopy(gray_lwpCV)

        #按'q'健退出循环
        if d['status'] == False:   
            break

    stop = time.time()
    print('总计处理{}帧，平均处理时间{:.2f}毫秒/帧，平均处理帧率{:.2f}'.format(counter,((stop-start)/counter)*1000,counter/(stop-start)))
    #处理完毕，释放所有资源
    output.release()
    print('完成录像')


def get_video(e,d):
    # 获取网络摄像头
    camera = cv2.VideoCapture('tcp://192.168.2.237:8090')
    # 测试用,查看视频size,fps
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    print('成功连接摄像头 size:{},fps:{}'.format(str(size),str(fps)))

    d['size'] = size
    d['fps'] = fps

    counter = 0
    start = time.time()
    
    # 判断视频是否打开
    while camera.isOpened():

        # 读取视频流
        ret, frame_lwpCV = camera.read()
        if ret == True:
            d['image'] = frame_lwpCV
            counter += 1
            e.set()

        if (counter/1500) == 1:
            d['status'] = False
            break

    camera.release()
    stop = time.time()
    print('捕捉图像子进程结束共计{}帧'.format(counter))
    print('平均捕获时间{:.2f}毫秒/帧,平均捕获帧率{:.2f}'.format(((stop-start)/counter)*1000,counter/(stop-start)))


if __name__ == '__main__':
    print("目标检测启动,等待时间满足条件后结束")
    e = mp.Event()
    with mp.Manager() as manager:
        d = manager.dict()
        d['status'] = True

        ob = mp.Process(target = object_detection,args = (e,d))
        ob.start()
        print('处理进程启动')

        print('视频开始捕获')
        get_video(e,d)

        ob.join()
        print('程序结束')
