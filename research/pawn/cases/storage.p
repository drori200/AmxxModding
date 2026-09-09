#include <lab>
var global;
counter() { static calls; var automatic; automatic++; return ++calls * 10 + automatic; }
main()
{
    check(global, 0);
    check(counter(), 11); check(counter(), 21);
    var value = 4;
    { var inner = 7; value += inner; }
    check(value, 11);
    return 0;
}
