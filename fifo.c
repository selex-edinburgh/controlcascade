#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <time.h>

int main (void)
{
	//Create FIFO
	char filename[] = "fifoY.tmp";
	struct timespec ts;
        struct timespec ts2;
	ts.tv_sec = 1;
	ts.tv_nsec = 0;
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

	for (int many = 0; many<1000000; many+=10000)
	{
           int n;
	   for ( n = 0; n <10000; n++) {
		int s_write = fprintf(wfd, "%d\n", many+n);
		if (s_write < 0)
		{
			printf("fprintf() error: %d\n", s_write);
			break;
		}
           }
   	   printf("%d\n", many);
           fflush(wfd);

   	   nanosleep(&ts,&ts2);
	   //sleep(1);
	}
	// Close and delete FIFO
	fclose(wfd);
	unlink(filename);
}
