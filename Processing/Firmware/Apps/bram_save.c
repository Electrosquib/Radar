#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

#define BRAM_BASE 0x40000000
#define BRAM_MAP_SIZE 4096
#define NUM_PROFILES 100
#define PROFILE_SIZE 16

int main(void)
{
    printf("Writing BRAM\n");
    uint8_t profiles[NUM_PROFILES][PROFILE_SIZE] = {0x03};

    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    volatile uint8_t *bram = mmap(NULL, BRAM_MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, BRAM_BASE);

    for (int p = 0; p < NUM_PROFILES; p++)
        for (int i = 0; i < PROFILE_SIZE; i++)
            bram[p * PROFILE_SIZE + i] = profiles[p][i];

    printf("BRAM contents:\n");

    for (int p = 0; p < NUM_PROFILES; p++) {
        printf("Profile %d: ", p);

        for (int i = 0; i < PROFILE_SIZE; i++)
            printf("%02X ", bram[p * PROFILE_SIZE + i]);

        printf("\n");
    }

    munmap((void *)bram, BRAM_MAP_SIZE);
    close(fd);

    return 0;
}