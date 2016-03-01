import serial, time, threading

port = serial.Serial("/dev/ttyAMA0",baudrate=9600,stopbits=1, parity='N', bytesize=8,timeout=100)
port.open()

ver = 127
hor = 127
MAX = 254
CEN = 127
MIN = 2
stime = time.time()
runtime = 300
stepsize = 5
sleeptime = 0.05

### Ease the chariot into forward motion.
### speed: The speed to accelerate to.
def forward(speed):
    global ver, MAX, CEN
    if speed > MAX or speed < CEN: return
    while ver < speed:
        ver+=1
        time.sleep(sleeptime)

### Ease the chariot into backward motion.
### speed: The speed to accelerate to.
def reverse(speed):
    global ver, MIN, CEN
    if speed < MIN or speed > CEN: return
    while ver > speed:
        ver-=1
        time.sleep(sleeptime)

### Ease the chariot into a right/clockwise turn.
### rspeed: the final speed to turn with.
def right(rspeed):
    global hor, MAX, CEN
    if rspeed > MAX or rspeed < CEN: return
    while hor < rspeed:
        hor+=1
        time.sleep(sleeptime)

### Ease the chariot into a left/anticlockwise turn.
### rspeed; the final speed to turn with.
def left(rspeed):
    global hor, MIN, CEN
    if rspeed < MIN or rspeed > CEN: return
    while hor > rspeed:
        hor-=1
        time.sleep(sleeptime)

### Ease the rotation of the chariot to a full stop.
def center():
    global hor, CEN
    while hor > CEN:
        hor-=1
        time.sleep(sleeptime)
    while hor < CEN:
        hor+=1
        time.sleep(sleeptime)


### Ease the motion of the chariot to a full stop. 
def stop():
    global ver, CEN
    while ver > CEN:
        ver-=1
        time.sleep(sleeptime)
    while ver < CEN:
        ver+=1
        time.sleep(sleeptime)

### Send command bytes to the control board.
def transmit():
    global port, ver, hor
    port.write(chr(ver))
    port.write(chr(hor))


def loop():
    global ver, hor, stime, runtime
    while time.time() - stime < runtime:
        transmit()
        time.sleep(0.016)
        #print("{},{}".format(ord(port.read()),ord(port.read())))
        print("{},{}".format(ver, hor))

t = threading.Thread(target=loop)
t.daemon = True
t.start() 

forward(254)
time.sleep(5)
stop()
time.sleep(5)
reverse(2)
time.sleep(5)
stop()
time.sleep(5)
left(2)
time.sleep(5)
center()
time.sleep(5)
right(254)
time.sleep(5)
center()
time.sleep(10)

