#!/usr/bin/env python

import time

try:
    import RPi.GPIO as GPIO
except RunTimeError as err:
    print err
    print ("Error: Can't import RPi.GPIO")
    
def read_raw(constants):
    
    a = 0
    dataPin0 = 0
    dataPin1 = 0
    
    GPIO.output(constants['CHIP_SELECT_PIN'],GPIO.HIGH)
    time.sleep(constants['TICK'])
    GPIO.output(constants['CLOCK_PIN'],GPIO.LOW)
    time.sleep(constants['TICK'])
    GPIO.output(constants['CHIP_SELECT_PIN'],GPIO.LOW)
    time.sleep(constants['TICK'])
    
    while a < (constants['READING_BIT_LENGTH'] + constants['READING_LOW_0_BIT']):
        GPIO.output(constants['CHIP_SELECT_PIN'], GPIO.HIGH)
        time.sleep(constants['TICK'])
        GPIO.output(constants['CLOCK_PIN'],GPIO.HIGH)
        time.sleep(constants['TICK'])
        
        readbit[0] = GPIO.input(constants['DATA_PIN_0'])
        readbit[1] = GPIO.input(constants['DATA_PIN_1'])
        
        packets[0] = ((packets[0] << 1) + readbit[0])
        packets[1] = ((packets[1] << 1) + readbit[1])
        
        a += 1
        
    return ((packets[1] << 16) | packets[0])
    
def bit_slicer(start, lowBit, count):
    range = 1 << count
    mask = range - 1
    return (start >> lowBit) & mask

def handle_rollovers(readings[2], constants):
    prevReadings = 0
    prevRollovers = 0
    
    range = 1 << constants['READING_BIT_LENGTH']
    big_jump = range / 2
    for(i=0;i<2;i++):
        change = readings[i] - prevReadings[i]
        prevReadings[i] = readings[i]
        prevRollovers[i] += (change > big_jump) ? -1 : (change < -big_jump)
        values[i] = readings[i] + range * prevRollovers[i]
    return values

def init_pins(constants):
    
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(constants['DATA_PIN_0'], GPIO.IN)
    GPIO.setup(constants['DATA_PIN_1'], GPIO.IN)
    GPIO.setup(constants['CHIP_SELECT_PIN'], GPIO.OUT)
    GPIO.setup(constants['CLOCK_PIN'], GPIO.OUT)
    
def main(is_first):

    constants = {
        'DATA_PIN_0' : 4,
        'DATA_PIN_1' : 8,
        'CHIP_SELECT_PIN' : 24,
        'CLOCK_PIN' : 23,
        'TICK' : 0.01,
        'READING_LOW_0_BIT' : 6,
        'READING_LOW_1_BIT' : 22,
        'READING_BIT_LENGTH' : 10,
        'ROLLOVER_RANGE' : 1024
    }

    # DATA_PIN_0 = 4
    # DATA_PIN_1 = 8
    # CHIP_SELECT_PIN = 24
    # CLOCK_PIN = 23
    # TICK = 0.01
    # READING_LOW_0_BIT = 6
    # READING_LOW_1_BIT = 22
    # READING_BIT_LENGTH = 10
    # ROLLOVER_RANGE = 1024
    
    init_pins(constants)
    crashed = False
    checkValue = 0
    values = 0
    
    while not crashed:
        data = read_raw(constants)
        
        readings[0] = bit_slicer(data,constants['READING_LOW_0_BIT'],constants['READING_BIT_LENGTH'])
        readings[1] = bit_slicer(data,constants['READING_LOW_1_BIT'],constants['READING_BIT_LENGTH'])
        
        values = handle_rollovers(readings)
        
        if (is_first == 0):
            init_reading_0 = values[0]
            init_reading_1 = values[1]
            is_first = 1
        else:
            values[0] = values[0] - checkValue[0]
            values[1] = values[1] - checkValue[1]
        # differingValue[0] = values[0] - checkValue[0]
        # differingValue[1] = values[1] - checkValue[1]
        
        checkValue[0] = values[0]
        checkValue[1] = values[1]
        
is_first = 0
main(is_first)