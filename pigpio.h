#ifndef _PIGPIO_H
#define _PIGPIO_H

#include <stdio.h>
#include <sys/stat.h>
#include <inttypes.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <pigpio.h>
#include <math.h>
#include <time.h>

//GPIO pin setup
#define DATA_PIN_1  4
#define DATA_PIN_2 18
#define CHIP_SELECT_PIN_1 24
#define CLOCK_PIN_1 23

//DO NOT CHANGE BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
#define PIN_HIGH 1
#define PIN_LOW 0
//#define TICK 0.00001
#define TICK 1
#define READING_LOW_0_BIT 6
#define READING_LOW_1_BIT 22
#define READING_BIT_LENGTH 10
#define ROLLOVER_RANGE 1024

#endif
