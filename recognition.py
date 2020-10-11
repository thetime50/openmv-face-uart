# Face recognition with LBP descriptors.
# See Timo Ahonen's "Face Recognition with Local Binary Patterns".
#
# Before running the example:
# 1) Download the AT&T faces database http://www.cl.cam.ac.uk/Research/DTG/attarchive/pub/data/att_faces.zip
# 2) Exract and copy the orl_faces directory  to the SD card root.


import sensor, time, image, pyb, os

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # or  sensor.GRAYSCALE
sensor.set_framesize(sensor.B128X128) # or  sensor.QQVGA (or others)
sensor.set_windowing((92,112))
sensor.skip_frames(10) # Let new settings  take affect
sensor.skip_frames(time = 2000) #等待5s



#SUB = "s1"
NUM_SUBJECTS = 1   #图像库中不同人数，一共2人
NUM_SUBJECTS_IMGS = 8  #每人有20张样本图片

#  拍摄当前人脸。
img = sensor.snapshot()
#img = image.Image("singtown/%s/1.pgm"%(SUB))
d0 = img.find_lbp((0, 0, img.width(), img.height()))
# d0为当前人脸的lbp特征
img = None
pmin = 999999
num=0

def min(pmin, a, s):
    global num
    if a<pmin:
        pmin=a
        num=s
    return pmin
while(True):
    for s in range(1, NUM_SUBJECTS+1):
        dist = 0
        for i in range(1, NUM_SUBJECTS_IMGS+1):
            photoDpath = "dbg/s%s" % (s)
            photoFpath = photoDpath + "/%s.bmp" % (i)
            print(photoFpath)
            img = image.Image(photoFpath)
            d1 = img.find_lbp((0, 0, img.width(), img.height()))
            # d1为第s文件夹中的第i张图片的lbp特征
            dist += image.match_descriptor(d0, d1)# 计算d0 d1即样本图像与被检测人脸的特征差异度。
        print("Average dist for subject %d: %d"%(s, dist/NUM_SUBJECTS_IMGS))
        pmin = min(pmin, dist/NUM_SUBJECTS_IMGS, s)# 特征差异度越小，被检测人脸与此样本更相似更匹配。
        print(pmin)
    sensor.skip_frames(time = 2000)
    print(num) # num为当前最匹配的人的编号。
