from djitellopy import tello
import time
import cv2
import os

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("Trainer1.yml")

# Names corresponding to each id
names = []
for users in os.listdir("images"):
    names.append(users)

me=tello.Tello()
me.connect()
me.set_speed(25)
print(me.get_battery())
me.takeoff()
me.move_up(100)

