#include <lab>
main()
{
    var value = identity(0);
    value = 0x100000001;
    check(value, 0x100000001);
    return 0;
}
