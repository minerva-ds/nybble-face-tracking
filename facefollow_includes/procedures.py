import time 
import requests 
import re

def write_serial(data,s):
    print(data)
    data_encoded = data.encode('utf-8')
    s.write(data_encoded)

def clear_in_waiting(s):
    while s.in_waiting:
        #gets rid of empty lines and other noise so the next time we use this function it gives us the result we want
        data = s.readline()
        print(data)
    
'''
def read_serial_line_reply():
    sreply = s.readline()
    sreply = sreply.decode("ISO-8859-1")
    x = threading.Thread(target=clear_in_waiting,daemon=True)
    x.start()
    print(sreply)

    return sreply
''' 
def read_serial_until(str,s):
    buffer = ""
    while True:
        try: 
            size = s.inWaiting()
            if size:
                data = s.read(size)
                datatext = data.decode('ISO-8859-1')
                print (datatext)
                buffer+=datatext
                if str in datatext:
                    return buffer
            time.sleep(0.01)

        except Exception as e:
            print("error")
            print(e)

def read_serial_check(regex,s):
    buffer = ""
    try: 
        p = re.compile(regex)
        size = s.inWaiting()
        if size:
            data = s.read(size)
            datatext = data.decode('ISO-8859-1')
            print (datatext)
            buffer+=datatext
            if p.match(datatext):
                return True
        return False

    except Exception as e:
        print("error")
        print(e)
    
def detectFaceOpenCVDnn(net, frame, cv2, conf_threshold=0.7):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False,)

    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    first = True
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            if first:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8,)
                first=False
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), int(round(frameHeight / 150)), 8,)
            
            top=x1
            right=y1
            bottom=x2-x1
            left=y2-y1

            face = frame[right:right+left, top:top+bottom]
            frame[right:right+face.shape[0], top:top+face.shape[1]] = face

    return frame, bboxes

def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")

def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb