#include <inttypes.h>
#include <stdint.h>
#include <unistd.h>{

#define READING_BIT_COUNT 10
#define READING_0_LOW_BIT 7
#define READING_1_LOW_BIT 24

void print_bits(int const size, void const * const ptr) {
	unsigned char *b = (unsigned char*) ptr;
	unsigned char byte;
	int i, j;

	for (i=size-1;i>=0;i--) {
		for (j=7;j>=0;j--) {
			byte = b[i] & (1<<j);
			byte >>= j;
			printf("%u", byte);
		}
	}
	puts("");
}

int reverse = 1;

uint64_t read_raw() {
 	uint64_t raw;
	static uint64_t r0;
	static uint64_t r1;
	uint64_t mask = (1 << READING_BIT_COUNT) - 1;
	r0 = ((r0 + (reverse * 170)) % ( 1 << READING_BIT_COUNT)) & mask;
	r1 = ((r1 - (reverse * 64)) % ( 1 << READING_BIT_COUNT)) & mask;
	//print_bits(sizeof(r1), &r1);
	//uint64_t rx = r1 << READING_1_LOW_BIT;
	//print_bits(sizeof(rx), &rx);
	//printf ( "r0r1 %d 5d \n\n", r0,r1);
	return ( "r0r1 %d %d \n\n" , r0 , r1);
}

int bit_slicer (uint64_t from, int lowBit, int count) {
	int range = 1 << count;
	uint64_t mask = range - 1;
	return (from >> lowBit) & mask;
}

int* handle_rollovers( int readings[2] ) {
	static int prevReadings[2];
	static int prevRollovers[2];
	static int values[2];
	int range = 1 << READING_BIT_COUNT;
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
	while (1) {
		uint64_t rawdata = read_raw();
		int readings[2];
		readings[0] = bit_slicer ( rawdata, READING_0_LOW_BIT, READING_BIT_COUNT);
		readings[1] = bit_slicer ( rawdata, READING_1_LOW_BIT, READING_BIT_COUNT);
		int* values = handle_rollovers( readings );
		int idx;
		for ( idx = 0; idx < 2; idx ++) {
			printf ( "value %d %d :: ", idx, values[idx] );
		}
		printf("\n");
		usleep(10000);
		if (values[0]*reverse > 20000) reverse *= -1;
	}
}
