# Face Detection Example
#
# This example shows off the built-in face detection feature of the OpenMV Cam.
#
# Face detection works by using the Haar Cascade feature detector on an image. A
# Haar Cascade is a series of simple area contrasts checks. For the built-in
# frontalface detector there are 25 stages of checks with each stage having
# hundreds of checks a piece. Haar Cascades run fast because later stages are
# only evaluated if previous stages pass. Additionally, your OpenMV Cam uses
# a data structure called the integral image to quickly execute each area
# contrast check in constant time (the reason for feature detection being
# grayscale only is because of the space requirment for the integral image).

import sensor, time, image, pyb, os, ustruct, lcd

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA) # HQVGA 240x160
# sensor.set_framesize(sensor.HQQVGA) # HQQVGA: 160x80
# sensor.set_framesize(sensor.QQVGA) # QQVGA: 160x120

sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(time = 2000) #等待5s




#########################################
################ 参数定义 ################
#########################################

THRESHOLD_SIZE_MIN = 7000 # 脸部大小阈值
# THRESHOLD_SIZE_MAX = 12000 # 脸部大小阈值
SAMPLING_COUNT = 30 # 15

# HaarCascade 人脸检测
HAAR_FACE_STAGES = 50 # 25 lod #数值越大越严格
HAAR_MOUTH_STAGES = 50
HAAR_NOSE_STAGES = 50

HAAR_MOUTH_CHECK = False #True # 7k
HAAR_NOSE_CHECK = False #True # 1K

# descriptor 样本比较参数
DESC_THRESHOLD = 95 # 70 default 0-100
DESC_FILTER_OUTLIERS = True #False default #True 更宽松
MATCH_THRESHOLD = 3500 # 匹配值小于此值才是匹配到注册过的用户

SAMPLING_SKIP = 3 # 采样前跳过3 个样本
CHECK_MIN_CNT = 6 # 计算最小n个对比人员样本的平均值 如果是0 计算所有的平均值

##
# 重点改MATCH_THRESHOLD和CHECK_MIN_CNT这两个值
##

# 硬件配置
RED_LED_PIN = 1
BLUE_LED_PIN = 3

# UART on pins P4 (TX) and P5 (RX)
uart = pyb.UART(3, 9600, timeout_char = 50)

# cammand 命令
CMD_USER1 = 0x01
CMD_USER2 = 0x02
CMD_USER3 = 0x03
CMD_BREAK = 0x04
CMD_CLEAR = 0x05

# response 应答
RPS_OK = 0x01
RPS_FACE = 0x02
RPS_MASK = 0x03

HAVE_LCD_MODULE = False
#########################################


try:
    lcd.init()
    HAVE_LCD_MODULE = True
    print("lcd init ok")
except:
    HAVE_LCD_MODULE = False
    print("lcd init error")


try:
    os.listdir('desc')
except:
    print('mkdir desc')
    os.mkdir('desc')
try:
    os.listdir('photo')
except:
    print('mkdir photo')
    os.mkdir('photo')

face_cascade = image.HaarCascade("frontalface", stages=HAAR_FACE_STAGES)
def loadFaceCascade():
    # Load Haar Cascade
    # By default this will use all stages, lower satges is faster but less accurate.
    # face_cascade = image.HaarCascade("frontalface", stages=HAAR_FACE_STAGES)
    # # print(face_cascade)
    # return face_cascade
    global face_cascade
    return face_cascade

# https://github.com/opencv/opencv/tree/master/data/haarcascades
# https://github.com/openmv/openmv/blob/master/ml/haarcascade/cascade_convert.py
# https://github.com/atduskgreg/opencv-processing/tree/master/lib/cascade-files #这数据太大了
# https://stackoverflow.com/questions/9015498/need-haar-casscades-for-nose-eyes-lipsmouth
# http://alereimondo.no-ip.org/OpenCV/34 #没法转换

def loadMouthCascade():
    mouth_cascade = None
    try:
        if HAAR_MOUTH_CHECK:
            # mouth_cascade = image.HaarCascade("haar/haarcascade_mcs_mouth.cascade", stages=HAAR_MOUTH_STAGES)
            print("mouth haar loaded")
    except:
        print("no mouth haar cascade")
    return mouth_cascade

def loadNoseCascade():
    nose_cascade = None
    try:
        if HAAR_NOSE_CHECK:
            # nose_cascade = image.HaarCascade("haar/haarcascade_mcs_nose.cascade", stages=HAAR_NOSE_STAGES)
            print("nose haar loaded")
    except:
        print("no nose haar cascade")
    return nose_cascade


