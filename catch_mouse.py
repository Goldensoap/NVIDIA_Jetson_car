import cv2
from copy import deepcopy
import multiprocessing as mp
import numpy
import time 

def object_detection(q,d,v):
    r"""
    """
    print('处理进程启动')
    now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())

    #帧计数
    counter = 0

    #录入标志
    flag = False

    #es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))

    background = None

    fps = q.get(timeout = 10)
    size = q.get(timeout = 10)

    # 设置保存名称和编码格式
    fourcc = cv2.VideoWriter_fourcc('X','2','6','4')
    output = cv2.VideoWriter('/media/pi/OTA128/{}.avi'.format(now),fourcc,fps,size)
    print('创建文件{}.avi'.format(now))

    print('开始处理')
    start = time.time()
    
    # 判断视频是否打开
    while True:

        if d['img'] is None:
            continue
        frame_lwpCV = deepcopy(d['img'])
        # 对帧进行预处理，先转灰度图，再进行高斯滤波。
        # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
        gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY)
        gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (3, 3), 0)
        # 萤石CT6C 在768*432 分辨率下时间戳位置
        gray_lwpCV[400:413,590:745] = 255
        
        # 将第一帧设置为整个输入的背景
        if background is None:
            background = deepcopy(gray_lwpCV)
            continue
        
        # 对于每个从背景之后读取的帧都会计算其与背景之间的差异，并得到一个差分图（different map）。
        # 还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
        diff = cv2.absdiff(background, gray_lwpCV)

        # 二值化阈值处理
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1] 

        # 形态学膨胀（嵌入式设备上过于浪费时间）
        #diff = cv2.dilate(diff, es, iterations=2) 

        # 显示矩形框
        # 该函数计算一幅图像中目标的轮廓
        _, contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        for c in contours:

            # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            s = cv2.contourArea(c)
            if  s < 25 or s > 200000 : 
                continue
            flag = True
            # 该函数计算矩形的边界框
            (x, y, w, h) = cv2.boundingRect(c) 
            cv2.rectangle(frame_lwpCV, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if flag:
            output.write(frame_lwpCV)
            flag = False

        # 更新背景
        counter +=1
        if counter % 150 ==0:
            background = deepcopy(gray_lwpCV)
        
        if v.value == 1:
            break

    # When everything done, release the capture
    stop = time.time()
    print('总计处理{}帧，平均处理时间{:.2f}毫秒/帧'.format(counter,((stop-start)/counter)*1000))
    output.release()

def get_rtsp(q,d,v):
    # 获取网络摄像头
    print('捕获进程启动')

    camera = cv2.VideoCapture('rtsp://admin:PSAXMJ@192.168.2.129:554/h264/ch1/main/av_stream')
    
    # 测试用,查看视频size,fps
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    if fps > 100:
        fps = 15

    print('成功连接摄像头 size:{},fps:{}'.format(size,fps))
    q.put(fps,block = False)
    q.put(size,block = False)

    counter = 0
    
    print('开始捕获流')
    start = time.time()
    while camera.isOpened():
        # 读取视频流
        ret, frame_lwpCV = camera.read()
        counter +=1
        if ret != True:
            continue

        d['img'] = frame_lwpCV 

        if v.value == 1:
            break

    stop = time.time()
    camera.release()
    print('捕捉图像子进程结束共计{}帧'.format(counter))
    print('平均捕获时间{:.2f}毫秒/帧'.format(((stop-start)/counter)*1000))

def get_order(v):
    while True:
        if input() == 'q':
            v.value = 1
            break

if __name__ == '__main__':
    print("目标检测启动,输入q回车结束程序")
    q = mp.Queue()
    status = mp.Value('i',0)
    with mp.Manager() as manager:
        d = manager.dict()
        d['img'] = None

        get_image = mp.Process(target = get_rtsp, args = (q,d,status))
        ob = mp.Process(target =  object_detection, args = (q,d,status))
        
        get_image.start()
        ob.start()

        start = time.time()

        get_order(status)

        get_image.join()
        ob.join()

        stop = time.time()

        print('程序结束,总计运行{:.2f}秒'.format(stop-start))