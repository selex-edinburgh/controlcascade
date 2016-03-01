import time, signal

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error: importing RPi.SPIO")

GPIO.setmode(GPIO.BCM)

GPIO.setup(7, GPIO.OUT)

GPIO.setwarnings(False)

try:
    while True:

        GPIO.output(7, True)
        print "LED on"

        time.sleep(1)

        GPIO.output(7, False)
        print "LED off"
        time.sleep(1)

except KeyboardInterrupt:

    print("KeyboardInterrupt: Will clean up and exit")
    GPIO.cleanup(7)

       
