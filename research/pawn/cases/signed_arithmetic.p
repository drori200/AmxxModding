#include <lab>
// Language Guide (August 2025), pp. 89-90: floored division;
// the nonzero remainder has the divisor's sign. Check folding AND execution.
main()
{
    var dividends[] = [7, -7, 7, -7, 6, -6, 0];
    var divisors[] = [3, 3, -3, -3, -3, 3, -3];
    var quotients[] = [2, -3, -3, 2, -2, -2, 0];
    var remainders[] = [1, 2, -2, -1, 0, 0, 0];
    for (var i = 0; i < sizeof dividends; i++) {
        var a = identity(dividends[i]), b = identity(divisors[i]);
        check(a / b, quotients[i]);
        check(a % b, remainders[i]);
        check((a / b) * b + a % b, a);
    }
    check(7 / 3, 2); check(-7 / 3, -3);
    check(7 / -3, -3); check(-7 / -3, 2);
    check(7 % 3, 1); check(-7 % 3, 2);
    check(7 % -3, -2); check(-7 % -3, -1);
    return 0;
}
