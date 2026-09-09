#include <lab>
var called;
touch() { called++; return 1; }
main()
{
    var no = identity(0), yes = identity(1), result;
    result = no && touch(); check(result, 0); check(called, 0);
    result = yes || touch(); check(result, 1); check(called, 0);
    result = yes ? touch() : 42; check(result, 1); check(called, 1);
    result = (called = 7, called + 2); check(result, 9);
    check(0 <= identity(3) < 5, true);
    check(0 <= identity(-1) < 5, false);
    // No dependent side effects in function arguments: their order is undefined.
    return 0;
}
