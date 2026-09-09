#include <lab>
// Expected: the newly zero-initialized array does not overwrite its neighbour.
main()
{
    var sentinel = identity(1234);
    var values[2];
    check(values[0], 0);
    check(values[1], 0);
    check(sentinel, 1234);
    return 0;
}
