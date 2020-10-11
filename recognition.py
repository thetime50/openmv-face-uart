# Face recognition with LBP descriptors.
# See Timo Ahonen's "Face Recognition with Local Binary Patterns".
#
# Before running the example:
# 1) Download the AT&T faces database http://www.cl.cam.ac.uk/Research/DTG/attarchive/pub/data/att_faces.zip
# 2) Exract and copy the orl_faces directory  to the SD card root.


import sensor, time, image, pyb, os

sensor.reset() # Initialize the camera sensor.

###
# sensor.set_pixformat(sensor.GRAYSCALE) # or  sensor.GRAYSCALE
# sensor.set_framesize(sensor.B128X128) # or  sensor.QQVGA (or others)
# sensor.set_windowing((92,112))

###
# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(10) # Let new settings  take affect
sensor.skip_frames(time = 2000) #等待5s




#SUB = "s1"
NUM_SUBJECTS = 2   #图像库中不同人数，一共2人
NUM_SUBJECTS_IMGS = 10  #每人有20张样本图片

img = None

# Load Haar Cascade
# By default this will use all stages, lower satges is faster but less accurate.
face_cascade = image.HaarCascade("frontalface", stages=200)
print(face_cascade)
def facsTest(img,thresholdSize = 9000):
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

def min(pmin, a, s):
    global num
    if a<pmin:
        pmin=a
        num=s
    return pmin
while(True):
    pmin = 999999
    num=0
    #  拍摄当前人脸。
    img = sensor.snapshot()
    face = facsTest(img)
    if not face:
        continue
    #img = image.Image("singtown/%s/1.pgm"%(SUB))
    d0 = img.find_lbp(face,face)
    # d0为当前人脸的lbp特征
    for s in range(1, NUM_SUBJECTS+1):
        dist = 0
        distArr = []
        for i in range(1, NUM_SUBJECTS_IMGS+1):
            photoDpath = "dbg/s%s" % (s)
            photoFpath = photoDpath + "/%s.bmp" % (i)
            img1 = image.Image(photoFpath)
            d1 = img1.find_lbp((0, 0, img1.width(), img1.height()))
            # d1为第s文件夹中的第i张图片的lbp特征
            ds = image.match_descriptor(d0, d1)# 计算d0 d1即样本图像与被检测人脸的特征差异度。
            distArr.append(ds)
            dist += ds
        print("Average dist for subject %d: %d"%(s, dist/NUM_SUBJECTS_IMGS))
        pmin = min(pmin, dist/NUM_SUBJECTS_IMGS, s)# 特征差异度越小，被检测人脸与此样本更相似更匹配。
        print(pmin,distArr)
    sensor.skip_frames(time = 500)
    print(num) # num为当前最匹配的人的编号。
