/* DMA Proxy Test Application
 *
 * This application is intended to be used with the DMA Proxy device driver. It provides
 * an example application showing how to use the device driver to do user space DMA
 * operations.
 *
 * The driver allocates coherent memory which is non-cached in a s/w coherent system.
 * Transmit and receive buffers in that memory are mapped to user space such that the
 * application can send and receive data using DMA channels (transmit and receive).
 *
 * It has been tested with an AXI DMA system with transmit looped back to receive.
 * Since the AXI DMA transmit is a stream without any buffering it is throttled until
 * the receive channel is running.  
 * 
 * More complete documentation is contained in the device driver (dma-proxy.c).
 */

#include "dma-proxy.h"
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

static struct dma_proxy_channel_interface* tx_proxy_interface_p;
static int tx_proxy_fd;
static int test_size, test_count;

/* The following function is the transmit thread to allow the transmit and the
 * receive channels to be operating simultaneously. The ioctl calls are blocking
 * such that a thread is needed.
 */

int test(void);

void* tx_thread(void* dma_count_input)
{
    int dma_count = (int) dma_count_input;
    int dummy, i, counter;

    /* Set up the length for the DMA transfer and initialize the transmit
 	 * buffer to a known pattern.
 	 */
    tx_proxy_interface_p->length = test_size;

    for (counter = 0; counter < dma_count; counter++) {
        for (i = 0; i < test_size; i++)
            tx_proxy_interface_p->buffer[i] = counter + i;

        /* Perform the DMA transfer and the check the status after it completes
	 	 * as the call blocks til the transfer is done.
 		 */
        ioctl(tx_proxy_fd, 0, &dummy);

        if (tx_proxy_interface_p->status != PROXY_NO_ERROR)
            printf("Proxy tx transfer error\n");
    }
    return NULL;
}

int main(int argc, char* argv[])
{

    if (argc != 3) {
        printf("Usage: dma-proxy-test <# of DMA transfers to perform> <# of bytes in each transfer (< 3MB)>\n");
        exit(EXIT_FAILURE);
    }

    /* Get the size of the test to run, making sure it's not bigger than the statically configured memory size)
	 */
    test_count = atoi(argv[1]);

    test_size = atoi(argv[2]);
    if (test_size > TEST_SIZE)
        test_size = TEST_SIZE;

    return test();
}

int test(void){
    struct dma_proxy_channel_interface* rx_proxy_interface_p;
    int rx_proxy_fd, i;
    int dummy;
    int counter;
    pthread_t tid;
    int rc = 0;

    printf("DMA proxy test\n");

    /* Open the DMA proxy device for the transmit and receive channels
 	 */
    tx_proxy_fd = open("/dev/dma_proxy_tx", O_RDWR);

    if (tx_proxy_fd < 1) {
        printf("Unable to open DMA proxy device file");
        exit(EXIT_FAILURE);
    }

    rx_proxy_fd = open("/dev/dma_proxy_rx", O_RDWR);
    if (tx_proxy_fd < 1) {
        printf("Unable to open DMA proxy device file");
        exit(EXIT_FAILURE);
    }

    /* Map the transmit and receive channels memory into user space so it's accessible
 	 */
    tx_proxy_interface_p = (struct dma_proxy_channel_interface*)mmap(NULL, sizeof(struct dma_proxy_channel_interface),
        PROT_READ | PROT_WRITE, MAP_SHARED, tx_proxy_fd, 0);

    rx_proxy_interface_p = (struct dma_proxy_channel_interface*)mmap(NULL, sizeof(struct dma_proxy_channel_interface),
        PROT_READ | PROT_WRITE, MAP_SHARED, rx_proxy_fd, 0);
    if ((rx_proxy_interface_p == MAP_FAILED) || (tx_proxy_interface_p == MAP_FAILED)) {
        printf("Failed to mmap\n");
        exit(EXIT_FAILURE);
    }

    /* Set up the length for the DMA transfer and initialize the transmit buffer to a known pattern. Since
	 * transmit channel is using cyclic mode the same data will be received every time a transfer is done.
 	 */
    tx_proxy_interface_p->length = test_size;

    char input_message[] = "HELLO SUKHAMN!!!!";
    int message_size = sizeof(input_message);

    for (i = 0; i < test_size && i < message_size; i++)
        tx_proxy_interface_p->buffer[i] = input_message[i];

    // for (i = 0; i < test_size; i++)
    //     tx_proxy_interface_p->buffer[i] = i;

    /* Create the thread for the transmit processing passing the number of transactions to it
	 */
    pthread_create(&tid, NULL, tx_thread, (void*)test_count);

    for (counter = 0; counter < test_count; counter++) {

        /* Initialize the receive buffer so that it can be verified after the transfer is done
		 * and setup the size of the transfer for the receive channel
		 */
        for (i = 0; i < test_size; i++)
            rx_proxy_interface_p->buffer[i] = 0;

        rx_proxy_interface_p->length = test_size;

        /* Perform a receive DMA transfer and after it finishes check the status
		 */
        ioctl(rx_proxy_fd, 0, &dummy);

        if (rx_proxy_interface_p->status != PROXY_NO_ERROR)
            printf("Proxy rx transfer error\n");

        /* Verify the data recieved matchs what was sent (tx is looped back to tx)
		 */
        for (i = 0; i < test_size; i++)
            if (rx_proxy_interface_p->buffer[i] != (unsigned char)(counter + i))
                printf("buffer not equal, index = %d, data = %d expected data = %d\n", i,
                    rx_proxy_interface_p->buffer[i], (unsigned char)(counter + i));
        printf("%s", rx_proxy_interface_p->buffer);
    }
    pthread_join(tid, NULL);
    if (!rc){
        printf("Child thread result: %d", rc);
    }

    /* Unmap the proxy channel interface memory and close the device files before leaving
	 */
    munmap(tx_proxy_interface_p, sizeof(struct dma_proxy_channel_interface));
    munmap(rx_proxy_interface_p, sizeof(struct dma_proxy_channel_interface));

    close(tx_proxy_fd);
    close(rx_proxy_fd);

    printf("DMA proxy test complete\n");

    return 0;
}

void wrapTest(void){
    test_size = 16;
    test_count = 2;
    test();
}
