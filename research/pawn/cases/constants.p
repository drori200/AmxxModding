#include <lab>
const Mode: { Idle = 2, Running, Stopped = 7, Finished }
main()
{
    check(_:Idle, 2); check(_:Running, 3); check(_:Stopped, 7); check(_:Finished, 8);
    check(defined Running, true);
    check(defined absent_constant, false);
    check(cellbits, 32); check(charbits, 8);
    return 0;
}
