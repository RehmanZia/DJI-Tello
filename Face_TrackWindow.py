import cv2
import numpy as np
from djitellopy import tello
import time
from tkinter import *
import os
import pickle
import sqlite3



recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("Trainer1.yml")

names = []
for users in os.listdir("images"):
    names.append(users)


w, h = 360, 240

fbRange = [6000, 6500]

pid = [0.4, 0.4, 0]

def findFace(img):

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        imgGray, scaleFactor=1.1, minNeighbors=4
    )
    myFaceListC = []

    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        """cv2.putText(
            img,
            "Zia",
            (x, y - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            1,
            cv2.LINE_AA,1,
        )
        cv2.putText(
            img,
            "yes",
            (x, y - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )"""
        id, conf = recognizer.predict(imgGray)
        if conf > 120:
            cv2.putText(
                img,
                "Unknown",
                (x, y - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                1,
                cv2.LINE_AA,
            )
            print("Unknown Person Detected")
        else:
            #profile = getData(id)
            # cv2.putText(img, str(profile[1]), (x, y - 60), font, 0.9, color, stroke, cv2.LINE_AA)
            cv2.putText(
                img,
                names[id - 1],
                (x, y - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                "Yes",
                (x, y - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        cx = x + w // 2

        cy = y + h // 2

        area = w * h

        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        myFaceListC.append([cx, cy])

        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:

        i = myFaceListArea.index(max(myFaceListArea))

        return img, [myFaceListC[i], myFaceListArea[i]]

    else:

        return img, [[0, 0], 0]

def trackFace( info, w, pid, pError,me):

    area = info[1]

    x, y = info[0]

    fb = 0

    error = x - w//2

    speed = pid[0] * error + pid[1] * (error - pError)

    speed = int(np.clip(speed, -100, 100))

    if area > fbRange[0] and area < fbRange[1]:

        fb = 0

    elif area > fbRange[1]:

        fb = -10

    elif area < fbRange[0] and area != 0:

        fb = 10

    if x == 0:

        speed = 0

        error = 0


    me.send_rc_control(0, fb, 0, speed)

    return error


def start():
    pError = 0

    me = tello.Tello()
    me.connect()
    me.streamon()
    print(me.get_battery())

    me.takeoff()

    me.send_rc_control(0, 0, 25, 0)
    time.sleep(3.2)
    while True:

        # _, img = cap.read()

        img = me.get_frame_read().frame

        img = cv2.resize(img, (w, h))

        img, info = findFace(img)

        pError = trackFace(info, w, pid, pError,me)

        print("Center", info[0], "Area", info[1])

        cv2.imshow("Output", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()

            break




def home(window):
    window.destroy()
    os.system("HomeWindow.py")

def quit(window):
    window.destroy()
    sys.exit()



window = Tk()
window.geometry("400x400")
window.resizable(False, False)
window.title("Survillance App")
window.configure(bg='#003e53')

Title = Label(window, text="Tracking", fg="White", bg="#003e53", font=("bold", 18))
Title.place(x=150, y=8)

First_Name = Label(window, text="First Name", fg="White", bg="#003e53", font=(14))
First_Name.place(x=50, y=100)

Last_Name = Label(window, text="Last Name", fg="White", bg="#003e53", font=(14))
Last_Name.place(x=50, y=150)

FirstName_Entry = Entry(window)
FirstName_Entry.place(x=150,y=104)
LastName_Entry = Entry(window)
LastName_Entry.place(x=150, y=154)

fname=FirstName_Entry.get()

home_button = Button(window,text="Home",fg="Black",bg="White",font=(12),command=lambda :home(window))
home_button.place(x=150,y=250)
quit_button = Button(window, text="Quit", fg="Black", bg="White", font=(12),command=lambda :quit(window))
quit_button.place(x=50, y=250)
start_button = Button(window, text="Start", fg="Black", bg="White", font=(12),command = start)
start_button.place(x=250, y=250)


window.mainloop()





