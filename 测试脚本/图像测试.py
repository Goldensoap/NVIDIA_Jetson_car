import cv2


if __name__ == '__main__':

    cv2.namedWindow('contours',0)

    camera = cv2.VideoCapture('tcp://192.168.2.237:8090')
    # 测试用,查看视频尺寸,帧率
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    print('成功连接摄像头 size:{},fps:{}'.format(str(size),str(fps)))

    while camera.isOpened():
        # 读取视频流
        ret, frame_lwpCV = camera.read()
        if ret == True:
            video = frame_lwpCV

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        cv2.imshow('contours', video)

    cv2.destroyAllWindows()
