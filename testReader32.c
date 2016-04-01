#include <stdio.h>
#include <stdint.h>
#include <pigpio.h>

#define DATA_PIN 22
#define CHIP_SELECT_PIN 17
#define CLOCK_PIN 18
#define PIN_HIGH 1
#define PIN_LOW 0

int read_raw_val() {
	double tick = 0.01;
	int a = 0;
	int output = 0;
	int readbit = 0;

	gpioWrite(CHIP_SELECT_PIN, PIN_HIGH);
	time_sleep(tick);
	gpioWrite(CLOCK_PIN, PIN_HIGH);
	time_sleep(tick);
	gpioWrite(CHIP_SELECT_PIN, PIN_LOW);
	time_sleep(tick);
	gpioWrite(CLOCK_PIN, PIN_LOW);
	time_sleep(tick);
	while (a < 32) {
		gpioWrite(CLOCK_PIN, PIN_HIGH);
		time_sleep(tick);
		readbit = gpioRead(DATA_PIN);
		output = (output <<1) + readbit;
		gpioWrite(CLOCK_PIN, PIN_LOW);
		time_sleep(tick);
		a += 1;
	};
	return output;
}
int main(int argc, char *argv[])
{
	uint32_t rawval;
	int left;
	int right;
	double start = time_time();

	if (gpioInitialise() < 0)
   	{
      		fprintf(stderr, "pigpio initialisation failed\n");
      		return 1;
   	}
	gpioSetMode(CHIP_SELECT_PIN, PI_OUTPUT);
   	gpioSetMode(DATA_PIN, PI_INPUT);
	gpioSetMode(CLOCK_PIN, PI_OUTPUT);

	while (1) {
		rawval = read_raw_val();
		left = (rawval >> 16) & 0x0000ffff;
		right = rawval & 0x0000ffff;
		printf("read: %d \n",  rawval);
		printf("raw rotation left: %d \n", (left >> 6));
		printf("raw rotation right: %d \n", (right >> 6));
		time_sleep(1);
	};
}
