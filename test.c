#include <stdio.h>

#include <pigpio.h>


int read_raw_val() {
	int data = 23;
	int chip_select = 4;
	int clock = 17;
	double tick = 0.0001;
	int a = 0;
	int output = 0;
	int readbit = 0;

	gpioWrite(4, 1);
	time_sleep(tick);
	gpioWrite(17, 1);
	time_sleep(tick);
	gpioWrite(4, 0);
	time_sleep(tick);
	gpioWrite(17, 0);
	time_sleep(tick);
	while (a < 16) {
		gpioWrite(17, 1);
		time_sleep(tick);
		readbit = gpioRead(23);
		output = (output << 1) + readbit;
		gpioWrite(17, 0);
		time_sleep(tick);
		a += 1;
	};
	return output;
}
int main(int argc, char *argv[])
{
   	int rawval = 0;
	double start = time_time();
	if (gpioInitialise()<0) exit(1);

	gpioSetMode(17, PI_OUTPUT);
   	gpioSetMode(23, PI_INPUT);
	gpioSetMode(4, PI_OUTPUT);

	while (1) {
		rawval = read_raw_val();
		//printf("read: %d \n",  rawval);
		//printf("raw rotation: %d \n", (rawval >> 6));
		time_sleep(0.005);
	};
}
