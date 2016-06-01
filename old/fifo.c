#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>

int main (void)
{

	//Array to send
	int arr[] = {2,4,5,6};
	int len = 4;

	//Create FIFO
	char filename[] = "fifo.tmp";

	int s_fifo = mkfifo(filename, S_IRWXU);
	if (s_fifo != 0)
	{
		printf("mkfifo() error: %d\n", s_fifo);
		return -1;
	}

	FILE * wfd = fopen(filename, "w");
	if (wfd < 0)
	{
		printf("open() error: %d\n", wfd);
		return -1;
	}

	// Write to FIFO
	for (int i=0; i<len; i++)
	{
		int s_write = fprintf(wfd, "%d ", arr[i]);

		if (s_write < 0)
		{
			printf("fprintf() error: %d\n", s_write);
			break;
		}
	}

	// Close and delete FIFO
	fclose(wfd);
	unlink(filename);
}
