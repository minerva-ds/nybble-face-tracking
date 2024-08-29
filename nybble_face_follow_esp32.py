import serial
#import threading
import time
import cv2
#import urllib.request
import numpy as np
import os
import math
import sys
import requests
#from nybble_face_follow_procedures import *
import facefollow_includes.procedures as nfp
#ret = os.system('sudo bash bind_rfcomm0.sh')

#joints 

'''Flags'''
connwifi = False
test_camcenter = False
wait_for_serial_ready = True
detectionEnabled = False
record_video = True
record_video = False

'''Face Tracking Config'''
#in seconds
move_delay = .01 
#cut down on servo commands only track if it's this far out of alignment, in pixels
alignment_window = 15
reset_time = 5
last_movement_time = 0

'''Face Detection Models'''
face_threshold = .6
#face_threshold = .7
dir_path = os.path.dirname(os.path.realpath(__file__))
# download model and prototxt from https://github.com/spmallick/learnopencv/tree/master/FaceDetectionComparison/models
modelFile = dir_path+"/models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
configFile = dir_path+"/models/deploy.prototxt"

'''ESP32 Settings'''
URL = "http://192.168.4.1"
AWB = True

'''connect wifi to cam (disabled by default)'''
if connwifi:
    # scan available Wifi networks
    ret = os.system('nmcli d wifi list > /dev/null')
    #print(ret)
    ret = os.system('nmcli d wifi connect "ESP32-CAM Access Point"')
    print(ret)

'''Stream from ESP32'''
cap = cv2.VideoCapture(URL + ":81/stream")
#face_classifier = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_alt.xml') # insert the full path to haarcascade file if you encounter any problem

#set to 320 x 240
set_resolution = False
if set_resolution:
    resolution_check_xy = {7:[320,480],4:[240,240]}
    resolution_index=7
    nfp.set_resolution(URL, index=resolution_index)
    check_resolution = resolution_check_xy[resolution_index]
    AWB = nfp.set_awb(URL, AWB)

    '''capture a frame to get resolution'''
    ret, frame = cap.read()
    if not ret:
        print("can't get camera stream")
        sys.exit()
    await_resolution = True
    time.sleep(1)
    numtries=0
    while await_resolution:
        ret, frame = cap.read()
        if not ret:
            print("can't get camera stream")
            sys.exit()
        if numtries > 10:
            print("failed to match resolution")
            sys.exit()
            
        if frame.shape[0] == check_resolution[0] and frame.shape[1] == check_resolution[1]:
            await_resolution=False
        else:
            numtries+=1
            time.sleep(1)
            
    print("matched resolutions")
    
'''capture a frame to get resolution'''
ret, frame = cap.read()
frame = cv2.rotate(frame,cv2.ROTATE_180)
if not ret:
    print("can't get camera stream")
    sys.exit()

'''Camera Pixels Per Degree'''
#resolution = [640,480]
#resolution = [320,240]
resolution = [frame.shape[1],frame.shape[0]]
camcenter = [int(resolution[0]/2),int(resolution[1]/2)]
viewangle = 90
resolution_squares = (math.pow(resolution[0],2) + math.pow(resolution[1],2))
diagnolpixels = math.sqrt(resolution_squares)
degrees_per_pixel = viewangle/diagnolpixels
pixels_per_degree = diagnolpixels/viewangle
print(f'resolution {resolution[0]} x {resolution[1]}')
print(f'camcenter {camcenter[0]} x {camcenter[1]}')
print(f'viewangle {viewangle}')
print(f'resolution_squares {resolution_squares}')
print(f'diagnolpixels {diagnolpixels}')
print(f'degrees per pixel {degrees_per_pixel}')

if test_camcenter:
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    #print(f'resolution2 :{frameWidth} x {frameHeight}')
    #paint the camera center
    x1 = int(camcenter[0] - alignment_window)
    y1 = int(camcenter[1] - alignment_window)
    x2 = int(camcenter[0] + alignment_window)
    y2 = int(camcenter[1] + alignment_window)
    while True:
        print(f'resolution2 :{frameWidth} x {frameHeight}')
        ret, frame = cap.read()
        frame = cv2.rotate(frame,cv2.ROTATE_180)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), int(round(frameHeight / 150)), 8,)
        cv2.imshow('Face', frame)
        key = cv2.waitKey(1) & 0xFF    

        if key == ord("q"):
            sys.exit()

