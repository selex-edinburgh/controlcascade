#include "pigpio.h"

unsigned get_binary(unsigned k)
{
	if (k == 0) return 0;
	if (k == 1) return 1;
	return (k % 2) + 10 * get_binary(k / 2);
}

int write_raw_val(packet)
{
	if (gpioRead(CHIP_SELECT_PIN) == 1)
	{
		int a = 0;
		while (a < 34)
		{
			gpioSetISRFunc(CLOCK_PIN, RISING_EDGE,-1,);
			a += 1;
		}
	}
}

int main(int argc, char *argv[])
{
        int data0 = 204;
	int data1 = 178;
	uint16_t packet0;
	uint16_t packet1;
	uint32_t packet;

        gpioInitialise();

        gpioSetMode(CHIP_SELECT_PIN, PI_INPUT);
        gpioSetMode(DATA_PIN, PI_OUTPUT);
        gpioSetMode(CLOCK_PIN, PI_INPUT);

        while (1)
        {
		packet0 = get_binary(data0);
		packet1 = get_binary(~data1);

		packet = ((uint32_t)packet0 << 17) | packet1;
		write_raw_val(packet);
		printf("output %x\n", packet);
///                printf("read: %d \n",  rawval);
  //              printf("raw rotation left: %d \n", (left));
    //            printf("raw rotation right: %d \n", (right));
      //          printf("pulseL: %d \n",(total_pulseL));
        //        printf("pulseR: %d \n",(total_pulseR));
                time_sleep(1);
        };
}

