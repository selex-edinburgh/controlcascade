import serial, time, threading

### ControlBoard represents the main control board and allows you to digitally 
### control what normally would be controlled via the radio remote.
### When using the methods, keep in mind that 'speed' is actually a number 
### between 2 and 253 (safe limits), with 127 being the centre point at which there is 
### no movement. A value lower than this produces movement in a backward 
### direction. A value higher than this produces forward motion.
class ControlBoard:

    ### When a ControlBoard object is created ( ControlBoard() ),  
    ### tranmission is started immediately.
    def __init__(self):
        self.connect = False
        try:
            self.port = serial.Serial("/dev/ttyAMA0",baudrate=9600,stopbits=1, parity='N', bytesize=8,timeout=1)
            self.port.open()
            self.connect = True
        except:
            print "WARNING: No control board attached!"

        self.ver = 127
        self.hor = 127
        self.MAX = 253
        self.CEN = 127
        self.MIN = 2
        self.DEFAULTSLEEP = 0.05
        self.stime = time.time()
        self.sleeptime = self.DEFAULTSLEEP
        self.run = True

        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    ### Ease the chariot into forward motion.
    ### speed -> The speed to accelerate to. (int)
    def forward(self, speed):
        if speed > self.MAX or speed < self.CEN: return
        while self.ver < speed:
            self.ver+=1
            time.sleep(self.sleeptime)

    ### Ease the chariot into backward motion.
    ### speed -> The speed to accelerate to. (int)
    def reverse(self, speed):
        if speed < self.MIN or speed > self.CEN: return
        while self.ver > speed:
            self.ver-=1
            time.sleep(self.sleeptime)

    ### Ease the chariot into a right/clockwise turn.
    ### rspeed -> the final speed to turn with. (int)
    def right(self, rspeed):
        if rspeed > self.MAX or rspeed < self.CEN: return
        while self.hor < rspeed:
            self.hor+=1
            time.sleep(self.sleeptime)

    ### Ease the chariot into a left/anticlockwise turn.
    ### rspeed -> the final speed to turn with. (int)
    def left(self, rspeed):
        if rspeed < self.MIN or rspeed > self.CEN: return
        while self.hor > rspeed:
            self.hor-=1
            time.sleep(self.sleeptime)

    ### Ease the rotation of the chariot to a full stop.
    def center(self):
        while self.hor > self.CEN:
            hor-=1
            time.sleep(0.1)
        while self.hor < self.CEN:
            self.hor+=1
            time.sleep(self.sleeptime)


    ### Ease the motion of the chariot to a full stop. 
    def stop(self):
        while self.ver > self.CEN:
            self.ver-=1
            time.sleep(0.1)
        while self.ver < self.CEN:
            self.ver+=1
            time.sleep(self.sleeptime)

    ### Send command bytes to the control board.
    def transmit(self):
        self.port.write(chr(self.ver))
        self.port.write(chr(self.hor))

    ### The loop that transmits the signals with appropriate timing.
    def loop(self):
        if self.connect:
            while self.run == True:
                self.transmit()
                time.sleep(0.010)

    ### Signals for the transmitting loop to exit.
    def shutdown(self):
        self.run = False
        self.thread.join()
