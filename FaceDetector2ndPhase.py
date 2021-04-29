import cv2
import os, sys
from random import randrange
import tkinter as tk
import time
import threading

def get_file_path(filename):
    return os.path.join(sys.path[0],filename)

trained_face_data = cv2.CascadeClassifier(get_file_path('haarcascade_frontalface_default.xml'))
trained_eye_data = cv2.CascadeClassifier(get_file_path('haarcascade_eye_tree_eyeglasses.xml'))

#trained_face_data = cv.CascadeClassifier(get_file_path('haarcascade_eye.xml'))

webcam = cv2.VideoCapture(0)
print("Loaded webcam")

timer_count = 0
blink_count = 0
detecting = False
open_eyes = True
label_font = ("Arial", 30, 'bold')
status_font = ("Arial", 20, 'italic')
time_value = 5

window = tk.Tk()

timer_var = tk.StringVar()
timer_var.set("0")
blink_var = tk.StringVar()
blink_var.set("Blinks: 0")
status_var = tk.StringVar()
status_var.set("STATUS: ")

def detection_thread():
    global blink_var
    global blink_count
    global detecting
    global open_eyes
    global new_blink_count
    while True:
        ret, img = webcam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray,5,1,1)
        faces = trained_face_data.detectMultiScale(gray, 1.3, 5, minSize=(150,150))

        for (x,y,w,h) in faces:

            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            #y_val = int((y+h))
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            eyes = trained_eye_data.detectMultiScale(roi_gray,1.3,5,minSize=(40,40))
        #    print(len(eyes), "EYES", len(eyes[0:2]))
            if len(eyes) == 0:
                open_eyes = False
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                #print(blink_count, "blinkssss")
                #print(detecting)
                if detecting == True and open_eyes == False:
                    blink_count+=1
                    new_blink_count+=1
                    blink_var.set("Blinks: " + str(blink_count))
                open_eyes = True

        cv2.imshow('Face Detector',img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    webcam.release()
    cv2.destroyAllWindows()
    '''
    key = cv.waitKey(1)

    face_coordinates = trained_face_data.detectMultiScale(grayscaled_img)
    print(face_coordinates)
    for (x, y, w, h) in face_coordinates:
        cv.rectangle(resized, (x, y), (x+w, y+h), (randrange(256),randrange(256),randrange(256)), 5)



    cv.imshow("Face Detector", resized)
    cv.waitKey()
'''
detect_thread = threading.Thread(target=detection_thread)
detect_thread.start()

local_seconds = 0
def timer_thread():
    global timer_count
    global local_seconds
    while detecting:
        timer_var.set(str(timer_count))
        time.sleep(1)
        local_seconds += 1
        timer_count +=1
        if local_seconds == time_value:
            check_blinking_status()
            local_seconds = 0
        #print(timer_count)

time_thread = None
def start():
    global detecting
    detecting = True
    print("started")
    time_thread = threading.Thread(target=timer_thread)
    time_thread.start()

def stop():
    global detecting
    detecting = False
    print("stopped")

def reset():
    global timer_count
    global blink_count
    timer_count = 0
    blink_count = 0
    timer_var.set(str(timer_count))
    blink_var.set("Blinks: 0")


previous_blink_count = 0
new_blink_count = 0
def check_blinking_status():
    global previous_blink_count
    global new_blink_count
    print(new_blink_count)
    avg = float(new_blink_count/time_value)
    status = ""
    print(avg, "AVG")
    if new_blink_count > previous_blink_count:
        status = "BLINKING MORE -> AVG (Blinks/5s): " + str(avg)
        print("BLINKING MORE")
    elif new_blink_count < previous_blink_count:
        status = "BLINKING LESS -> AVG (Blinks/5s): " + str(avg)
        print("BLINKING LESS")
    else:
        status = "SAME BLINKING -> AVG (Blinks/5s): " + str(avg)
        print("SAME BLINKING")
    status_var.set(status)
    previous_blink_count = new_blink_count
    new_blink_count = 0


start_button = tk.Button(window, text="Start Blink Detection Timer", width = 20, height=10, command = start)
stop_button = tk.Button(window, text="Stop Blink Detection Timer", width = 20, height=10, command = stop)
reset_button = tk.Button(window, text="Reset", width = 20, height=10, command = reset)
timer_label = tk.Label(window, textvariable = timer_var, width = 20, height=2, font = label_font)
blink_label = tk.Label(window, textvariable = blink_var, width = 25, height=2, font = label_font)
status_label = tk.Label(window, textvariable = status_var, width=40, height=2, font = status_font)
start_button.grid(row=0,column=0)
stop_button.grid(row=0, column=1)
reset_button.grid(row=0, column=2)
timer_label.grid(row=1, column=0, columnspan=3)
blink_label.grid(row=2, column=0, columnspan=3)
status_label.grid(row=3, column=0, columnspan=3)
window.mainloop()


print("Code Completed")