# FPS clock
clock = time.clock()


def checkDisplay(img):
    if HAVE_LCD_MODULE:
        lcd.display(img)

def uartTx(val):
    #return uart.writechar(val)
    return uart.write(ustruct.pack("<b", val))
def uartRx():
    # ustruct.pack("<b", val)
    return uart.readchar()

oldState = 0xff
def stateTx(state):
    global oldState
    if state != oldState :
        oldState = state
        return uartTx(state)

def haarTest(img,haar,desSizeMax = 0,draw = True, rio = None):
    # Find objects.
    # Note: Lower scale factor scales-down the image more and detects smaller objects.
    # Higher threshold results in a higher detection rate, with more false positives.
    if not rio:
        rio=[0,0,img.width,img.height]
    objects = img.find_features(haar, threshold=0.75, scale_factor=1.25, rio=rio)

    # Draw objects
    des = None
    maxSize = 0
    #faceSizeMax = 0
    for r in objects:
        size = r[2] * r[3]
        if size > desSizeMax and size > maxSize:
            maxSize = size
            des = r

    draw and des and img.draw_rectangle(des)
    return des

def facsTest(img,faceSizeMax = THRESHOLD_SIZE_MIN):
    face_cascade = loadFaceCascade()
    result = haarTest(img,face_cascade,faceSizeMax)
    # del face_cascade
    return result
def mouthTest(img,mouthSizeMax = 0, rio = None):
    mouth_cascade = loadMouthCascade()
    result = mouth_cascade and haarTest(img,mouth_cascade,mouthSizeMax,rio = rio)
    # del mouth_cascade
    return result
def noseTest(img,noseSizeMax = 0, rio = None):
    nose_cascade = loadNoseCascade()
    result = nose_cascade and haarTest(img,nose_cascade,noseSizeMax,rio = rio)
    # del nose_cascade
    return result

def samplingSkip(cnt,faceSizeMax = THRESHOLD_SIZE_MIN,interval = 300):
    size = 0
    maxFace = faceSizeMax
    face = None
    img = None
    for i in range(cnt):
        pyb.delay(interval)
        while not face:
            pyb.LED(BLUE_LED_PIN).on()
            img = sensor.snapshot()
            face = facsTest(img,faceSizeMax)
            checkDisplay(img)
            if face:
                size = face[2] * face[3]
                maxFace = max(maxFace, size)
                if size < maxFace * 0.85:
                # if False: # 不做大脸判断了
                    face = None
                else:# 只有这里是有效face
                    pyb.LED(BLUE_LED_PIN).off()
    print("samplingSkip",size)
    pyb.LED(BLUE_LED_PIN).off()
    return size
    

def sampling(user,cnt,interval = 500):
    # maxFace = THRESHOLD_SIZE_MIN
    maxFace = samplingSkip(SAMPLING_SKIP)
    clearUser(user)
    for n in range(cnt):
        #红灯亮
        pyb.LED(RED_LED_PIN).on()
        sensor.skip_frames(time = interval) # Give the user time to get ready.等待3s，准备一下表情。

        #红灯灭，蓝灯亮
        pyb.LED(RED_LED_PIN).off()
        pyb.LED(BLUE_LED_PIN).on()

        #保存截取到的图片到SD卡
        photoDpath = "photo/%s" % (user)
        photoFpath = photoDpath + "/%s.bmp" % (n)
        try:
            os.listdir(photoDpath)
        except:
            os.mkdir(photoDpath)

        face = None
        img = None
        
        while not face:
            img = sensor.snapshot()
            face = facsTest(img)
            checkDisplay(img)
            if face:
                size = face[2] * face[3]
                if size < maxFace * 0.88:
                    face = None
                elif size > maxFace:
                    maxFace = maxFace*0.35 + size*(1-0.35)

        img.save(photoFpath,face) # or "example.bmp" (or others)

        descDpath = "desc/%s" % (user)
        descFpath = descDpath + "/%s.lbp" % (n)
        try:
            os.listdir(descDpath)
        except:
            os.mkdir(descDpath)

        d0 = img.find_lbp(face)
        image.save_descriptor(d0,descFpath)

        pyb.LED(BLUE_LED_PIN).off()
        print(descFpath)
    print("finished!")

