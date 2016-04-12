#include "pigpio.h"

int reverse = 1;

struct timeval {
	int tv_sec;
	int tv_usec;

};

int read_raw() {
        int a = 0;
	int readbit[2];
	int packets[2];
        static int data0;
	static int data1;
        uint16_t mask = (1 << READING_BIT_LENGTH) - 1;
        gpioWrite(CHIP_SELECT_PIN_1, PIN_HIGH);
        gpioWrite(CHIP_SELECT_PIN_2, PIN_HIGH);
	gpioDelay(TICK);
        gpioWrite(CLOCK_PIN_1, PIN_HIGH);
        gpioWrite(CLOCK_PIN_2, PIN_HIGH);
	gpioDelay(TICK);
        gpioWrite(CHIP_SELECT_PIN_1, PIN_LOW);
        gpioWrite(CHIP_SELECT_PIN_2, PIN_LOW);
	gpioDelay(TICK);
        gpioWrite(CLOCK_PIN_1, PIN_LOW);
        gpioWrite(CLOCK_PIN_2, PIN_LOW);
	gpioDelay(TICK);
	while (a < (READING_BIT_LENGTH + READING_LOW_0_BIT)) {
		gpioWrite(CLOCK_PIN_1, PIN_HIGH);
                gpioWrite(CLOCK_PIN_2, PIN_HIGH);
                gpioDelay(TICK);

//                readbit[0] = gpioRead(DATA_PIN_1);
//                readbit[1] = gpioRead(DATA_PIN_2);

//                packets[0] = ((packets[0] << 1) + readbit[0]);
//                packets[1] = ((packets[1] << 1) + readbit[1]);

                gpioWrite(CLOCK_PIN_1, PIN_LOW);
                gpioWrite(CLOCK_PIN_2, PIN_LOW);
                gpioDelay(TICK);
                a += 1;
        };
	data0 = ((data0 + (reverse)) % ( 1 << READING_BIT_LENGTH)) & mask;
        data1 = ((data1 - (reverse)) % ( 1 << READING_BIT_LENGTH)) & mask;
        //print_bits(sizeof(r1), &r1);
        //uint64_t rx = r1 << READING_1_LOW_BIT;
        //print_bits(sizeof(rx), &rx);
        //printf ( "r0r1 %d 5d \n\n", r0,r1);
        return (data1 << READING_LOW_1_BIT) | (data0 << READING_LOW_0_BIT);
}

int bit_slicer (uint32_t from, int lowBit, int count) {
        int range = 1 << count;
        uint32_t mask = range - 1;
        return (from >> lowBit) & mask;
}

int* handle_rollovers( int readings[2] ) {
        static int prevReadings[2];
        static int prevRollovers[2];
        static int values[2];
        int range = 1 << READING_BIT_LENGTH;
	int bigJump = range / 2;
        int i, change;
        for ( i = 0; i < 2; i++) {
                //printf ( "reading %d %d \n", idx, readings[i]);
                //print_bits(sizeof(readings), &readings[i]);
                change = readings[i] - prevReadings[i];
                prevReadings[i] = readings[i];
                prevRollovers[i] += (change > bigJump) ? -1 : (change < -bigJump);
                values[i] = readings[i] + range * prevRollovers[i];
        }
        //printf ( " %d\n" , prevRollovers[i]);
        return values;
}

main() {

	char filename[] = "fifo.tmp";
        struct timespec ts;
        struct timespec ts2;
        ts.tv_sec = 1;
        ts.tv_nsec = 0;

	int s_fifo = mkfifo(filename, S_IRWXU);
/*        if (s_fifo != 0)
        {
                printf("mkfifo() error: %d\n", s_fifo);
                return -1;
        }
*/
        FILE * wfd = fopen(filename, "w");
        if (wfd < 0)
        {
                printf("open() error: %d\n", wfd);
                return -1;
        }



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
		struct timeval tv;
		time_t curtime;
		gettimeofday(&tv, NULL);
		curtime = tv.tv_sec;
		int data = read_raw();
                int readings[2];
                readings[0] = bit_slicer ( data, READING_LOW_0_BIT, READING_BIT_LENGTH );
                readings[1] = bit_slicer ( data, READING_LOW_1_BIT, READING_BIT_LENGTH );
                int* values = handle_rollovers( readings );
		int s_write = fprintf(wfd, "%d,%d,%d\n", values[0], values[1], tv.tv_usec);
               	if (s_write < 0)
		{
			printf("fprintf() error: %d\n", s_write);
			break;
		}
		fflush(wfd);
                usleep(10000);
                if (values[0]*reverse > 20000) reverse *= -1;
        }
	fclose(wfd);
	unlink(filename);
}
