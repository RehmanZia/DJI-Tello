from tkinter import *
from tkinter import messagebox
from djitellopy import tello
from time import sleep
import sqlite3
import os
import numpy as np
import math
import sys
import pygame
import cv2

def getData(id):
    conn = sqlite3.connect("InviteListInfro.db")
    cmd = "SELECT * FROM PeoplesInfo WHERE ID=" + str(id)
    cursor = conn.execute(cmd)
    profile = None
    for row in cursor:
        profile = row
    conn.commit()
    conn.close()
    return profile

def getKey(keyName):

    ans = False

    for eve in pygame.event.get(): pass

    keyInput = pygame.key.get_pressed()

    myKey = getattr(pygame, 'K_{}'.format(keyName))

    #print('K_{}'.format(keyName))

    if keyInput[myKey]:

        ans = True

    pygame.display.update()

    return ans


######## PARAMETERS ###########

fSpeed = 280 / 10  # Forward Speed in cm/s   (29cm/s)

aSpeed = 360 / 10  # Angular Speed Degrees/s  (50d/s)

interval = 0.25

dInterval = fSpeed * interval

aInterval = aSpeed * interval

###############################################
x, y = 40, 40

a = 0

yaw = 0

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
#video_capture = cv2.VideoCapture(0)

# Call the trained model yml file to recognize faces
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("Trainer1.yml")

# Names corresponding to each id
names = []
for users in os.listdir("images"):
    names.append(users)


def findFace(faces,img,gray,count):
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y + h, x:x + w]  # roi is region of intreset for gray img
        color_img = img[y:y + h, x:x + w]
        end_cord_x = x + w
        end_cord_y = y + h
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, conf = recognizer.predict(roi_gray)
        #print(conf)
        if conf>120:
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
            filepath = 'Unauthorized Individuals/' + str(count) + '.jpg'
            cv2.imwrite(filepath, color_img)
            print("Unknown Person Detected")
        else:
            profile = getData(id)
            #cv2.putText(img, str(profile[1]), (x, y - 60), font, 0.9, color, stroke, cv2.LINE_AA)
            #if profile != None:
                #cv2.putText(img, str(profile[1]), (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 1, cv2.LINE_AA)
                #cv2.putText(img, str(profile[6]), (x, y - 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv2.LINE_AA)
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


            items_list = os.listdir('Authorized Individuals')
            if profile[1] in items_list:
                pass
            else:
                filepath = 'Authorized Individuals/' + str(names[id - 1]) + '.jpg'
                cv2.imwrite(filepath, color_img)
    return img

def getKeyboardInput(me):

    speed = 25
    aspeed=50

    global x, y, yaw, a
    d = 0

    Left_Right, Foward_Backword, Up_Down, Yawn_Velocity = 0, 0, 0, 0


    if getKey("LEFT"):
        Left_Right = -speed
        d = dInterval
        a = -180

    elif getKey("RIGHT"):
        Left_Right = speed
        d = -dInterval
        a = 180

    if getKey("UP"):
        Foward_Backword = speed
        d = dInterval

        a = -270

    elif getKey("DOWN"):
        Foward_Backword = -speed
        d = -dInterval

        a = +90

    if getKey("w"):Up_Down = speed

    elif getKey("s"): Up_Down = -speed

    if getKey("a"):
        Yawn_Velocity = -aspeed

        yaw -= aInterval

    elif getKey("d"):
        Yawn_Velocity = aspeed
        yaw += aInterval

    if getKey("q"):
        me.land()
        sleep(3)
        pygame.quit()
        me.stop_video_capture()


    if getKey("e"):
        me.takeoff()

    sleep(interval)
    a += yaw

    x += int(d * math.cos(math.radians(a)))

    y += int(d * math.sin(math.radians(a)))

    return [Left_Right, Foward_Backword, Up_Down, Yawn_Velocity,x,y]

def start(window):
    count = 1
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    me=tello.Tello()
    me.connect()
    print(me.get_battery())
    win = pygame.display.set_mode((400, 400))
    me.streamon()
    points = [(0, 0), (0, 0)]
    while True:
        vals = getKeyboardInput(me)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        imag = np.zeros((700, 700, 3), np.uint8)
        if (points[-1][0] != vals[4] or points[-1][1] != vals[5]):
            points.append((vals[4], vals[5]))
        x_coordinate = ((points[-1][0] - 40) / 100)
        y_coordinate = ((points[-1][1] - 40) / 100)
        Location_entry = Label(text=(x_coordinate, y_coordinate, "m"))
        Location_entry.place(x=180, y=370)
        print(x_coordinate, ",", y_coordinate, "m")
        img = me.get_frame_read().frame
        img=cv2.resize(img,(400,400))
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4
        )
        findFace(faces, img, gray,count)
        count+=1
        cv2.imshow("Image", img)
        # Location_entry = Entry(window,text=(x_coordinate,y_coordinate,"m"))
        # Location_entry.place(x=30, y=370)
        if cv2.waitKey(1) & 0xFF == ord('y'):
            me.land()
            break

    cv2.destroyAllWindows()