def recognition(timeout = 500):
    face = None
    img = None

    matchMin = 999999
    matchUser = ''
    matchArr = []

    basePath = "photo"
    #basePath = "desc"
    users = os.listdir(basePath)

    time_start = pyb.millis()
    while not face:
        if pyb.elapsed_millis(time_start) > timeout:
            break
        img = sensor.snapshot()
        face = facsTest(img)
        checkDisplay(img)
    if not face:
        return matchUser,face,img

    if not len(users):
        # pyb.delay(timeout)
        return matchUser,face,img

    nowDesc = img.find_lbp(face)

    photoFpath = ""
    try:
        for user in users:
            userDescArr = []
            baseDpath = "%s/%s" %(basePath,user)
            files = os.listdir(baseDpath)
            for file_ in files:
                # descFpath = baseDpath+"/"+file_
                # oldDesc = image.load_descriptor(descFpath)

                photoFpath = baseDpath+"/"+file_
                oldImg = image.Image(photoFpath)
                oldDesc = oldImg.find_lbp((0, 0, oldImg.width(), oldImg.height()))

                match = image.match_descriptor(
                    nowDesc, oldDesc,
                    DESC_THRESHOLD,
                    DESC_FILTER_OUTLIERS
                )
                userDescArr.append(match)
            userDescArr.sort()
            sliceCnt = CHECK_MIN_CNT or len(userDescArr)
            matchResult= sum(userDescArr[:sliceCnt])/sliceCnt
            matchArr.append(matchResult)
            # print("sliceCnt,userDescArr: ",sliceCnt,userDescArr)
            if matchResult < matchMin :
                matchMin = matchResult
                if matchResult < MATCH_THRESHOLD:
                    matchUser = user
    except : # OSError,err:
        print("recognition error:",photoFpath) # ,err)

    print(matchMin,matchUser,matchArr,len(matchArr)>=2 and (matchArr[0]-matchArr[1]))
    return matchUser,face,img

def debugFun():
    #sampling('233',10,500)
    #sensor.skip_frames(time = 1500) #等待5s
    #sampling('666',10,500)
    while (True):
        clock.tick()
        matchUser = recognition()
        print(matchUser)

        # # Capture snapshot
        # img = sensor.snapshot()

        # face = facsTest(img)
        # print(face,face and (face[2] * face[3]),bool(face))

        # Print FPS.
        # Note: Actual FPS is higher, streaming the FB makes it slower.
        #print(clock.fps())

        img = sensor.snapshot()
        # facsTest(img)
        mouthTest(img)
        noseTest(img)

def registerUser(user):
    sampling(user,SAMPLING_COUNT)
    uartTx(RPS_OK)

def pathForEach(path,cb):
    path = path
    try:
        users = os.listdir(path)
    except:
        print("no path:",path)
        return
    for user in users:
        baseDpath = "%s/%s" %(path,user)
        cb and cb(baseDpath)

def clearUser(user):
    user = str(user)
    print("clearUser:",user)
    def rmFile(path):
        os.remove(path)
    pathForEach("photo/"+user,rmFile)
    try:
        os.rmdir("photo/"+user)
    except:
        pass
    pathForEach("desc/"+user,rmFile)
    try:
        os.rmdir("desc/"+user)
    except:
        pass
    uartTx(RPS_OK)

def clearUsers():
    print("clearUsers")
    def rmFile(path):
        os.remove(path)
    def rmPath(path):
        pathForEach(path,rmFile)
        os.rmdir(path)
    pathForEach("photo",rmPath)
    pathForEach("desc",rmPath)
    uartTx(RPS_OK)

def checkUser():
    result = 0
    user,face,img = recognition(20)

    img and face and mouthTest(img, rio = face)
    img and face and noseTest(img, rio = face)

    print("user:",user,"face:",face)
    if face:
        result = (result | RPS_FACE)
    if user:
        user = int(user)
        result = (result | (user<<4))
    # stateTx(result)
    uartTx(result)


def appFun():
    timeStart = pyb.millis()
    timeCheck = pyb.millis()
    while (True):
        nowTime = pyb.elapsed_millis(timeStart)
        if nowTime % 1000 > 1:
            pyb.LED(RED_LED_PIN).off()
        elif nowTime>1000:
            pyb.LED(RED_LED_PIN).on()
            timeStart = pyb.millis()
        val = uartRx()
        if val != -1:
            pyb.LED(RED_LED_PIN).off()
            if val == CMD_USER1 :
                registerUser(1)
            elif val == CMD_USER2 :
                registerUser(2)
            elif val == CMD_USER3 :
                registerUser(3)
            elif val == CMD_CLEAR:
                clearUsers()
        else:
            deltaTime = pyb.elapsed_millis(timeCheck)
            if deltaTime>500:
                pyb.LED(RED_LED_PIN).off()
                timeCheck = pyb.millis()
                checkUser()

def main():
    # debugFun()
    appFun()

main()