'''simulate move'''
deltax = -resolution[0]/2
xdeg = deltax * degrees_per_pixel
tomovex = 0 + int(xdeg)
print(f"simulate moving to {deltax}px on screen is {tomovex} degrees")

deltay = -resolution[1]/2
ydeg = deltay * degrees_per_pixel
tomovey = 0 + int(ydeg)
print(f"simulate moving to {deltay}px on screen is {tomovey} degrees")

'''Setup Serial over Bluetooth'''
baudrate = 115200
port = '/dev/rfcomm0'  # set the correct port before run it

'''Offsets for head joints and safety'''
m0offset = 0
#m0 positive = turn left and rotate clockwise
#m0 negative = turn right and rotate counterclockwise
m0max = 50
m0min = 50

m1offset = -45 
#m1 positive = look up
#m1 negative = look down 
m1max = 35 
m1min = -70 


'''Open Serial'''
s = serial.Serial(port=port, baudrate=baudrate,timeout=2)
if s.is_open:
    print("Serial Port Open!")
else:
    print("Could not open serial port")
    sys.exit()

'''Serial Ready'''
if wait_for_serial_ready:
    nfp.read_serial_until("Ready!",s)

#nfp.write_serial("j0",s)
#nfp.read_serial_until("=",s)

nfp.clear_in_waiting(s)
sit = f"i 0 {m0offset} 1 {m1offset} 2 80 8 35 9 35 10 -60 11 -60 12 62 13 62 14 35 15 40"

#turn off AI moving joints
nfp.write_serial("c",s)
nfp.read_serial_until("c",s)

#manually configure position
nfp.write_serial(sit,s)
nfp.read_serial_until("i",s)

'''setup the models for face detection'''
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

moved_await_reply = 0


