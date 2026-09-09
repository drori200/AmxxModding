#include <lab>
// The comparison must not change the already-evaluated expected argument.
main()
{
    check(0 <= identity(3) < 5, true);
    return 0;
}
