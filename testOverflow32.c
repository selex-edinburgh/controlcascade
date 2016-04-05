#include <stdio.h>
#include <stdint.h>
#include <pigpio.h>
#include <math.h>

#define DATA_PIN 22
#define CHIP_SELECT_PIN 17
#define CLOCK_PIN 18
#define PIN_HIGH 1
#define PIN_LOW 0
#define TICK 0.00001
#define ROLLOVER_RANGE 1024

int bit_reverse(reading)
{
	const uint16_t mask0 = 0x5555;
	const uint16_t mask1 = 0x3333;
	const uint16_t mask2 = 0x0F0F;
	const uint16_t mask3 = 0x00FF;

	reading = (((~mask0) & reading) >> 1) | ((mask0 & reading) << 1);
	reading = (((~mask1) & reading) >> 2) | ((mask1 & reading) << 2);
	reading = (((~mask2) & reading) >> 4) | ((mask2 & reading) << 4);
	reading = (((~mask3) & reading) >> 8) | ((mask3 & reading) << 8);

	return reading;
}

int check_rollover(rollover_count, total_pulse, prev_pulse, reading)
{
	total_pulse = reading + rollover_count * ROLLOVER_RANGE;
	if (abs(total_pulse - prev_pulse) > ROLLOVER_RANGE * 0.95)
	{
		int sign = copysign(1, total_pulse - prev_pulse);
		rollover_count = rollover_count - sign;
		total_pulse = reading + rollover_count * ROLLOVER_RANGE;
	};
	return total_pulse;
}

int read_raw_val()
{
	int a = 0;
	int output = 0;
	int readbit = 0;

	gpioWrite(CHIP_SELECT_PIN, PIN_HIGH);
	time_sleep(TICK);
	gpioWrite(CLOCK_PIN, PIN_HIGH);
	time_sleep(TICK);
	gpioWrite(CHIP_SELECT_PIN, PIN_LOW);
	time_sleep(TICK);
	gpioWrite(CLOCK_PIN, PIN_LOW);
	time_sleep(TICK);
	while (a < 32)
	{
		gpioWrite(CLOCK_PIN, PIN_HIGH);
		time_sleep(TICK);
		readbit = gpioRead(DATA_PIN);
		output = (output <<1) + readbit;
		gpioWrite(CLOCK_PIN, PIN_LOW);
		time_sleep(TICK);
		a += 1;
	};
	return output;
}
int main(int argc, char *argv[])
{
	uint32_t rawval;
	uint16_t left;
	uint16_t right;
	int rollover_count = 0;
	int total_pulse = 0;
	int prev_pulse;
	int total_pulseL;
	int total_pulseR;
	int prev_pulseL;
	int prev_pulseR;
	double start = time_time();

	if (gpioInitialise() < 0)
   	{
      		fprintf(stderr, "pigpio initialisation failed\n");
      		return 1;
   	};

	gpioSetMode(CHIP_SELECT_PIN, PI_OUTPUT);
   	gpioSetMode(DATA_PIN, PI_INPUT);
	gpioSetMode(CLOCK_PIN, PI_OUTPUT);

	while (1)
	{
		prev_pulseL = total_pulseL;
		prev_pulseR = total_pulseR;
		rawval = read_raw_val();
		left = (rawval >> 16) & 0x0000ffff;
		total_pulseL = check_rollover(rollover_count, total_pulseL, prev_pulseL, left);
		right = rawval & 0x0000ffff;
		bit_reverse(right);
		total_pulseR = check_rollover(rollover_count, total_pulseR, prev_pulseR, right);
		printf("read: %d \n",  rawval);
		printf("raw rotation left: %d \n", (left));
		printf("raw rotation right: %d \n", (right));
		printf("pulseL: %d \n",(total_pulseL));
		printf("pulseR: %d \n",(total_pulseR));
		time_sleep(1);
	};
}
