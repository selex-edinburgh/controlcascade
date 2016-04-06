#ifndef _PIGPIO_H
#define _PIGPIO_H

#include <stdio.h>
#include <stdint.h>
#include <pigpio.h>
#include <math.h>

#define DATA_PIN_1 22
#define DATA_PIN_2 21
#define CHIP_SELECT_PIN 17
#define CLOCK_PIN 18
#define PIN_HIGH 1
#define PIN_LOW 0
#define TICK 0.00001
#define READING_LOW_BIT 7
#define READING_BIT_LENGTH 10
#define ROLLOVER_RANGE 1024

#endif
