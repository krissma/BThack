#include <cstdint>
#include <stdio.h>
using namespace std;

void print_lsb(uint8_t b)
{
    printf("%02X \n", b);
    for (int i = 0; i < 8; i++)
    {
        putchar('0' + (b & 1));
        b >>= 1;
    }
}

void print_lsb_16(uint16_t b)
{
    printf("%02X \n", b);
    for (int i = 0; i < 16; i++)
    {
        putchar('0' + (b & 1));
        b >>= 1;
    }
}

uint16_t readBits(uint8_t byte_ctr, uint8_t cycle_ctr, uint8_t *p_in)
{
    // Es gibt beim shiften ein pattern, dass sich alle 5 Iterierungen wiederholt, cycle_ctr zählt
    // Iterierungen, jeder shift ist 2*cycle_ctr
    uint16_t result = (uint16_t)p_in[byte_ctr];
    //printf("%d \n", result);
    uint16_t intermediate = (uint16_t)p_in[byte_ctr + 1];
    //printf("%d \n", intermediate);
    result |= (intermediate << 8);
    //printf("%d \n", result);
    result = ((result >> (2 * cycle_ctr)) & ((1 << 10) - 1));
    //print_lsb_16(result);
    return result;
}

void writeBits(uint8_t byte_ctr, uint8_t cycle_ctr, uint8_t *p_out, uint16_t data, uint16_t parity)
{
    // MSB             LSB
    // 0PPP PPDD DDDD DDDD
    uint16_t encoded = data | (parity << 10);
    // Fülle letztes angefangenes Byte auf
    if (cycle_ctr > 0)
        p_out[byte_ctr++] |= (data & ((1 << cycle_ctr) - 1)) << (8 - cycle_ctr);
    // Jetzt kommt ein volles Byte
    p_out[byte_ctr++] = encoded >> cycle_ctr;
    // Jetzt fängt noch ein neues Byte mit 7 - i Bits an
    if (cycle_ctr < 7)
        p_out[byte_ctr++] = encoded >> (8 + cycle_ctr);
}

uint8_t encode(uint8_t *p_in, uint8_t *p_out, size_t n)
{
    uint16_t state;
    uint8_t read_cycle_ctr = 0;
    uint8_t write_cycle_ctr = 0;
    uint8_t read_byte_ctr = 0;
    uint8_t write_byte_ctr = 0;
    uint16_t dataByte;

    while (read_byte_ctr < n)
    {
        // Am Anfang wird Register auf 0 gesetzt
        state = 0x0;
        // Hier brauche ich 10 Bit als Input
        dataByte = readBits(read_byte_ctr, read_cycle_ctr, p_in);
        read_byte_ctr++;
        read_cycle_ctr++;
        if (read_cycle_ctr == 4)
        {
            read_cycle_ctr = 0;
            read_byte_ctr++;
        }

        for (int i = 0; i < 10; i++)
        {
            uint8_t dataBit = ((dataByte >> i) ^ state) & 1;
            state = (dataBit << 4) | (state >> 1) ^ (dataBit << 2) ^ dataBit;
        }
        writeBits(write_byte_ctr, write_cycle_ctr, p_out, dataByte, state);
        write_byte_ctr++;
        if (write_cycle_ctr > 0)
            write_byte_ctr++;
        write_cycle_ctr = (write_cycle_ctr + 1) % 8;
    }
    return state;
}

int main()
{
    // nur gepaddete werte übergeben mit 2*0 hintendran (vielfaches von 10 bits)
    uint8_t in[] = {0x40, 0x25, 0x39, 0x2D, 0x4F, 0xE8, 0x08, 0x53, 0xEC, 0xCB, 0x2D,
                    0xA8, 0x5E, 0x3D, 0xA7, 0x66, 0xB0, 0x75, 0x31, 0x11, 0x9E, 0x4C};
    int n = sizeof(in);
    int n_blocks = ((n * 8) + 9) / 10;
    int n_out = (n_blocks * 15 + 7) / 8;
    readBits(0, 0, in);
    //printf("%d \n", n);
    uint8_t out[n_out];
    uint8_t state = encode(in, out, n);
    printf("LFSR state: ");
    print_lsb(state);
    printf("\n");
    printf("Encoded data:\n");
    /* for (int i = n_out - 1; i >= 0; i--)
    {
        // dieser Input muss in testFec in CRC.hs
        printf("%02x", out[i]);
        //printf("0x");
        //printf("%02X", i);
        //printf(" %d ", i);
        //print_lsb(out[i]);
    }
    printf("\n");
    */

    for (int i = 0; i < n_out; i++)
    {
        printf("0x%02X, ", out[i]);
    }
    printf("\n");

    return 0;
}