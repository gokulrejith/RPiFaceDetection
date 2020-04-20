import io
import picamera
import cv2
import numpy
from firebase import firebase
import RPi.GPIO as GPIO
import time
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO_TRIGGER = 8
GPIO_ECHO = 12
DELAY = 40
LOOPON = 38
n = 1
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(DELAY, GPIO.OUT)
GPIO.setup(LOOPON, GPIO.OUT)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

firebase = firebase.FirebaseApplication('https://dashboard-39f63.firebaseio.com/')
#def ledblink():
 #   GPIO.output(26, True)
  #  sleep(0.5)
  #  GPIO.output(26, False)
        #ledblink()
try:
    
    while True:
        print(distance())
        if distance() <= 100:
            GPIO.output(LOOPON, True)

#Create a memory stream so photos doesn't need to be saved in a file
            stream = io.BytesIO()

#Get the picture (low resolution, so it should be quite fast)
#Here you can also specify other parameters (e.g.:rotate the image)
            with picamera.PiCamera() as camera:
                camera.resolution = (320, 240)
                camera.capture(stream, format='jpeg')

#Convert the picture into a numpy array
            buff = numpy.frombuffer(stream.getvalue(), dtype=numpy.uint8)

#Now creates an OpenCV image
            image = cv2.imdecode(buff, 1)

#Load a cascade file for detecting faces
            face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/FaceDetection/haarcascade_frontalface_default.xml')

#Convert to grayscale
            gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

#Look for faces in the image using the loaded cascade file
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)

            print("Found "+ str(len(faces)) +" face(s)")

            if len(faces) >=1:
                if distance() <= 100:
                    result= firebase.put('/sensor',"total",n)
                    n += 1
                    GPIO.output(DELAY,True)
                    sleep(1)
                    GPIO.output(DELAY,False)
                    sleep(0.3)
                    GPIO.output(DELAY,True)
                    sleep(0.5)
                    GPIO.output(DELAY,False)
                    print(result)
        

#Draw a rectangle around every found face
                    for (x,y,w,h) in faces:
                        cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)

#Save the result image
                    cv2.imwrite('/home/pi/Desktop/result.jpg',image)
        
        else:
            GPIO.output(LOOPON, False)
        
finally:
    GPIO.output(LOOPON, False)
    GPIO.cleanup()
    
            