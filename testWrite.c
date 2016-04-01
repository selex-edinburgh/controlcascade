#include <stdio.h>

#include <pigpio.h>


int read_raw_val() {
	int data = 22;
	int chip_select = 17;
	int clock = 18;
	int pin_high = 1;
	int pin_low = 0;
	double tick = 0.0001;
	int a = 0;
	int output = 0;
	int readbit = 0;

	gpioWrite(chip_select, pin_high);
	time_sleep(tick);
	gpioWrite(clock, pin_high);
	time_sleep(tick);
	gpioWrite(chip_select, pin_low);
	time_sleep(tick);
	gpioWrite(clock, pin_low);
	time_sleep(tick);
	while (a < 16) {
		gpioWrite(clock, 1);
		time_sleep(0.01);
		readbit = gpioRead(data);
		output = (output << 1) + readbit;
		gpioWrite(clock, 0);
		time_sleep(0.01);
		a += 1;
	};
	return output;
}
int main(int argc, char *argv[])
{
	int data = 22;
   	int chip_select = 17;
	int clock = 18;
	int rawval = 0;
	double start = time_time();

	if (gpioInitialise() < 0)
   	{
      		fprintf(stderr, "pigpio initialisation failed\n");
      		return 1;
   	}
	gpioSetMode(chip_select, PI_OUTPUT);
   	gpioSetMode(data, PI_INPUT);
	gpioSetMode(clock, PI_OUTPUT);

	while (1) {
		rawval = read_raw_val();
		printf("read: %d \n",  rawval);
		printf("raw rotation: %d \n", (rawval >> 6));
		time_sleep(1);
	};
}
