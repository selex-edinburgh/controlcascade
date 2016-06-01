#include "pigpio.h"

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

int get_decimal(int binary_number)
{
	long int decimal_number = 0;
	int j = 1;
	int remainder;

	while (binary_number != 0)
	{
		remainder = binary_number % 10;
		decimal_number = decimal_number + remainder * j;
		j = j * 2;
		binary_number = binary_number/10;
	}
	return decimal_number;
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
	while (a < 34)
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
	uint32_t rawdata;
	uint16_t packet0;
	uint16_t packet1;
	int data0;
	int data1;
	int rollover_count = 0;
	int total_pulse = 0;
	int prev_pulse;
	int total_pulseL;
	int total_pulseR;
	int prev_pulseL;
	int prev_pulseR;

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

		rawdata = read_raw_val();

		packet0 = ((rawdata >> 17) & 0x0000ffff) >> 7;
		packet1 = ((rawdata & 0x0000ffff) >> 7);

		data0 = get_decimal(packet0);
		data1 = get_decimal(packet1);

		total_pulseL = check_rollover(rollover_count, total_pulseL, prev_pulseL, data0);
		total_pulseR = check_rollover(rollover_count, total_pulseR, prev_pulseR, data1);

//-----------------------------------READY TO SEND TO PIPE FOR PYTHON--------------------------------------

		printf("read: %d \n",  rawdata);
		printf("raw rotation left: %d \n", (data0));
		printf("raw rotation right: %d \n", ~(data1));
		printf("pulseL: %d \n",(total_pulseL));
		printf("pulseR: %d \n",(total_pulseR));
		time_sleep(1);
	};
}
