import cv2
import multiprocessing as mp
import numpy
import time 

def object_detection(e,d):
    r"""
    """
    now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())

    bs=cv2.createBackgroundSubtractorKNN(detectShadows=True)

    #阻塞等待视频流
    e.wait()


    # 设置保存名称和编码格式
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    output = cv2.VideoWriter('{}.avi'.format(now),fourcc,d['fps'],d['size'])
    print('创建文件{}.avi'.format(now))

    print('开始处理')
    计时起点 = time.time()
    帧计数 = 0

    while True:

        # 读取视频流
        frame_lwpCV = d['image']
        fgmask=bs.apply(frame_lwpCV)
        th=cv2.threshold(fgmask.copy(),244,255,cv2.THRESH_BINARY)[1]
        th=cv2.erode(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=2)
        
        dilated=cv2.dilate(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=2)
        
        contours,_=cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        是否录制 = False
        for c in contours:
            if cv2.contourArea(c)>300:
                (x,y,w,h)=cv2.boundingRect(c)
                cv2.rectangle(frame_lwpCV,(x,y),(x+w,y+h),(255,255,0),2)
                是否录制 = True
        
        if len(contours) > 0 and 是否录制 == True:
            output.write(frame_lwpCV)
        
        # 显示结果图像
        cv2.imshow("mog",fgmask)
        cv2.imshow("detection",frame_lwpCV)
        #按'q'健退出循环
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            d['status'] = False
            break

        帧计数 += 1
        e.clear()
        e.wait()
    计时终点 = time.time()
    print('总计处理{}帧，平均处理时间{:.2f}毫秒/帧，平均处理帧率{:.2f}'.format(帧计数,((计时终点-计时起点)/帧计数)*1000,帧计数/(计时终点-计时起点)))
    #处理完毕，释放所有资源
    output.release()
    cv2.destroyAllWindows()
    print('完成录像，释放资源')


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


    计时起点 = time.time()
    帧计数 = 0

    # 判断视频是否打开
    while camera.isOpened():

        # 读取视频流
        ret, frame_lwpCV = camera.read()
        if ret == True:
            d['image'] = frame_lwpCV
            帧计数 += 1
            e.set()

        if d['status'] == False:
            break

    camera.release()
    e.set()
    计时终点 = time.time()
    print('捕捉图像子进程结束共计{}帧'.format(帧计数))
    print('平均捕获时间{:.2f}毫秒/帧,平均捕获帧率{:.2f}'.format(((计时终点-计时起点)/帧计数)*1000,帧计数/(计时终点-计时起点)))

if __name__ == '__main__':
    print("目标检测启动,按q 结束程序")
    e = mp.Event()
    with mp.Manager() as manager:
        d = manager.dict()
        d['status'] = True

        get_image = mp.Process(target = get_video,args = (e,d))
        get_image.start()
        print('视频捕获进程启动')

        object_detection(e,d)

        get_image.join()
        print('程序结束')
