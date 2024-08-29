'''
elif key == 180: #numpad 4
    m0offset = m0offset-1
    if(m0offset > m0max):
        m0offset=m0max
    elif(m0offset < (-1 * m0max)):
        m0offset = -1 * m0max

    print(m1offset)
    nfp.write_serial(f"m0 {m0offset}",s)
    nfp.read_serial_until('m',s)
    time.sleep(1)

elif key == 182: #numpad 6
    m0offset = m0offset+1
    if(m0offset > m0max):
        m0offset=m0max
    elif(m0offset < (-1 * m0max)):
        m0offset = -1 * m0max
        
    print(m1offset)

    nfp.write_serial(f"m0 {m0offset}",s)
    nfp.read_serial_until('m',s)
    time.sleep(1)
'''
'''
elif key == ord('j'):
    nfp.write_serial("m0 0",s)
    m0offset = 0
    nfp.read_serial_until('m',s)
    time.sleep(1)

    deltax = -resolution[0]/2
    xdeg = deltax * degrees_per_pixel
    tomovex = 0 + int(xdeg)
    print(f"simulate moving to {deltax}px on screen is {tomovex} degrees")

    nfp.write_serial(f"m0 {tomovex}",s)
    m0offset = tomovex 
    nfp.read_serial_until('m',s)
    time.sleep(1)

elif key == ord('k'):
    nfp.write_serial("m1 0",s)
    m1offset = 0
    nfp.read_serial_until('m',s)
    time.sleep(1)

    deltay = -resolution[1]/2
    ydeg = deltay * degrees_per_pixel
    tomovey = 0 + int(ydeg)
    print(f"simulate moving to {deltay}px on screen is {tomovey} degrees")

    nfp.write_serial(f"m1 {tomovey}",s)
    m1offset = tomovey 
    nfp.read_serial_until('m',s)
    time.sleep(1)
''' 
'''
if (m0offset!=0 or m1offset!=0) and len(bboxes)==0 and timenow - last_movement_time > reset_time:
    nfp.write_serial("m0 0",s)
    m0offset = 0
    nfp.read_serial_until('m',s)

    nfp.write_serial("m1 0",s)
    m1offset = 0
    nfp.read_serial_until('m',s)
'''


'''
data = f'm0 {tomovex}'
nfp.write_serial(data,s)
#nfp.read_serial_until('m',s)
m0offset = tomovex

data = f'm1 {tomovey}'
nfp.write_serial(data,s)
moved_await_reply+=1
m1offset = tomovey
'''

'''
nfp.write_serial("m0 0",s)
nfp.read_serial_until("m",s)
nfp.write_serial("m1 0",s)
nfp.read_serial_until("m",s)
'''
#nfp.write_serial("ksit",s)
#nfp.read_serial_until("m",s)
#m15 back left leg + is up - is down
#m13 front right leg + is down - is up
#m14 back right leg + is up - is down
#m12 front left leg + is down - is up
#move left while sitting
'''
i 12 80 14 30
i 12 62 14 47 
'''
#sit = "c 0 0 1 -20 2 58 8 32 9 32 10 -80 11 -70 12 62 13 62 14 47 15 30"
'''
turn m9+ and 
'''
