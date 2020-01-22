#include "libuio.h"
#include "libpwm.h"
#include <dirent.h>
#include <sys/types.h>
#include <errno.h>
#include <getopt.h>
#include <signal.h>
#include <stdlib.h>

void getDeviceInfo(uint8_t * uioNum, uint8_t * mapNum);
void exitHandler();

#define ZERO    0x0000
#define TWENTYFIVE 0x0800
#define FIFTY   0x8000

PWM * pwm;

void run_demo() {
    uint16_t r1 = 0, r2 = 0, 
            b1 = 0, b2 = 0, 
            g1 = 0, g2 = 0;
    
    // uint8_t b1flag = 0, b2flag = 0;

    uint8_t uioNum, mapNum;
    getDeviceInfo(&uioNum, &mapNum);

    printf("Using PWM device at UIO:%d, MAP:%d\n", uioNum, mapNum);
    printf("Beginning PWM demo....\n");
    printf("Press ctrl+c to exit\n");

    struct sigaction sigIntHandler;
    
    //sigIntHandler.sa_handler = exitHandler;
    //sigemptyset(&sigIntHandler.sa_mask);
    //sigIntHandler.sa_flags = 0;
    
    //sigaction(SIGINT, &sigIntHandler, NULL);


    pwm = PWM_init(uioNum, mapNum);
    PWM_Enable(pwm);

    // PL Clock is 100 MHz, each successive value in the frequency register is 10ns
    // Set PWM frequency to 10 * 100000 ==  1000000 ns     ==     1 KHz
    setPwmPeriod(pwm, 59999);
    uint16_t i = 0;
    uint32_t j = 0;
    while(j < 5000) {

        // setPwmDuty(pwm, 1, b1);
        setPwmDuty(pwm, 2, g1);
        setPwmDuty(pwm, 3, r1);
        setPwmDuty(pwm, 4, b2);
        setPwmDuty(pwm, 5, g2);
        setPwmDuty(pwm, 6, r2);
        
        if(i == 0) {
            b1 = 19998;
            r1 = 0;
            g1 = 0;
            g2 = 19998;
            r2 = 0;
            b2 = 0;
        } else if(i < 20000) {
            setPwmDuty(pwm, 1, b1--);
            setPwmDuty(pwm, 3, r1++);
            
            setPwmDuty(pwm, 5, (g2 == 0) ? 0 : g2--);
            setPwmDuty(pwm, 6, r2++);
            
        } else if (i < 40000) {
            setPwmDuty(pwm, 3, (r1 == 0) ? 0 : r1--);
            setPwmDuty(pwm, 2, g1++);

            setPwmDuty(pwm, 4, b2++);
            setPwmDuty(pwm, 6, (r2 == 0) ? 0 : r2--);
        } else if (i < 60000) {
            setPwmDuty(pwm, 2, (g1 == 0) ? 0 : g1--);
            setPwmDuty(pwm, 1, b1++);

            setPwmDuty(pwm, 4, (b2 == 0) ? 0 : b2--);
            setPwmDuty(pwm, 5, g2++);

        }
 
        (i == 59999) ? i = 0 : i++;
        usleep(150);
	j++;
    }
    
    PWM_Disable(pwm);
    PWM_Close(pwm);
    printf("\nYa done now\n");
    usleep(1000);
    //exit(EXIT_SUCCESS);
}

