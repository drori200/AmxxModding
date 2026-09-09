#include <lab>
main()
{
    var ragged[][] = [[1, 2], [3, 4, 5]];
    var cube[2][2][2] = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]];
    check(sizeof ragged, 2);
    check(ragged[0][1], 2); check(ragged[1][2], 5);
    check(cube[1][1][1], 8);
    check(sizeof cube, 2); check(sizeof cube[], 2); check(sizeof cube[][], 2);
    return 0;
}
