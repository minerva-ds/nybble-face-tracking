
connwifi = False
wait_for_serial_ready = True


'''Camera Pixels Per Degree'''
#resolution = [640,480]
resolution = [320,240]
camcenter = [int(resolution[0]/2),int(resolution[1]/2)]
viewangle = 90
diagnolpixels = math.sqrt(resolution[0]^2 + resolution[1]^2)
degrees_per_pixel = diagnolpixels/viewangle
print(degrees_per_pixel)

'''Setup Serial over Bluetooth'''
baudrate = 115200
port = '/dev/rfcomm0'  # set the correct port before run it

s = serial.Serial(port=port, baudrate=baudrate,timeout=2)
if s.is_open:
    print("Serial Port Open!")
else:
    print("Could not open serial port")
    sys.exit()


m0offset = 0
#m0 positive = turn left and rotate clockwise
#m0 negative = turn right and rotate counterclockwise
m0max = 50

m1offset = 0
#m1 positive = look up
#m1 negative = look down 
m1max = 35 

'''Setup Stream over WiFi'''
dir_path = os.path.dirname(os.path.realpath(__file__))

# load face detection model
# download model and prototxt from https://github.com/spmallick/learnopencv/tree/master/FaceDetectionComparison/models
modelFile = dir_path+"/models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
configFile = dir_path+"/models/deploy.prototxt"

net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
detectionEnabled = False