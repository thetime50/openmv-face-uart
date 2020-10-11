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

import sensor, time, image, pyb, os

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

# Load Haar Cascade
# By default this will use all stages, lower satges is faster but less accurate.
face_cascade = image.HaarCascade("frontalface", stages=25)
print(face_cascade)

# FPS clock
clock = time.clock()




#########################################
#################参数定义#################
#########################################

THRESHOLD_SIZE = 7000 # 脸部大小阈值

RED_LED_PIN = 1
BLUE_LED_PIN = 3

#########################################





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

def sampling(user,cnt,interval = 3000):
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

        img = sensor.snapshot().save(photoFpath) # or "example.bmp" (or others)


        descDpath = "desc/%s" % (user)
        descFpath = descDpath + "/%s.orb" % (n)
        try:
            os.listdir(descDpath)
        except:
            os.mkdir(descDpath)

        d0 = img.find_lbp((0, 0, img.width(), img.height()))
        image.save_descriptor(d0,descFpath)

        pyb.LED(BLUE_LED_PIN).off()
    print("finished!")



def main():

    sampling('233',5,1000)
    while (True):
        clock.tick()

        # Capture snapshot
        img = sensor.snapshot()

        face = facsTest(img)
        #print(face,face and (face[2] * face[3]),bool(face))

        # Print FPS.
        # Note: Actual FPS is higher, streaming the FB makes it slower.
        #print(clock.fps())

main()
