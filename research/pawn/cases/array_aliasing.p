#include <lab>
mutate(first[], second[]) { first[1] = 9; return second[1]; }
main()
{
    var values[] = [1, 2, 3];
    var copy[3];
    copy = values;
    check(mutate(values, values), 9);
    check(values[1], 9);
    check(copy[1], 2);
    var matrix[2][3] = [[1, 2, 3], [4, 5, 6]];
    check(sizeof matrix, 2); check(sizeof matrix[], 3);
    check(mutate(matrix[0], matrix[1]), 5);
    check(matrix[0][1], 9);
    return 0;
}
