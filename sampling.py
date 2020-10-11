# Snapshot Example
#
# Note: You will need an SD card to run this example.
#
# You can use your OpenMV Cam to save image files.

import sensor, image, pyb, os

RED_LED_PIN = 1
BLUE_LED_PIN = 3

sensor.reset() # Initialize the camera sensor.

###
# sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE
# sensor.set_framesize(sensor.B128X128) # or sensor.QQVGA (or others)
# sensor.set_windowing((92,112))

###
# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(10) # Let new settings take affect.
sensor.skip_frames(time = 2000)

num = 2 #设置被拍摄者序号，第一个人的图片保存到s1文件夹，第二个人的图片保存到s2文件夹，以此类推。每次更换拍摄者时，修改num值。

n = 10 #设置每个人拍摄图片数量。

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


#连续拍摄n张照片，每间隔3s拍摄一次。
while(n):
    #红灯亮
    pyb.LED(RED_LED_PIN).on()
    sensor.skip_frames(time = 400) # Give the user time to get ready.等待3s，准备一下表情。

    #红灯灭，蓝灯亮
    pyb.LED(RED_LED_PIN).off()
    pyb.LED(BLUE_LED_PIN).on()

    #保存截取到的图片到SD卡
    print(n)
    photoDpath = "dbg/s%s" % (num)
    photoFpath = photoDpath + "/%s.bmp" % (n)
    try:
        os.listdir(photoDpath)
    except:
        os.mkdir(photoDpath)
    img = sensor.snapshot()
    face = facsTest(img)
    if not face:
        continue
    img.save(photoFpath,face) # or "example.bmp" (or others)

    n -= 1

    pyb.LED(BLUE_LED_PIN).off()
    print(photoFpath)
    print("Done! Reset the camera to see the saved image.")

print("finished!")
