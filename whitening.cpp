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

uint8_t whiten(uint8_t iv, uint8_t *p_in, uint8_t *p_out, size_t n)
{
    uint8_t state = iv;

    for (int j = 0; j < n; j++)
    {
        // dieses Byte bekomme ich rein
        uint8_t dataB = p_in[j];
        uint8_t resultB = 0;
        for (int i = 0; i <= 7; i++)
        {

            // ich shifte state 6 bit nach rechts, dann habe ich nur noch 6tes Bit übrig, dass xor ich
            // mit dataB, durch << i schreibe ich Ergebnis an das i-te bit von resultB
            resultB |= ((dataB ^ (state >> 6)) & 1) << i;
            // ich shifte dataB eins nach rechts
            dataB >>= 1;
            // ich kille das oberste Bit mit Bitmaske, shifte state nach rechts um 6tes Bit zu bekommen
            // und wende or an, um bit an erste Stelle zu schreiben
            state = (state >> 6) | (state << 1) & 0x7f;
            // ehemaliges 6tes Bit ist jetzt an 1ter Stelle, ich shifte es an 4te Stelle und xor es mit
            // state
            state ^= ((state & 0x1) << 4);
        }
        p_out[j] = resultB;
    }

    return state;
}

int main()
{

    uint8_t in[] = {0x20, 0xce, 0x5b, 0x0f, 0xdf, 0xc4, 0xe7, 0xa3, 0x2b, 0x46,
                    0xff, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xd6, 0xda};
    int n = sizeof(in);
    printf("%d \n", n);
    uint8_t out[n];
    uint8_t state = whiten(0x3, &in[0], &out[0], n);
    printf("LFSR state: ");
    print_lsb(state);
    printf("\n");
    printf("Whitened data:\n");
    for (int i = 0; i < n; i++)
    {
        printf("0x");
        printf("%02X", out[i]);
        printf(", ");
        //print_lsb(out[i]);
    }
    printf("\n");

    return 0;
}