'''setup recording stream to video file'''
if record_video:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (resolution[0],resolution[1]))
while True:
    try:
        if not cap.isOpened():
            print("capture not opened")
            time.sleep(1)
            pass

        ret, frame = cap.read()
        frame = cv2.rotate(frame,cv2.ROTATE_180)
        #frameHeight = frame.shape[0]
        #frameWidth = frame.shape[1]
        #print(f'resolution :{frameWidth} x {frameHeight}')

        if ret:
            timenow = time.perf_counter()

            if detectionEnabled == True:
                outOpencvDnn, bboxes = nfp.detectFaceOpenCVDnn(net, frame,cv2=cv2,conf_threshold=face_threshold)

                frameWidth = frame.shape[1]
                frameHeight = frame.shape[0]
                #print(f'resolution2 :{frameWidth} x {frameHeight}')
                #paint the camera center
                x1 = int(camcenter[0] - alignment_window)
                y1 = int(camcenter[1] - alignment_window)
                x2 = int(camcenter[0] + alignment_window)
                y2 = int(camcenter[1] + alignment_window)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), int(round(frameHeight / 150)), 8,)
                
                deltax=deltay=0
                numfaces = len(bboxes)

                #checks for verification nybble is done moving
                #we do this check each loop so the rest the code can keep running
                if nfp.read_serial_check('[im]',s):
                    moved_await_reply-=1
                    print(f"moved await reply {moved_await_reply}")
                    if moved_await_reply < 0:
                        moved_await_reply = 0

                if numfaces>0:
                    facebox = bboxes[0]
                    facexcenter = facebox[0] + (facebox[2] - facebox[0])/2
                    faceycenter = facebox[1] + (facebox[3] - facebox[1])/2

                    #-1's because camera is rotated
                    deltax = -1 * (facexcenter - camcenter[0]) 
                    deltay = (faceycenter - camcenter[1])

                    #paint the face center
                    x1 = int(facexcenter - alignment_window)
                    y1 = int(faceycenter - alignment_window)
                    x2 = int(facexcenter + alignment_window)
                    y2 = int(faceycenter + alignment_window)
                    
                    #region of interest for our blur
                    '''
                    roi = frame[facebox[1]:facebox[3], facebox[0]:facebox[2]] 
                    #print(f"roi is at ({facebox[1]}:{facebox[3]}) ({facebox[0]}:{facebox[2]})")
                    roi = cv2.GaussianBlur(roi, (23,23), 30)
                    frame[facebox[1]:facebox[3], facebox[0]:facebox[2]]  = roi
                    '''

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), int(round(frameHeight / 150)), 8,)

                if numfaces>0 and (timenow - last_movement_time) > move_delay and moved_await_reply==0:
                    last_movement_time=timenow
                    print(f"face is at ({facexcenter}, {faceycenter}).  camcenter is ({camcenter[0]}, {camcenter[1]}).  (In Pixels) Move X: {deltax}, Move Y:{deltay}")

                    if abs(deltax) > alignment_window or abs(deltay) > alignment_window:
                        xdeg = deltax * degrees_per_pixel
                        ydeg = deltay * degrees_per_pixel

                        tomovex = m0offset + int(xdeg)
                        if(tomovex > m0max):
                            tomovex=m0max
                        elif(tomovex < (-1 * m0max)):
                            tomovex = -1 * m0max

                        #minus because up is negative for this servo
                        tomovey = m1offset - int(ydeg)
                        if(tomovey > m1max):
                            tomovey=m1max
                        elif(tomovey < m1min):
                            tomovey = m1min

                        print(f"moving {xdeg}, {ydeg} which means joint m0(x) moves to {m0offset} + {xdeg} = {tomovex} and m1(y) moves to {m1offset} - {ydeg} = {tomovey}")
                        nfp.write_serial(f"i 0 {tomovex} 1 {tomovey}",s)
                        #nfp.read_serial_until('i',s)
                        m1offset = tomovey
                        m0offset = tomovex
                        moved_await_reply+=1
                        
            if record_video:
                out.write(frame)
            cv2.imshow('Face', frame)

            nfp.clear_in_waiting(s)

            key = cv2.waitKey(1) & 0xFF    

            if key == ord("d"):
                detectionEnabled = not detectionEnabled
            elif key == 178: #numpad 2
                m1offset = m1offset-1
                if(m1offset > m1max):
                    m1offset=m1max
                elif(m1offset < m1min):
                    m1offset = m1min

                print(m0offset)
                nfp.write_serial(f"m1 {m1offset}",s)
                nfp.read_serial_until('m',s)
                time.sleep(1)

            elif key == 184: #numpad 8
                m1offset = m1offset+1
                if(m1offset > m1max):
                    m1offset=m1max
                elif(m1offset < m1min):
                    m1offset = m1min

                print(m0offset)
                nfp.write_serial(f"m1 {m1offset}",s)
                nfp.read_serial_until('m',s)
                time.sleep(1)

            elif key == 180: #numpad 4
                #spin left
                nfp.write_serial("kvtL",s)
            elif key == 182: #numpad 6
                #spin right
                nfp.write_serial("kvtR",s)

            elif key == ord('-'):
                move_delay=move_delay-.05
                if(move_delay<0):
                    move_delay=.01
                print(f'move delay {move_delay}')

            elif key == ord('n'):
                idx = int(input("Select resolution index: "))
                nfp.set_resolution(URL, index=idx, verbose=True)

            elif key == ord('t'):
                val = float(input("Set face detection threshold (.01 - 1): "))
                face_threshold=val
            elif key == ord('+'):
                move_delay=move_delay+.05
                if(move_delay>5):
                    move_delay=5
                print(f'move delay {move_delay}')
            elif key == ord('-'):
                move_delay=move_delay-.05
                if(move_delay<0):
                    move_delay=.01
                print(f'move delay {move_delay}')
            elif key == 181: #numpad 5
                #nfp.write_serial("m0 0",s)
                #nfp.read_serial_until('m',s)

                #nfp.write_serial("m1 0",s)
                #nfp.read_serial_until('m',s)

                nfp.write_serial(sit,s)
                nfp.read_serial_until("i",s)
                m0offset = 0
                m1offset = 0
                #nfp.write_serial("kbalance",s)
            elif key == ord('u'):
                val = int(input("Set quality (10 - 63): "))
                nfp.set_quality(URL, value=val)

            elif key == ord('a'):
                AWB = nfp.set_awb(URL, AWB)
            elif key == ord("q"):
                break
    except Exception as e:
        print(f'exc: {e}')
        pass

cap.release()
if record_video:
    out.release()
cv2.destroyAllWindows()
s.close()