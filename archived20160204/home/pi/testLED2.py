import time, signal

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error: importing RPi.GPIO")

GPIO.setmode(GPIO.BCM)

GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

GPIO.setwarnings(False)

try:
    while True:
      
        GPIO.output(24, True)
        GPIO.output(25, False)
        print "LED on"
        time.sleep(1)
          
        GPIO.output(24, False)
        GPIO.output(25, True)
        print "LED off"  
        time.sleep(1)

except KeyboardInterrupt:
    print("KeyboardInterrupt Detected! Will clean the channel and exit")
    GPIO.cleanup(7)

