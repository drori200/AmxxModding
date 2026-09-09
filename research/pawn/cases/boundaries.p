#include <lab>
main()
{
    var maximum = identity(cellmax), minimum = identity(cellmin);
    check(maximum > 0, true); check(minimum < 0, true);
    check(maximum + minimum, -1);
    check(identity(-1) >>> (cellbits - 1), 1);
    check(identity(-8) >> 2, -2);
    check(identity(1) << 3, 8);
    check(identity(0x55) & 0x0F, 5);
    check(identity(0x50) | 0x05, 0x55);
    check(identity(0x55) ^ 0x0F, 0x5A);
    // Overflow and min/-1 are separate hazardous/implementation probes.
    return 0;
}
