#include <stdio.h>
#include "pigpio.h"

int bitSlice ( uint64_t from, int lowBit, int count) {
	int range = 1 << count;
	uint64_t mask = range - 1;
	return (from >> lowBit) & mask;
}

int* read_raw_val() {
	int a = 0;
	int packets[2];
	int readbit0;
	int readbit1;
	static int data[2];

	gpioWrite(CHIP_SELECT_PIN_1, PIN_HIGH);
	gpioWrite(CHIP_SELECT_PIN_2, PIN_HIGH);
	time_sleep(TICK);
	gpioWrite(CLOCK_PIN_1, PIN_HIGH);
	gpioWrite(CLOCK_PIN_2, PIN_HIGH);
	time_sleep(TICK);
	gpioWrite(CHIP_SELECT_PIN_1, PIN_LOW);
	gpioWrite(CHIP_SELECT_PIN_2, PIN_LOW);
	time_sleep(TICK);
	gpioWrite(CLOCK_PIN_1, PIN_LOW);
	gpioWrite(CLOCK_PIN_2, PIN_LOW);
	time_sleep(TICK);
	while (a < (READING_BIT_LENGTH + READING_LOW_BIT)) {
		gpioWrite(CLOCK_PIN_1, PIN_HIGH);
		gpioWrite(CLOCK_PIN_2, PIN_HIGH);
		time_sleep(TICK);

		readbit0 = gpioRead(DATA_PIN_1);
		readbit1 = gpioRead(DATA_PIN_2);

		packets[0] = ((packets[0] << 1) + readbit0);
		packets[1] = ((packets[1] << 1) + readbit1);

		gpioWrite(CLOCK_PIN_1, PIN_LOW);
		gpioWrite(CLOCK_PIN_2, PIN_LOW);
		time_sleep(TICK);
		a += 1;
	};
	data[0] = bitSlice(packets[0],READING_LOW_BIT,READING_BIT_LENGTH);
	data[1] = bitSlice(packets[1],READING_LOW_BIT,READING_BIT_LENGTH);

	return data;
}

int main(int argc, char *argv[])
{
	double start = time_time();

	if (gpioInitialise() < 0)
   	{
      		fprintf(stderr, "pigpio initialisation failed\n");
      		return 1;
   	}
	gpioSetMode(CHIP_SELECT_PIN_1, PI_OUTPUT);
	gpioSetMode(CHIP_SELECT_PIN_2, PI_OUTPUT);
   	gpioSetMode(DATA_PIN_1, PI_INPUT);
   	gpioSetMode(DATA_PIN_2, PI_INPUT);
	gpioSetMode(CLOCK_PIN_1, PI_OUTPUT);
	gpioSetMode(CLOCK_PIN_2, PI_OUTPUT);

	while (1) {
		int* data = read_raw_val();
		int idx;
		for ( idx = 0; idx < 2; idx ++) {
			printf ( "value %d %d :: ", idx, data[idx]);
		}
		printf ("\n");
		time_sleep(1);
	};
}
