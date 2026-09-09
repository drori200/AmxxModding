#include <lab>
// Corrected canonical cell-array versions of the guide's stale brace examples.
main()
{
    var repeated[4] = [7, ...];
    var ascending[5] = [1, 2, ...];
    var descending[5] = [5, 3, ...];
    var zero_tail[4] = [1, 2];
    check(repeated[3], 7);
    check(ascending[4], 5);
    check(descending[4], -3);
    check(zero_tail[2], 0); check(zero_tail[3], 0);
    return 0;
}
