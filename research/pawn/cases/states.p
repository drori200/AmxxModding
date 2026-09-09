#include <lab>
var entered;
entry() <machine:idle> { entered += 1; }
entry() <machine:active> { entered += 10; }
value() <machine:idle> { return 1; }
value() <machine:active> { return 2; }
value() <> { return -1; }
main()
{
    state machine:idle;
    check(value(), 1); check(entered, 1);
    state machine:active;
    check(value(), 2); check(entered, 11);
    state (identity(0)) machine:idle;
    check(value(), 2);
    state machine:idle;
    check(entered, 12);
    return 0;
}
