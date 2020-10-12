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

import sensor, time, image, pyb, os, ustruct

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(time = 2000) #等待5s




#########################################
################ 参数定义 ################
#########################################

THRESHOLD_SIZE = 9000 # 脸部大小阈值
SAMPLING_COUNT = 15

RED_LED_PIN = 1
BLUE_LED_PIN = 3

# UART on pins P4 (TX) and P5 (RX)
uart = pyb.UART(3, 9600, timeout_char = 50)

# HaarCascade 人脸检测
HAAR_FACE_STAGES = 50 # 25 lod #数值越大越严格

# descriptor 样本比较参数
DESC_THRESHOLD = 95 # 70 default 0-100
DESC_FILTER_OUTLIERS = False #False default #true 更宽松


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
#########################################


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


# Load Haar Cascade
# By default this will use all stages, lower satges is faster but less accurate.
face_cascade = image.HaarCascade("frontalface", stages=HAAR_FACE_STAGES)
print(face_cascade)

# FPS clock
clock = time.clock()

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

def facsTest(img,thresholdSize = THRESHOLD_SIZE):
    # Find objects.
    # Note: Lower scale factor scales-down the image more and detects smaller objects.
    # Higher threshold results in a higher detection rate, with more false positives.
    objects = img.find_features(face_cascade, threshold=0.75, scale_factor=1.25)

    # Draw objects
    face = None
    maxSize = 0
    #thresholdSize = 0
    for r in objects:
        size = r[2] * r[3]
        if size > thresholdSize and size > maxSize:
            maxSize = size
            face = r

    face and img.draw_rectangle(face)
    return face

def sampling(user,cnt,interval = 500):
    maxFace = THRESHOLD_SIZE
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
            if face:
                size = face[2] * face[3]
                maxFace = max(maxFace, size)
                if size < maxFace * 0.85:
                    face = None

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
    if not face:
        return matchUser,face

    if not len(users):
        # pyb.delay(timeout)
        return matchUser,face

    nowDesc = img.find_lbp(face)

    for user in users:
        matchResult = 0
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
            matchResult += match
        matchResult= matchResult/(len(files) or 1)
        matchArr.append(matchResult)
        if matchResult < matchMin:
            matchMin = matchResult
            matchUser = user
    print(matchMin,matchUser,matchArr)
    return matchUser,face

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

def registerUser(user):
    sampling(user,SAMPLING_COUNT)
    uartTx(RPS_OK)

def pathForEach(path,cb):
    path = path
    users = os.listdir(path)
    for user in users:
        baseDpath = "%s/%s" %(path,user)
        cb and cb(baseDpath)
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
    user,face = recognition(20)
    print("user:",user,"face:",face)
    if face:
        result = (result | RPS_FACE)
    if user:
        user = int(user)
        result = (result | (user<<4))
    stateTx(result)
    # uartTx(result)


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