def home(window):
    window.destroy()
    os.system("testpython.py")
    #os.system("HomeWindow.py")
    sys.exit()

def quit(window):
    window.destroy()
    sys.exit()


def main():
    window=Tk()
    window.geometry("700x500")
    window.resizable(False, False)
    window.title("Survillance App")
    window.configure(bg='#003e53')

                #****Labels****
    Title = Label(window,text="Manual Control",fg="White",bg="#003e53" ,font=("bold",18))
    Title.place(x=15,y=8)
    Operation_Label= Label(window,text="Operation   ",font=("bold",12))
    Operation_Label.place(x=30,y=50)
    Key_Label= Label(window,text="Key                   ",font=("bold",12))
    Key_Label.place(x=150,y=50)
    Operation2_Label= Label(window,text="Operation   ",font=("bold",12))
    Operation2_Label.place(x=330,y=50)
    Key_Label2= Label(window,text="Key                   ",font=("bold",12))
    Key_Label2.place(x=450,y=50)
    Forword_Arrow_Label= Label(window,text="Move Forward   ")
    Forword_Arrow_Label.place(x=30,y=90)
    Backward_Arrow_Label= Label(window,text="Move Backward")
    Backward_Arrow_Label.place(x=30,y=130)
    Right_Arrow_Label= Label(window,text="Move Right        ")
    Right_Arrow_Label.place(x=30,y=170)
    Left_Arrow_Label= Label(window,text="Move Left           ")
    Left_Arrow_Label.place(x=30,y=210)
    Take_Off_Label= Label(window,text="Take Off              ")
    Take_Off_Label.place(x=30,y=250)
    Land_Off_Label= Label(window,text="Land                    ")
    Land_Off_Label.place(x=30,y=290)
    Up_Label= Label(window,text="Up                      ")
    Up_Label.place(x=330,y=90)
    Down_Label= Label(window,text="Down                 ")
    Down_Label.place(x=330,y=130)
    Right_Rotate_Label= Label(window,text="Right-Rotate      ")
    Right_Rotate_Label.place(x=330,y=170)
    Left_Rotate_Label= Label(window,text="Left-Rotate         ")
    Left_Rotate_Label.place(x=330,y=210)
    Stream_On_Label= Label(window,text="Stream-On         ")
    Stream_On_Label.place(x=330,y=250)
    Stream_Off_Label= Label(window,text="Stream-Off        ")
    Stream_Off_Label.place(x=330,y=290)

                    #*****Button*****
    Forward_button= Button(window,text="Up-Arrow                ")
    Forward_button.place(x=150,y=90)
    Back_button= Button(window,text="Down-Arrow           ")
    Back_button.place(x=150,y=130)
    Right_button= Button(window,text="Right-Arrow            ")
    Right_button.place(x=150,y=170)
    Left_button= Button(window,text="Left-Arrow              ")
    Left_button.place(x=150,y=210)
    Take_off_button= Button(window,text="E                               ")
    Take_off_button.place(x=150,y=250)
    Land_button= Button(window,text="Q                              ")
    Land_button.place(x=150,y=288)
    Up_button= Button(window,text="W                             ")
    Up_button.place(x=450,y=90)
    Down_button= Button(window,text="S                               ")
    Down_button.place(x=450,y=130)
    Right_Rotate_button= Button(window,text="D                              ")
    Right_Rotate_button.place(x=450,y=170)
    Left_Rotate_button= Button(window,text="A                              ")
    Left_Rotate_button.place(x=450,y=210)
    Stream_on_button= Button(window,text="R                              ")
    Stream_on_button.place(x=450,y=250)
    Stream_off_button= Button(window,text="T                              ")
    Stream_off_button.place(x=450,y=288)
    start_button= Button(window,text="Start                ",command=lambda :start(window))
    start_button.place(x=30,y=330)

    Login_button= Button(window,text="Back           ",command=lambda :home(window))
    Login_button.place(x=250,y=450)
    Quit_button= Button(window,text="Quit           ",command=lambda :quit(window))
    Quit_button.place(x=350,y=450)



    window.mainloop()

if __name__ == '__main__':


    while True:

        main()




