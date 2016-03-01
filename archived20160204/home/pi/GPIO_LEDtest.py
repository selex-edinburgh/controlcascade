import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.OUT)

while True:
  GPIO.output(7, True)
  time.sleep(1)
  GPIO.output(7, False)
  time.sleep(1)

