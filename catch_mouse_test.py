import cv2
import multiprocessing as mp
import numpy
import time 

def object_detection(e,d):
    r"""
    """
    now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())

    # 创建掩模
    addimg = numpy.zeros([1080,1920],dtype=numpy.uint8)
    mask = numpy.zeros([1080,1920],dtype=numpy.uint8)
    mask[:,:]=255
    mask[1012:1047,1391:1848]=0

    #帧计数
    counter = 0

    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
    background = None

    e.wait()

    #cv2.namedWindow('contours',0)
    #cv2.resizeWindow('contours',640,360)
    #cv2.namedWindow('gary',0)
    #cv2.namedWindow('dis',0)

    # 设置保存名称和编码格式
    fourcc = cv2.VideoWriter_fourcc('X','2','6','4')
    output = cv2.VideoWriter('/media/pi/OTA128/{}.avi'.format(now),fourcc,d['fps'],d['size'])

    # 判断视频是否打开
    while True:

        # 读取视频流
        frame_lwpCV = d['image']
            
        # 对帧进行预处理，先转灰度图，再进行高斯滤波。
        # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
        gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY)
        gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)
        gray_lwpCV = cv2.add(gray_lwpCV,addimg,mask=mask)

        # 将第一帧设置为整个输入的背景
        if background is None:
            background = gray_lwpCV
            continue

        # 对于每个从背景之后读取的帧都会计算其与背景之间的差异，并得到一个差分图（different map）。
        # 还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
        diff = cv2.absdiff(background, gray_lwpCV)

        # 二值化阈值处理
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1] 

        # 形态学膨胀
        diff = cv2.dilate(diff, es, iterations=2) 

        # 显示矩形框
        # 该函数计算一幅图像中目标的轮廓
        image, contours, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        for c in contours:

            # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            if cv2.contourArea(c) < 1500: 
                continue

            # 该函数计算矩形的边界框
            (x, y, w, h) = cv2.boundingRect(c) 
            cv2.rectangle(frame_lwpCV, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if len(contours) > 0:
            output.write(frame_lwpCV)

        # 更新背景
        counter +=1
        if counter == 150:
            counter = 0
            background = gray_lwpCV
        
        # 显示结果图像
        #cv2.imshow('contours', frame_lwpCV)
        #cv2.imshow('gary', gray_lwpCV)
        #cv2.imshow('dis', diff)

        # 按'esc'健退出循环
        # key = cv2.waitKey(1) & 0xFF
        # if key == ord('q'):
        #     d['status'] = False
        #     break

    # When everything done, release the capture
    output.release()
    #cv2.destroyAllWindows()


def get_rtps(e,d):
    # 获取网络摄像头
    camera = cv2.VideoCapture('rtsp://admin:PSAXMJ@192.168.2.129:554/h264/ch1/main/av_stream')
    print('成功连接摄像头')
    # 测试用,查看视频size,fps
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    if fps > 30:
        fps = 14

    d['size'] = size
    d['fps'] = fps
    # 判断视频是否打开
    while camera.isOpened():

        # 读取视频流
        ret, frame_lwpCV = camera.read()
        if ret == True:
            d['image'] = frame_lwpCV

        # 停止主进程阻塞
        if e.is_set():
            pass
        else:
            e.set()

        if d['status'] == False:
            break

    camera.release()

if __name__ == '__main__':
    print("目标检测启动,按q 结束程序")
    e = mp.Event()
    with mp.Manager() as manager:
        d = manager.dict()
        d['status'] = True

        get_image = mp.Process(target = get_rtps,args = (e,d))
        get_image.start()
        print('视频捕获进程启动')

        object_detection(e,d)

        get_image.join()
        print('程序结束')
        