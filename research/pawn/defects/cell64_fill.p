#include <lab>
main()
{
    var values[2] = [0x100000001, 0x100000001];
    check(values[0], 0x100000001);
    check(values[1], 0x100000001);
    return 0;
}
