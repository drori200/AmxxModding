#include <lab>
main()
{
    var total;
    for (var i = 0; i < 6; i++) {
        if (i == 1) continue;
        if (i == 5) break;
        total += i;
    }
    check(total, 9);
    var iterations;
    do { iterations++; } while (identity(0))
    check(iterations, 1);
    while (iterations < 3) iterations++;
    check(iterations, 3);
    switch (identity(2)) {
        case 1: total = 100;
        case 2, 3: total = 200;
        default: total = 300;
    }
    check(total, 200);
    return 0;
}
