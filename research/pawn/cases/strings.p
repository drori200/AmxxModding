#include <lab>
// Canonical 4.1: double quotes packed; doubled single quotes unpacked.
main()
{
    var packed{12} = "abc";
    var unpacked[4] = ''abc'';
    check(packed{0}, 'a'); check(packed{2}, 'c'); check(packed{3}, 0);
    check(unpacked[0], 'a'); check(unpacked[2], 'c'); check(unpacked[3], 0);
    packed{0} = 'A'; unpacked[0] = 'A';
    check(packed{0}, unpacked[0]);
    // Capacity is an allocation property, not the current string length.
    check(sizeof unpacked, 4);
    check(sizeof packed, (12 + cellbits / charbits - 1) / (cellbits / charbits));
    return 0;
}
